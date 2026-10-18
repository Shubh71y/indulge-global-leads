"""
INDULGE GLOBAL — GOOGLE SHEETS REAL-TIME SYNC ENGINE
=====================================================
Synchronizes leads directly from `leads_store.jsonl` / `HNI.xlsx`
into Google Sheets via Google Apps Script Webhook.

Key Features:
- Real-time background sync on every lead appended.
- Batch syncing to avoid Google Apps Script execution timeout.
- Non-destructive updates: preserves SDR Call Dispositions & Notes.
- Auto-loads `GOOGLE_SHEET_WEBHOOK_URL` from `.env` or system environment.
"""

import os
import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts import env_loader


def get_configured_webhook_url() -> Optional[str]:
    """Retrieve Google Sheet Webhook URL from environment or .env file."""
    url = os.environ.get("GOOGLE_SHEET_WEBHOOK_URL", "").strip()
    if url:
        return url

    env_path = BASE_DIR / ".env"
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("GOOGLE_SHEET_WEBHOOK_URL="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return None


def save_configured_webhook_url(url: str) -> bool:
    """Save or update GOOGLE_SHEET_WEBHOOK_URL in .env file and environment."""
    url = (url or "").strip()
    os.environ["GOOGLE_SHEET_WEBHOOK_URL"] = url

    env_path = BASE_DIR / ".env"
    lines = []
    found = False

    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("GOOGLE_SHEET_WEBHOOK_URL="):
                    lines.append(f"GOOGLE_SHEET_WEBHOOK_URL={url}\n")
                    found = True
                else:
                    lines.append(line)

    if not found:
        lines.append(f"GOOGLE_SHEET_WEBHOOK_URL={url}\n")

    try:
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save Google Sheet Webhook URL: {e}")
        return False


def test_google_sheet_webhook(webhook_url: Optional[str] = None) -> Dict[str, Any]:
    """Perform a health check against the Google Apps Script Web App."""
    target_url = webhook_url or get_configured_webhook_url()
    if not target_url:
        return {"success": False, "error": "No Google Sheet Webhook URL configured."}

    try:
        resp = requests.get(target_url, timeout=12, allow_redirects=True)
        if resp.status_code == 200:
            try:
                data = resp.json()
                return {"success": True, "data": data, "url": target_url}
            except Exception:
                return {"success": True, "text": resp.text[:200], "url": target_url}
        else:
            return {
                "success": False,
                "status_code": resp.status_code,
                "error": f"HTTP {resp.status_code}: {resp.text[:200]}",
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def sync_leads_to_google_sheet(
    leads: Optional[List[Dict[str, Any]]] = None,
    webhook_url: Optional[str] = None,
    batch_size: int = 50,
) -> Dict[str, Any]:
    """
    Sync all leads (or a provided batch) to Google Sheets via Webhook.
    Splits into sub-batches of `batch_size` (default 50) to respect Google Apps Script timeouts.
    """
    target_url = webhook_url or get_configured_webhook_url()
    if not target_url:
        return {"success": False, "error": "No Google Sheet Webhook URL configured."}

    if leads is None:
        from scripts.lead_store import get_all_leads
        leads = get_all_leads()

    if not leads:
        return {"success": True, "synced": 0, "message": "No leads to sync."}

    total_added = 0
    total_updated = 0
    errors = []

    print(f"[*] Syncing {len(leads)} leads to Google Sheet in batches of {batch_size}...")

    for i in range(0, len(leads), batch_size):
        chunk = leads[i : i + batch_size]
        payload = {
            "action": "sync_leads",
            "source": "Indulge Global Python Server",
            "batch_index": i // batch_size + 1,
            "leads": chunk,
        }

        try:
            resp = requests.post(
                target_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=25,
                allow_redirects=True,
            )
            if resp.status_code in (200, 302):
                try:
                    res_json = resp.json()
                    total_added += res_json.get("added", 0)
                    total_updated += res_json.get("updated", 0)
                except Exception:
                    total_updated += len(chunk)
            else:
                errors.append(f"Batch {i//batch_size+1} failed with HTTP {resp.status_code}")
        except Exception as e:
            errors.append(f"Batch {i//batch_size+1} error: {str(e)}")

        time.sleep(0.3)

    return {
        "success": len(errors) == 0,
        "total_leads_sent": len(leads),
        "added": total_added,
        "updated": total_updated,
        "errors": errors,
    }


def push_single_lead_async(lead_dict: Dict[str, Any], webhook_url: Optional[str] = None):
    """Fire-and-forget asynchronous push for a single newly discovered lead."""
    target_url = webhook_url or get_configured_webhook_url()
    if not target_url:
        return

    def _worker():
        try:
            requests.post(
                target_url,
                json={"action": "add_lead", "lead": lead_dict},
                headers={"Content-Type": "application/json"},
                timeout=10,
                allow_redirects=True,
            )
        except Exception as e:
            pass

    t = threading.Thread(target=_worker, daemon=True)
    t.start()


def push_batch_async(leads_batch: List[Dict[str, Any]], webhook_url: Optional[str] = None):
    """Fire-and-forget asynchronous batch push for newly discovered leads."""
    target_url = webhook_url or get_configured_webhook_url()
    if not target_url or not leads_batch:
        return

    def _worker():
        try:
            for i in range(0, len(leads_batch), 50):
                chunk = leads_batch[i : i + 50]
                requests.post(
                    target_url,
                    json={"action": "sync_leads", "leads": chunk},
                    headers={"Content-Type": "application/json"},
                    timeout=20,
                    allow_redirects=True,
                )
                time.sleep(0.2)
        except Exception:
            pass

    t = threading.Thread(target=_worker, daemon=True)
    t.start()



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Indulge Global Google Sheets Sync Engine")
    parser.add_argument("--url", help="Google Apps Script Web App URL")
    parser.add_argument("--test", action="store_true", help="Test connection to webhook")
    args = parser.parse_args()

    url = args.url or get_configured_webhook_url()
    if args.url:
        save_configured_webhook_url(args.url)
        print(f"[+] Saved Google Sheet Webhook URL: {args.url}")

    if not url:
        print("[!] No Google Sheet Webhook URL configured. Pass --url <WEBHOOK_URL>")
        sys.exit(1)

    if args.test:
        res = test_google_sheet_webhook(url)
        print("Health Check Result:", json.dumps(res, indent=2))
    else:
        res = sync_leads_to_google_sheet(webhook_url=url)
        print("Sync Result:", json.dumps(res, indent=2))
