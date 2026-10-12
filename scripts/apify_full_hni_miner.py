import os
import env_loader
r"""
=============================================================================
INDULGE GLOBAL - FULL-FLEDGED MIDDLE EAST HNI & PHONE MINER
=============================================================================
Mines complete HNI/UHNI leads across GCC (Dubai, Abu Dhabi, Riyadh, Jeddah, Doha):
1. Apify Google Maps Luxury & Real Estate & Family Office Actor:
   - Extracts business name, phone numbers, international dialing codes,
     office addresses, websites, and review status.
2. Apify / Tavily Multi-Source Decision-Maker & Phone Enrichment:
   - Maps C-suite and Family Office leaders.
   - Extracts and normalizes phone numbers (+971, +966, +974).
   - Verifies corporate email deliverability via Port 25 SMTP.
3. Live Synchronized Output to:
   - C:\Users\gozoi\Projects\indulge\data\HNI.xlsx (Formatted Excel Workbook)
   - C:\Users\gozoi\Projects\indulge\data\indulge_gcc_hni_master.csv
=============================================================================
"""

import os
import sys
import time
import re
import csv
import requests
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")
TAVILY_KEY = os.environ.get("TAVILY_API_KEYS", "").split(",")[0].strip()

BASE_DIR = r"C:\Users\gozoi\Projects\indulge"
DATA_DIR = os.path.join(BASE_DIR, "data")
EXCEL_PATH = os.path.join(DATA_DIR, "HNI.xlsx")
CSV_PATH = os.path.join(DATA_DIR, "indulge_gcc_hni_master.csv")

os.makedirs(DATA_DIR, exist_ok=True)

from smtp_verifier import get_mx_record, verify_email_smtp, generate_email_permutations

# High-intent Google Maps luxury & family office queries
GMAPS_SEARCH_QUERIES = [
    # Dubai & Abu Dhabi
    "Luxury Real Estate Developer Dubai",
    "Family Office Dubai DIFC",
    "Private Wealth Management Dubai",
    "Holding Company Dubai Business Bay",
    "Luxury Hospitality Group Dubai",
    "Family Office Abu Dhabi ADGM",
    "Private Equity Firm Dubai",
    
    # Saudi Arabia (Riyadh & Jeddah)
    "Holding Company Riyadh",
    "Real Estate Developer Riyadh KAFD",
    "Family Business Holding Riyadh",
    "Investment Company Jeddah",
    
    # Qatar & Kuwait
    "Family Holding Company Doha",
    "Real Estate Development Kuwait"
]

