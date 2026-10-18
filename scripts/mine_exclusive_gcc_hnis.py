import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts import env_loader
from scripts.phone_verifier import (
    classify_gcc_phone,
    extract_phone_with_proximity,
    clean_corporate_domain,
    clean_and_validate_email,
    is_valid_person_name,
    is_broker_or_retail_trap,
)
from scripts.entity_resolver import resolve_lead_entity
from scripts.lead_store import append_leads_batch, get_all_leads, EXCEL_PATH as HNI_XLSX, CSV_PATH as HNI_CSV

import re
import json
import time
import requests
import pandas as pd
from urllib.parse import urlparse

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")
TAVILY_KEYS = [k.strip() for k in os.environ.get("TAVILY_API_KEYS", "").split(",") if k.strip()]
tavily_idx = 0


def get_tavily_key():
    global tavily_idx
    if not TAVILY_KEYS:
        return ""
    key = TAVILY_KEYS[tavily_idx % len(TAVILY_KEYS)]
    tavily_idx += 1
    return key


JUNK_NAMES = {
    "breaking", "news", "weather", "forecast", "wikipedia", "article", "update",
    "report", "latest", "trending", "analysis", "jazeera", "reuters", "bloomberg",
    "executive", "office", "linkedin", "average", "compare", "online", "unknown",
    "google", "facebook", "twitter", "instagram", "youtube", "review", "reviews",
    "dubai", "abu", "dhabi", "riyadh", "doha", "qatar", "bahrain", "kuwait",
    "oman", "muscat", "jeddah", "saudi", "arabia", "uae", "emirates", "good",
    "services", "best", "top", "premium", "group", "company", "holding", "limited",
    "llc", "inc", "corp", "international", "investment", "capital", "management",
    "australia", "india", "pakistan", "china", "japan", "america", "director",
    "chairman", "co", "the", "hotels", "pif", "dr", "mr", "mrs", "profile", "contact"
}


def clean_name(raw_name):
    """Attempt to extract valid (First, Last) from title/snippet. Rejects single-word or placeholder names."""
    if not raw_name:
        return None, None
    raw_name = re.sub(r'[^\w\s]', ' ', raw_name)
    parts = [p.strip() for p in raw_name.split() if p.strip()]
    valid = [p for p in parts if p.lower() not in JUNK_NAMES and len(p) >= 2 and p.isalpha()]
    if len(valid) >= 2:
        fn = valid[0].capitalize()
        ln = " ".join([v.capitalize() for v in valid[1:3]])
        if is_valid_person_name(fn, ln):
            return fn, ln
    return None, None


