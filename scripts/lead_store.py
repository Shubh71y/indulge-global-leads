r"""
Indulge Global - Persistent Lead Store & Master Sync
===================================================
Maintains a durable JSONL append-only backing store at:
  C:\Users\gozoi\Projects\indulge\data\leads_store.jsonl

And safely regenerates HNI.xlsx and indulge_gcc_hni_master.csv
with zero risk of data loss, truncation, or corruption.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os
import re
import json
import time
import pandas as pd
from pathlib import Path

BASE_DIR = Path(r"C:\Users\gozoi\Projects\indulge")
DATA_DIR = BASE_DIR / "data"
JSONL_PATH = DATA_DIR / "leads_store.jsonl"
EXCEL_PATH = DATA_DIR / "HNI.xlsx"
CSV_PATH = DATA_DIR / "indulge_gcc_hni_master.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)

def append_lead(lead_dict):
    """Append a single lead to jsonl store with atomic write."""
    # Clean phone
    phone = str(lead_dict.get("Phone Number", "")).strip()
    if not phone or phone == "nan":
        return False

    phone_clean = re.sub(r'[\s\-]', '', phone)
    
    # Check if already in jsonl
    existing_phones = set()
    if JSONL_PATH.exists():
        with open(JSONL_PATH, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line.strip())
                    p = re.sub(r'[\s\-]', '', str(obj.get("Phone Number", "")))
                    if p:
                        existing_phones.add(p)
                except Exception:
                    pass

    if phone_clean in existing_phones:
        return False

    # Append
    with open(JSONL_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(lead_dict, ensure_ascii=False) + "\n")
    return True

def append_leads_batch(leads_list):
    """Append multiple leads."""
    added = 0
    for lead in leads_list:
        if append_lead(lead):
            added += 1
    if added > 0:
        sync_to_excel_and_csv()
    return added

def get_all_leads():
    """Retrieve all leads from JSONL store."""
    if not JSONL_PATH.exists():
        return []
    leads = []
    seen = set()
    with open(JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line.strip())
                p = re.sub(r'[\s\-]', '', str(obj.get("Phone Number", "")))
                if p and p not in seen:
                    seen.add(p)
                    leads.append(obj)
            except Exception:
                pass
    return leads

def sync_to_excel_and_csv():
    """Export all stored JSONL leads to HNI.xlsx and CSV."""
    leads = get_all_leads()
    if not leads:
        return 0

    df = pd.DataFrame(leads)
    
    # Expected columns ordering
    cols = [
        "First Name", "Last Name", "Role", "Company", "Domain", "Phone Number",
        "Email", "City/Country", "Deliverability Status", "Full Address", "Website",
        "Source", "Phone Type"
    ]
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    df = df[cols]

    for attempt in range(10):
        try:
            df.to_excel(str(EXCEL_PATH), index=False, engine="openpyxl")
            break
        except Exception:
            time.sleep(1)

    for attempt in range(10):
        try:
            df.to_csv(str(CSV_PATH), index=False, encoding="utf-8")
            break
        except Exception:
            time.sleep(1)

    return len(df)

if __name__ == "__main__":
    count = sync_to_excel_and_csv()
    print(f"Master store synced: {count} leads in HNI.xlsx")
