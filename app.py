r"""
Indulge Global - HNI Lead Intelligence Dashboard
=================================================
Flask backend serving the luxury lead mining dashboard.

Backend API:
  GET  /                      -> Dashboard SPA
  GET  /api/leads             -> All leads from HNI.xlsx (JSON)
  GET  /api/stats             -> Summary statistics
  POST /api/mine              -> Launch a mining run
  GET  /api/miners             -> List active miner processes
  POST /api/miners/<pid>/kill -> Kill a specific miner
  GET  /api/export/csv        -> Download leads as CSV

Data path: C:\Users\gozoi\Projects\indulge\data\HNI.xlsx
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os
import json
import signal
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, jsonify, request, Response

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SCRIPTS_DIR = BASE_DIR / "scripts"
HNI_XLSX = DATA_DIR / "HNI.xlsx"
HNI_CSV = DATA_DIR / "indulge_gcc_hni_master.csv"
PYTHON_EXE = sys.executable  # Use whichever Python launched this server

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Active miners registry  { pid: {info} }
# ---------------------------------------------------------------------------
active_miners = {}
miners_lock = threading.Lock()


import sys
sys.path.append(str(SCRIPTS_DIR))
try:
    import lead_store
except Exception:
    lead_store = None

def _read_hni_xlsx():
    """Read leads from durable store and fallback to HNI.xlsx."""
    if lead_store:
        try:
            leads = lead_store.get_all_leads()
            if leads:
                return leads
        except Exception:
            pass
    import pandas as pd
    if not HNI_XLSX.exists():
        return []
    try:
        df = pd.read_excel(str(HNI_XLSX))
        df = df.fillna("")
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"[WARNING] Could not read HNI.xlsx: {e}")
        return []


def _read_hni_csv():
    """Fallback: read CSV mirror."""
    import pandas as pd
    if not HNI_CSV.exists():
        return []
    try:
        df = pd.read_csv(str(HNI_CSV))
        df = df.fillna("")
        return df.to_dict(orient="records")
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/leads")
def api_leads():
    """Return all leads as JSON array."""
    leads = _read_hni_xlsx()
    if not leads:
        leads = _read_hni_csv()
    return jsonify({"leads": leads, "count": len(leads), "timestamp": datetime.now().isoformat()})


@app.route("/api/stats")
def api_stats():
    """Return summary statistics."""
    leads = _read_hni_xlsx()
    if not leads:
        leads = _read_hni_csv()

    total = len(leads)
    with_phone = sum(1 for l in leads if l.get("Phone Number", ""))
    vip_mobiles = sum(1 for l in leads if "Mobile" in str(l.get("Phone Type", "")))
    corporate_landlines = total - vip_mobiles
    with_email = sum(1 for l in leads if l.get("Email", "") and l.get("Email") != "N/A")
    verified_email = sum(1 for l in leads if "Deliverable" in str(l.get("Deliverability Status", "")) or "Verified" in str(l.get("Deliverability Status", "")))
    risky_email = sum(1 for l in leads if "Risky" in str(l.get("Deliverability Status", "")))

    # Country/city breakdown
    cities = {}
    for l in leads:
        city = str(l.get("City/Country", "Unknown"))
        cities[city] = cities.get(city, 0) + 1

    # Source breakdown
    sources = {}
    for l in leads:
        src = str(l.get("Source", "Unknown"))
        if "Apify" in src:
            src = "Apify Google Maps"
        elif "Tavily" in src or "LinkedIn" in src:
            src = "LinkedIn / Tavily VIP"
        elif "Registry" in src:
            src = "Verified GCC Registry"
        sources[src] = sources.get(src, 0) + 1

    # Segment breakdown (6 UHNI Data Sources)
    segments = {}
    for l in leads:
        seg = str(l.get("Segment Tag", "family_office"))
        segments[seg] = segments.get(seg, 0) + 1

    # Companies
    companies = {}
    for l in leads:
        comp = str(l.get("Company", "Unknown"))
        if comp:
            companies[comp] = companies.get(comp, 0) + 1

    with miners_lock:
        running_miners = len(active_miners)

    return jsonify({
        "total_leads": total,
        "with_phone": with_phone,
        "vip_mobiles": vip_mobiles,
        "corporate_landlines": corporate_landlines,
        "with_email": with_email,
        "verified_email": verified_email,
        "risky_email": risky_email,
        "cities": cities,
        "sources": sources,
        "segments": segments,
        "top_companies": dict(sorted(companies.items(), key=lambda x: -x[1])[:15]),
        "running_miners": running_miners,
        "last_updated": datetime.now().isoformat(),
        "xlsx_size_kb": round(HNI_XLSX.stat().st_size / 1024, 1) if HNI_XLSX.exists() else 0,
    })


@app.route("/api/verify", methods=["POST"])
def api_verify():
    """Run 3-layer phone/WhatsApp verification, Microsoft 365 Azure AD email check, or full dataset audit."""
    data = request.get_json(force=True) if request.data else {}
    raw_phone = data.get("phone", "").strip()
    raw_email = data.get("email", "").strip()
    expected_name = data.get("name", "").strip()
    region = data.get("region", "AE").strip()

    if raw_email:
        from scripts.smtp_verifier import verify_office365_email_exact
        o365_status = verify_office365_email_exact(raw_email)
        return jsonify({"email": raw_email, "azure_ad_status": o365_status})

    if raw_phone:
        from scripts.phone_verifier import classify_gcc_phone, verify_whatsapp_live, reverse_caller_id_lookup
        info = classify_gcc_phone(raw_phone, default_region=region)
        if not info.get("valid"):
            return jsonify({"valid": False, "error": info.get("reason", "Invalid phone")}), 400
        wa = verify_whatsapp_live(info["e164"]) if info.get("is_mobile") else {"checked": False, "exists": False}
        caller = reverse_caller_id_lookup(info["e164"], expected_name=expected_name) if info.get("is_mobile") else {"checked": False}
        return jsonify({"phone": info, "whatsapp": wa, "caller_id": caller})

    from scripts.mine_uhni_6_sources import run_6_source_uhni_miner
    run_6_source_uhni_miner()
    leads = _read_hni_xlsx()
    return jsonify({"message": "Dataset audited & verified with Azure AD + 3-Layer Phone Hygiene", "count": len(leads)})


@app.route("/api/mine", methods=["POST"])
def api_mine():
    """Launch a mining run with optional custom parameters."""
    data = request.get_json(force=True) if request.data else {}
    miner_type = data.get("type", "uhni_6_sources")  # uhni_6_sources | full | apify | tavily | mobile | custom
    location = data.get("location", "Dubai, UAE")
    query = data.get("query", "")
    target_count = data.get("target_count", 100)

    # Build a one-shot miner script dynamically
    script_name = None
    script_args = []

    if miner_type in ("uhni_6_sources", "full"):
        script_name = "mine_uhni_6_sources.py"
    elif miner_type in ("us_uhni", "us_uhni_family_office"):
        script_name = "us_uhni_miner.py"
    elif miner_type in ("emea_statutory", "eu_beneficial_owner"):
        script_name = "emea_uhni_classifier_and_miner.py"
    elif miner_type in ("gcc_alumni_nri", "nri_diaspora"):
        script_name = "gcc_elite_alumni_and_nri_miner.py"
    elif miner_type == "icij_offshore":
        script_name = "icij_offshore_leaks_uhni_filter.py"
    elif miner_type == "apify":
        script_name = "apify_full_hni_miner.py"
    elif miner_type == "tavily":
        script_name = "mine_middle_east_hni.py"
    elif miner_type == "mobile":
        script_name = "mine_direct_hni_mobiles.py"
    elif miner_type == "custom":
        # Generate a custom one-shot script
        script_name = _generate_custom_miner(location, query, target_count)
    else:
        return jsonify({"error": f"Unknown miner type: {miner_type}"}), 400

    script_path = SCRIPTS_DIR / script_name if miner_type != "custom" else BASE_DIR / "scripts" / script_name

    if not script_path.exists():
        return jsonify({"error": f"Script not found: {script_path}"}), 404

    # Pass user-selected location & query via environment variables so all miners can run custom queries
    child_env = os.environ.copy()
    child_env["INDULGE_TARGET_LOCATION"] = str(location or "")
    child_env["INDULGE_TARGET_QUERY"] = str(query or "")
    child_env["INDULGE_TARGET_COUNT"] = str(target_count or 100)

    # Launch as subprocess
    proc = subprocess.Popen(
        [PYTHON_EXE, "-u", str(script_path)] + script_args,
        cwd=str(BASE_DIR),
        env=child_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )

    info = {
        "pid": proc.pid,
        "type": miner_type,
        "script": script_name,
        "location": location,
        "query": query,
        "target_count": target_count,
        "started_at": datetime.now().isoformat(),
        "status": "running",
        "log_lines": [],
    }

    with miners_lock:
        active_miners[proc.pid] = info

    # Background thread to capture output
    def _capture(proc, pid):
        try:
            for line in proc.stdout:
                line = line.rstrip()
                with miners_lock:
                    if pid in active_miners:
                        active_miners[pid]["log_lines"].append(line)
                        # Keep only last 200 lines
                        if len(active_miners[pid]["log_lines"]) > 200:
                            active_miners[pid]["log_lines"] = active_miners[pid]["log_lines"][-200:]
        except Exception:
            pass
        finally:
            proc.wait()
            with miners_lock:
                if pid in active_miners:
                    active_miners[pid]["status"] = "finished"
                    active_miners[pid]["finished_at"] = datetime.now().isoformat()

    t = threading.Thread(target=_capture, args=(proc, proc.pid), daemon=True)
    t.start()

    return jsonify({"message": f"Miner '{miner_type}' launched", "pid": proc.pid, "script": script_name})


@app.route("/api/miners")
def api_miners():
    """List active/recent miner processes."""
    with miners_lock:
        miners_list = []
        for pid, info in active_miners.items():
            miners_list.append({
                "pid": pid,
                "type": info["type"],
                "script": info["script"],
                "location": info.get("location", ""),
                "query": info.get("query", ""),
                "started_at": info["started_at"],
                "status": info["status"],
                "finished_at": info.get("finished_at", ""),
                "last_log": info["log_lines"][-5:] if info["log_lines"] else [],
            })
    return jsonify({"miners": miners_list})


@app.route("/api/miners/<int:pid>/kill", methods=["POST"])
def api_kill_miner(pid):
    """Kill a running miner."""
    with miners_lock:
        info = active_miners.get(pid)
        if not info:
            return jsonify({"error": "Miner not found"}), 404

    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
        else:
            os.kill(pid, signal.SIGTERM)
        with miners_lock:
            if pid in active_miners:
                active_miners[pid]["status"] = "killed"
                active_miners[pid]["finished_at"] = datetime.now().isoformat()
        return jsonify({"message": f"Miner PID {pid} killed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/miners/<int:pid>/logs")
def api_miner_logs(pid):
    """Get full log output for a miner."""
    with miners_lock:
        info = active_miners.get(pid)
        if not info:
            return jsonify({"error": "Miner not found"}), 404
        return jsonify({"pid": pid, "log_lines": info["log_lines"]})


@app.route("/api/export/csv")
def api_export_csv():
    """Download leads as CSV."""
    import pandas as pd
    leads = _read_hni_xlsx()
    if not leads:
        leads = _read_hni_csv()
    if not leads:
        return jsonify({"error": "No leads found"}), 404
    df = pd.DataFrame(leads)
    csv_data = df.to_csv(index=False)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=HNI_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"}
    )


# ---------------------------------------------------------------------------
# Google Sheets & Google Apps Script Sync Endpoints
# ---------------------------------------------------------------------------

@app.route("/api/google-sheet/config", methods=["GET", "POST"])
def api_google_sheet_config():
    """Get or save Google Sheet Webhook URL."""
    from scripts import google_sheets_sync
    if request.method == "POST":
        data = request.get_json(force=True) if request.data else {}
        url = (data.get("webhook_url") or "").strip()
        google_sheets_sync.save_configured_webhook_url(url)
        test_res = google_sheets_sync.test_google_sheet_webhook(url) if url else {"success": False, "error": "URL cleared"}
        return jsonify({
            "configured": bool(url),
            "webhook_url": url,
            "test_result": test_res,
            "message": "Google Sheet Webhook URL updated" if url else "Webhook URL cleared"
        })

    url = google_sheets_sync.get_configured_webhook_url()
    return jsonify({
        "configured": bool(url),
        "webhook_url": url or ""
    })


@app.route("/api/google-sheet/sync", methods=["POST"])
def api_google_sheet_sync():
    """Trigger full sync of all leads to Google Sheets."""
    from scripts import google_sheets_sync
    leads = _read_hni_xlsx()
    if not leads:
        leads = _read_hni_csv()
    
    url = google_sheets_sync.get_configured_webhook_url()
    if not url:
        return jsonify({"success": False, "error": "No Google Sheet Webhook URL configured. Please configure it first."}), 400

    res = google_sheets_sync.sync_leads_to_google_sheet(leads=leads, webhook_url=url)
    return jsonify(res)


@app.route("/api/google-sheet/code", methods=["GET"])
def api_google_sheet_code():
    """Return the Google Apps Script Code.gs content."""
    script_file = SCRIPTS_DIR / "google_apps_script_code.js"
    if script_file.exists():
        content = script_file.read_text(encoding="utf-8")
        return jsonify({"code": content, "filename": "Code.gs"})
    return jsonify({"error": "Script file not found"}), 404



def _generate_custom_miner(location, query, target_count):
    """Generate a one-shot custom miner script using Tavily OSINT, 5-Gate Classifier, 120-Char Proximity Mobile, M365 Azure AD, and Apify."""
    script_name = f"custom_miner_{int(time.time())}.py"
    script_content = f'''# Auto-generated custom Global (US + EMEA) UHNI miner
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os, re, time, requests
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")

from scripts.phone_verifier import (
    classify_gcc_phone,
    clean_corporate_domain,
    extract_phone_with_proximity,
    infer_region_from_location,
    is_broker_or_retail_trap,
)
from scripts.emea_uhni_classifier_and_miner import evaluate_5_gate_hni_classification
from scripts.smtp_verifier import resolve_and_verify_corporate_email
from scripts.lead_store import append_leads_batch, get_all_leads

location = """{location}"""
query = """{query}"""
target_count = {target_count}
default_reg = infer_region_from_location(location)

print(f"[*] Launching Custom UHNI Miner for Location='{{location}}' (Region={{default_reg}}), Query='{{query}}'...")

keys_raw = os.getenv("TAVILY_API_KEYS", "") or os.getenv("TAVILY_API_KEY", "")
tavily_keys = [k.strip() for k in keys_raw.split(",") if k.strip()]

all_leads = []
if tavily_keys:
    dork_queries = [
        f'({{query}}) ("{{location}}") ("Founder" OR "Chairman" OR "Managing Partner" OR "Family Office" OR "Chief of Staff") site:linkedin.com/in/',
        f'({{query}}) ("{{location}}") ("+1" OR "+44" OR "+41" OR "+33" OR "+49" OR "+971" OR "+966" OR "wa.me")',
    ]
    for dq in dork_queries:
        try:
            resp = requests.post(
                "https://api.tavily.com/search",
                json={{"api_key": tavily_keys[0], "query": dq, "search_depth": "basic", "max_results": 8}},
                timeout=12,
            )
            if resp.status_code != 200:
                continue
            for r in resp.json().get("results", []):
                title = r.get("title", "")
                content = r.get("content", "")
                m = re.match(r"^([A-Z][a-z]+)\\s+([A-Z][a-z]+)\\s*[-–|]\\s*([^-–|]+?)(?:\\s+at\\s+|\\s*[-–|]\\s*)([^-–|]+)", title)
                if not m:
                    continue
                fn, ln, role, comp = m.group(1).strip(), m.group(2).strip(), m.group(3).strip(), m.group(4).strip()
                gate = evaluate_5_gate_hni_classification(role, comp, headcount=10, address=location, wealth_signal=query)
                if not gate["passed"]:
                    continue
                p_info = extract_phone_with_proximity(f"{{title}} {{content}}", fn, ln, url=r.get("url", ""), default_region=default_reg, max_distance=120, require_mobile=True)
                if not p_info or not p_info.get("valid"):
                    continue
                all_leads.append({{
                    "First Name": fn,
                    "Last Name": ln,
                    "Role": role[:80],
                    "Company": comp[:80],
                    "Domain": "N/A",
                    "Phone Number": p_info["formatted_intl"],
                    "Email": "N/A",
                    "City/Country": location,
                    "Full Address": location,
                    "Source": f"Custom OSINT Miner ({{query[:40]}})",
                    "Wealth Signal": f"{{gate['tier']}} ({{query[:35]}})",
                    "Pitch Angle": "Pitch: 24/7 Principal & Family Lifestyle Desk",
                }})
        except Exception as e:
            print(f"[Tavily] {{e}}")

q_low = (location + " " + query).lower()
if any(k in q_low for k in ("nri", "indian", "diaspora", "iit", "iim", "tie", "indiaspora", "asian rich", "singapore", "hong kong")):
    from scripts.gcc_elite_alumni_and_nri_miner import run_gcc_alumni_and_nri_miner
    run_gcc_alumni_and_nri_miner(target_location=location, target_query=query)

if all_leads:
    added = append_leads_batch(all_leads, allow_network=False)
    print(f"[+] Custom Miner finished! Added {{added}} new leads. Total verified leads: {{len(get_all_leads())}}")
else:
    print(f"[+] Custom Miner scan finished. Total verified leads in HNI.xlsx: {{len(get_all_leads())}}")
'''
    script_path = SCRIPTS_DIR / script_name
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    return script_name


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 60)
    print("  INDULGE GLOBAL - HNI Lead Intelligence Dashboard")
    print(f"  http://localhost:{port}")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