HNI_TARGET_DORKS = [
    ('site:linkedin.com/in/ ("Founder" OR "Managing Partner" OR "Principal" OR "Chairman") "Family Office" "Dubai" ("+971 50" OR "+971 52" OR "+971 54" OR "+971 55" OR "+971 58") -broker -agent', "Dubai, UAE", "AE"),
    ('site:linkedin.com/in/ ("Founder" OR "Managing Partner" OR "Chief Executive") "Family Office" "Abu Dhabi" ("+971 50" OR "+971 52" OR "+971 55") -broker -agent', "Abu Dhabi, UAE", "AE"),
    ('site:linkedin.com/in/ ("Principal" OR "Managing Director" OR "Chairman") "Single Family Office" ("Dubai" OR "DIFC" OR "ADGM") -broker', "Dubai, UAE", "AE"),
    ('site:linkedin.com/in/ ("Managing Partner" OR "General Partner") "Private Equity" ("DIFC" OR "Dubai") ("+971 50" OR "+971 52" OR "+971 55") -broker', "Dubai, UAE", "AE"),
    ('site:linkedin.com/in/ ("Founder" OR "Chairman" OR "CEO") ("Developments" OR "Holding") "Dubai" ("+971 50" OR "+971 52" OR "+971 55") -broker -agent -realtor', "Dubai, UAE", "AE"),
    ('site:linkedin.com/in/ ("Chairman" OR "Vice Chairman" OR "Board Member") "Holding" "Dubai" ("+971 50" OR "+971 52" OR "+971 55") -broker', "Dubai, UAE", "AE"),
    ('site:linkedin.com/in/ ("Chairman" OR "President" OR "CEO" OR "Owner") "Holding" "Riyadh" ("+966 50" OR "+966 55" OR "+966 54" OR "+966 56") -broker', "Riyadh, Saudi Arabia", "SA"),
    ('site:linkedin.com/in/ ("Founder" OR "Managing Director" OR "Partner") "Family Office" "Riyadh" ("+966 50" OR "+966 55") -broker', "Riyadh, Saudi Arabia", "SA"),
    ('site:linkedin.com/in/ ("President" OR "CEO" OR "Vice Chairman") "Group" "Jeddah" ("+966 50" OR "+966 55" OR "+966 54") -broker', "Jeddah, Saudi Arabia", "SA"),
    ('site:linkedin.com/in/ ("Managing Partner" OR "Principal") "Venture Capital" "Riyadh" ("+966 50" OR "+966 55") -broker', "Riyadh, Saudi Arabia", "SA"),
    ('site:linkedin.com/in/ ("Founder & CEO" OR "Co-Founder & CEO") ("Fintech" OR "AI") "Dubai" ("+971 50" OR "+971 52" OR "+971 55" OR "+971 58")', "Dubai, UAE", "AE"),
    ('site:linkedin.com/in/ ("Chairman" OR "Vice Chairman" OR "Managing Director") ("Holding" OR "Family Office") "Doha" ("+974 3" OR "+974 5" OR "+974 6" OR "+974 7")', "Doha, Qatar", "QA"),
    ('site:linkedin.com/in/ ("Chairman" OR "Managing Director" OR "CEO") ("Holding" OR "Investments") "Kuwait" ("+965 5" OR "+965 6" OR "+965 9")', "Kuwait City, Kuwait", "KW"),
    ('site:linkedin.com/in/ ("Managing Director" OR "Partner" OR "Owner") ("Holding" OR "Family Business") "Bahrain" ("+973 3")', "Manama, Bahrain", "BH"),
    ('site:linkedin.com/in/ ("Chairman" OR "Managing Director") "Holding" "Muscat" ("+968 9" OR "+968 7")', "Muscat, Oman", "OM"),
]

APIFY_HNI_CLUSTERS = [
    ("Single Family Office DIFC Dubai", "Dubai, UAE", "AE"),
    ("Multi Family Office ADGM Abu Dhabi", "Abu Dhabi, UAE", "AE"),
    ("Private Investment Office Dubai Downtown", "Dubai, UAE", "AE"),
    ("Private Family Office Riyadh Olaya", "Riyadh, Saudi Arabia", "SA"),
    ("Family Holding Company Jeddah Corniche", "Jeddah, Saudi Arabia", "SA"),
    ("Family Holding Company Doha West Bay", "Doha, Qatar", "QA"),
    ("Private Equity Holding Kuwait Sharq", "Kuwait City, Kuwait", "KW"),
    ("Family Business Holding Manama", "Manama, Bahrain", "BH"),
]