def format_excel_file(file_path):
    """Applies luxury formatting with gold headers and auto-adjusted column widths."""
    try:
        from openpyxl import load_workbook
        wb = load_workbook(file_path)
        ws = wb.active
        ws.title = "Middle East HNI Leads"

        header_fill = PatternFill(start_color="1A202C", end_color="1A202C", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="D4AF37") # Gold text
        align_center = Alignment(horizontal="center", vertical="center")
        align_left = Alignment(horizontal="left", vertical="center")
        thin_border = Border(
            left=Side(style='thin', color='E2E8F0'),
            right=Side(style='thin', color='E2E8F0'),
            top=Side(style='thin', color='E2E8F0'),
            bottom=Side(style='thin', color='E2E8F0')
        )

        for col_idx in range(1, ws.max_column + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = align_center
            cell.border = thin_border

        for row in range(2, ws.max_row + 1):
            fill = PatternFill(start_color="F8FAFC" if row % 2 == 0 else "FFFFFF", fill_type="solid")
            for col in range(1, ws.max_column + 1):
                c = ws.cell(row=row, column=col)
                c.fill = fill
                c.border = thin_border
                c.font = Font(name="Calibri", size=10)
                if col in [7, 8, 9]: # Status, Phone, City
                    c.alignment = align_center

        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

        wb.save(file_path)
    except Exception as e:
        print(f"Warning formatting excel: {e}")

def save_to_excel_and_csv(leads):
    """Saves leads to both HNI.xlsx and indulge_gcc_hni_master.csv with deduplication."""
    if not leads:
        return 0

    df_new = pd.DataFrame(leads)

    # Load existing Excel if exists
    if os.path.exists(EXCEL_PATH):
        try:
            df_old = pd.read_excel(EXCEL_PATH)
            df_combined = pd.concat([df_old, df_new], ignore_index=True)
        except Exception:
            df_combined = df_new
    else:
        df_combined = df_new

    # Deduplicate by Email (if present) or (Name + Company) or Phone
    df_combined.drop_duplicates(subset=['Email'], keep='first', inplace=True)
    if 'Phone Number' in df_combined.columns:
        # Keep non-empty unique phones
        mask = df_combined['Phone Number'].astype(str).str.strip().ne('')
        df_phones = df_combined[mask].drop_duplicates(subset=['Phone Number'], keep='first')
        df_no_phones = df_combined[~mask]
        df_combined = pd.concat([df_phones, df_no_phones], ignore_index=True)

    df_combined.to_excel(EXCEL_PATH, index=False)
    format_excel_file(EXCEL_PATH)

    # Sync to master CSV
    df_combined.to_csv(CSV_PATH, index=False, encoding='utf-8')
    return len(df_combined)

def run_apify_gmaps_actor(query, max_items=15):
    """Calls Apify Google Places / Maps Scraper Actor."""
    print(f"\n🗺️ Running Apify Google Maps Actor for: '{query}'...")
    url = f"https://api.apify.com/v2/acts/compass~crawler-google-places/runs?token={APIFY_TOKEN}"
    payload = {
        "searchStringsArray": [query],
        "maxCrawledPlacesPerSearch": max_items,
        "language": "en",
        "skipClosedPlaces": True,
        "includeOpeningHours": False,
        "includePeopleAlsoSearch": False
    }

    try:
        resp = requests.post(url, json=payload, timeout=20)
        if resp.status_code not in [200, 201]:
            print(f"  ❌ Apify Start Failed: {resp.status_code} - {resp.text[:150]}")
            return []

        run_data = resp.json().get('data', {})
        run_id = run_data.get('id')
        dataset_id = run_data.get('defaultDatasetId')
        print(f"  ⚡ Run started: {run_id}. Waiting for completion...")

        # Poll status
        for _ in range(25):
            time.sleep(5)
            s_resp = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}", timeout=10)
            if s_resp.status_code == 200:
                status = s_resp.json().get('data', {}).get('status')
                if status in ['SUCCEEDED', 'READY']:
                    break
                elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                    print(f"  ❌ Apify Run Ended with status: {status}")
                    return []

        # Fetch Dataset items
        items_resp = requests.get(f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}&format=json&limit={max_items}", timeout=20)
        if items_resp.status_code == 200:
            items = items_resp.json()
            print(f"  ✅ Retrieved {len(items)} places from Google Maps!")
            return items
    except Exception as e:
        print(f"  ❌ Error in Apify Maps run: {e}")
    return []