def mine_tavily_hnis():
    print(f"\n=======================================================")
    print(f"EXCLUSIVE HNI MINER - PHASE 1: TAVILY VIP DORKS ({len(HNI_TARGET_DORKS)} Targets)")
    print(f"=======================================================\n")

    batch = []
    for i, (query, location, region_code) in enumerate(HNI_TARGET_DORKS):
        key = get_tavily_key()
        print(f"[{i+1}/{len(HNI_TARGET_DORKS)}] Mining: '{query[:75]}...' ({location})")
        try:
            resp = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": key,
                    "query": query,
                    "search_depth": "advanced",
                    "max_results": 10,
                    "include_raw_content": True
                },
                timeout=25
            )
            if resp.status_code == 429:
                print("  [!] Rate limited, switching key and waiting 5s...")
                time.sleep(5)
                continue

            data = resp.json()
            results = data.get("results", [])
            for r in results:
                title = r.get("title", "")
                snippet = (r.get("content") or "") + " " + (r.get("raw_content") or "")
                url = r.get("url", "")
                combined_text = f"{title} {snippet}"

                clean_title = re.sub(r'\|\s*LinkedIn.*$', '', title).strip()
                title_parts = [p.strip() for p in clean_title.split('-')]

                first_name, last_name = None, None
                role = "Chairman & Managing Partner"
                company = "Private Family Office"

                if len(title_parts) >= 3:
                    fn, ln = clean_name(title_parts[0])
                    if fn and ln:
                        first_name, last_name = fn, ln
                        role = title_parts[1]
                        company = title_parts[2]
                elif len(title_parts) == 2:
                    fn, ln = clean_name(title_parts[0])
                    if fn and ln:
                        first_name, last_name = fn, ln
                        role = title_parts[1]
                else:
                    fn, ln = clean_name(title_parts[0])
                    if fn and ln:
                        first_name, last_name = fn, ln

                if not first_name or not last_name:
                    continue

                if is_broker_or_retail_trap(company, role, url):
                    continue

                # Strictly require a real phone within 120 chars of the person's name (NO +971 4 369 1700 fallback!)
                phone_info = extract_phone_with_proximity(
                    text=combined_text,
                    first_name=first_name,
                    last_name=last_name,
                    url=url,
                    default_region=region_code,
                    max_distance=120,
                    require_mobile=False,
                )
                if not phone_info:
                    continue

                raw_domain = ""
                if url:
                    try:
                        raw_domain = urlparse(url).netloc.replace("www.", "")
                    except Exception:
                        pass

                resolved = resolve_lead_entity(
                    first_name=first_name,
                    last_name=last_name,
                    company_name=company[:70],
                    title=role[:60],
                    email="",
                    domain=raw_domain,
                    allow_network=True,
                )
                if not resolved["name_valid"]:
                    continue

                lead = {
                    "First Name": resolved["first_name"],
                    "Last Name": resolved["last_name"],
                    "Role": resolved["title"],
                    "Company": company[:70],
                    "Domain": resolved["domain"] if resolved["domain"] else "N/A",
                    "Phone Number": phone_info["formatted_intl"],
                    "E164": phone_info["e164"],
                    "Email": resolved["email"],
                    "City/Country": location,
                    "Deliverability Status": "Verified Mobile & WhatsApp Direct" if phone_info["is_mobile"] else "Verified Corporate Line (Email N/A)",
                    "Full Address": location,
                    "Website": url,
                    "Source": "Indulge HNI Intelligence Engine (Tavily/LinkedIn VIP)",
                    "Phone Type": phone_info["phone_type"],
                    "Carrier": phone_info["carrier"],
                    "WhatsApp Link": phone_info["wa_link"] or "",
                }
                batch.append(lead)
                print(f"  [{company[:30]}] {lead['First Name']} {lead['Last Name']} ({lead['Role'][:25]}) | {lead['Phone Number']} ({lead['Phone Type']})")

            if (i + 1) % 4 == 0 and batch:
                added = append_leads_batch(batch)
                batch = []
                print(f"  Saved {added} deduplicated records to HNI.xlsx")

            time.sleep(2)
        except Exception as e:
            print(f"  [!] Query error: {e}")

    if batch:
        added = append_leads_batch(batch)
        print(f"Phase 1 complete! Added {added} verified records to HNI.xlsx")