def extract_hni_from_gmaps_item(item, default_city="Dubai, UAE"):
    """Transforms Apify Google Maps item into HNI lead entry."""
    title = item.get('title', '').strip()
    phone = item.get('phone', '') or item.get('phoneUnformatted', '')
    website = item.get('website', '')
    address = item.get('address', '')
    category = item.get('categoryName', '')

    if not title:
        return None

    # Clean domain
    domain = ""
    if website:
        domain = re.sub(r'https?://', '', website).split('/')[0].replace('www.', '').strip()

    # Determine city from address
    city = default_city
    if "abu dhabi" in address.lower():
        city = "Abu Dhabi, UAE"
    elif "riyadh" in address.lower():
        city = "Riyadh, Saudi Arabia"
    elif "jeddah" in address.lower():
        city = "Jeddah, Saudi Arabia"
    elif "doha" in address.lower():
        city = "Doha, Qatar"
    elif "kuwait" in address.lower():
        city = "Kuwait City, Kuwait"

    # Search for Founder / MD / Chairman of this business entity
    fn, ln, role, verified_email = "Executive", "Office", f"Founder / Principal ({category})", f"contact@{domain}" if domain else ""
    
    if domain:
        # Quick probe for specific leader
        q = f'"{title}" ("Founder" OR "Chairman" OR "Managing Director" OR "CEO") site:linkedin.com/in/'
        try:
            p_resp = requests.post(
                'https://api.tavily.com/search',
                json={'api_key': TAVILY_KEY, 'query': q, 'max_results': 2},
                timeout=8
            )
            if p_resp.status_code == 200:
                res = p_resp.json().get('results', [])
                if res:
                    first_res = res[0].get('title', '')
                    clean_res = re.sub(r' - LinkedIn.*', '', first_res)
                    tokens = [t for t in re.sub(r'[^a-zA-Z\s]', '', clean_res).split() if len(t) > 1]
                    if len(tokens) >= 2:
                        fn, ln = tokens[0].capitalize(), tokens[-1].capitalize()
                        role = "Chairman / Managing Director"
        except Exception:
            pass

        # Email Permutation & SMTP
        mx = get_mx_record(domain)
        status = "Risky/Catch-all"
        if fn != "Executive" and mx:
            perms = generate_email_permutations(fn, ln, domain)
            if perms:
                for candidate in perms[:3]:
                    if verify_email_smtp(candidate, mx):
                        verified_email = candidate
                        status = "Valid (SMTP 250 OK)"
                        break
                if not verified_email and perms:
                    verified_email = perms[0]
    else:
        status = "Direct Phone Only"

    return {
        "First Name": fn,
        "Last Name": ln,
        "Role": role,
        "Company": title,
        "Domain": domain,
        "Phone Number": phone,
        "Email": verified_email,
        "City/Country": city,
        "Deliverability Status": status,
        "Full Address": address,
        "Website": website,
        "Source": "Apify Google Maps GCC Luxury Intelligence"
    }

def run_full_fledged_miner():
    print("=" * 70)
    print("💎 INDULGE GLOBAL - FULL-FLEDGED MIDDLE EAST HNI & PHONE MINER")
    print("=" * 70)
    print(f"[+] Output Excel: {EXCEL_PATH}")
    print(f"[+] Output CSV: {CSV_PATH}")
    print(f"[+] Apify Engine: Google Places Luxury & Family Office Cluster")
    print("=" * 70)

    total_leads_added = 0

    for query in GMAPS_SEARCH_QUERIES:
        default_city = "Dubai, UAE"
        if "Riyadh" in query or "Jeddah" in query:
            default_city = "Saudi Arabia"
        elif "Abu Dhabi" in query:
            default_city = "Abu Dhabi, UAE"
        elif "Doha" in query:
            default_city = "Doha, Qatar"
        elif "Kuwait" in query:
            default_city = "Kuwait"

        places = run_apify_gmaps_actor(query, max_items=12)
        batch_leads = []

        for p in places:
            lead = extract_hni_from_gmaps_item(p, default_city=default_city)
            if lead:
                batch_leads.append(lead)
                phone_str = lead['Phone Number'] if lead['Phone Number'] else "No phone listed"
                print(f"  👑 [{lead['Company']}] {lead['First Name']} {lead['Last Name']} | 📞 {phone_str} | ✉️ {lead['Email']}")

        if batch_leads:
            saved_count = save_to_excel_and_csv(batch_leads)
            total_leads_added += len(batch_leads)
            print(f"  💾 Saved batch! Total leads in HNI.xlsx: {saved_count}")

        time.sleep(2)

    print("\n" + "=" * 70)
    print(f"🏆 ALL APPIFY GCC RUNS COMPLETED! Total Leads Exported: {total_leads_added}")
    print(f"📁 Excel File: {EXCEL_PATH}")
    print("=" * 70)

if __name__ == "__main__":
    run_full_fledged_miner()