def mine_apify_hnis():
    print(f"\n=======================================================")
    print(f"EXCLUSIVE HNI MINER - PHASE 2: APIFY FAMILY OFFICE & WEALTH HUBS ({len(APIFY_HNI_CLUSTERS)} Clusters)")
    print(f"=======================================================\n")

    batch = []
    for i, (query, location, region_code) in enumerate(APIFY_HNI_CLUSTERS):
        print(f"[{i+1}/{len(APIFY_HNI_CLUSTERS)}] Apify Maps: '{query}' ({location})...")
        try:
            run_url = "https://api.apify.com/v2/acts/compass~crawler-google-places/runs"
            payload = {
                "searchStringsArray": [query],
                "maxCrawledPlacesPerSearch": 20,
                "language": "en",
                "maxImages": 0
            }
            resp = requests.post(f"{run_url}?token={APIFY_TOKEN}", json=payload, timeout=30)
            run_data = resp.json()
            run_id = run_data.get("data", {}).get("id", "")
            if not run_id:
                continue

            status = ""
            for _ in range(30):
                time.sleep(5)
                try:
                    sr = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}", timeout=15)
                    status = sr.json().get("data", {}).get("status", "")
                    if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
                        break
                except Exception:
                    continue

            if status != "SUCCEEDED":
                continue

            dataset_id = sr.json().get("data", {}).get("defaultDatasetId", "")
            items_resp = requests.get(f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}", timeout=30)
            places = items_resp.json()

            for place in places:
                phone = place.get("phone", "")
                title = place.get("title", "")
                website = place.get("website", "")
                address = place.get("address", "")
                category = place.get("categoryName", "Family Office / Investment")

                if not phone or phone == "No phone listed":
                    continue

                if is_broker_or_retail_trap(title, category, website):
                    continue

                phone_info = classify_gcc_phone(phone, default_region=region_code)
                if not phone_info.get("valid"):
                    continue

                domain = clean_corporate_domain(website)

                # Resolve actual Chairman/CEO via Curated Registry or Apollo (never use "Chairman / Managing Director (Company)")
                resolved = resolve_lead_entity(
                    first_name="",
                    last_name="",
                    company_name=title,
                    title=f"Chairman & Managing Partner ({category})",
                    email="",
                    domain=domain,
                    allow_network=True,
                )
                if not resolved["name_valid"]:
                    continue

                lead = {
                    "First Name": resolved["first_name"],
                    "Last Name": resolved["last_name"],
                    "Role": resolved["title"],
                    "Company": title,
                    "Domain": resolved["domain"] if resolved["domain"] else "N/A",
                    "Phone Number": phone_info["formatted_intl"],
                    "E164": phone_info["e164"],
                    "Email": resolved["email"],
                    "City/Country": location,
                    "Deliverability Status": "Verified Mobile & WhatsApp Direct" if phone_info["is_mobile"] else "Verified Corporate Line (Email N/A)",
                    "Full Address": address or location,
                    "Website": website,
                    "Source": "Indulge HNI Family Office & Wealth Registry (Apify + Entity Resolved)",
                    "Phone Type": phone_info["phone_type"],
                    "Carrier": phone_info["carrier"],
                    "WhatsApp Link": phone_info["wa_link"] or "",
                }
                batch.append(lead)
                print(f"  [{title[:30]}] {lead['First Name']} {lead['Last Name']} | {lead['Phone Number']} ({lead['Phone Type']})")

            if batch:
                added = append_leads_batch(batch)
                batch = []
                print(f"  Saved {added} deduplicated records to HNI.xlsx")
            time.sleep(1)
        except Exception as e:
            print(f"  [!] Apify cluster error: {e}")


def main():
    print("=================================================================")
    print("INDULGE GLOBAL - ULTRA-TARGETED GCC HNI & CONTACT MINER")
    print("=================================================================")
    current = get_all_leads()
    print(f"[+] Loaded existing database baseline: {len(current)} leads")

    mine_tavily_hnis()
    mine_apify_hnis()

    final = get_all_leads()
    print("\n=================================================================")
    print(f"MINING RUN COMPLETED SUCCESSFULLY!")
    print(f"Final HNI Records in HNI.xlsx: {len(final)}")
    print("=================================================================")


if __name__ == "__main__":
    main()
