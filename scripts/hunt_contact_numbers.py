import os
import env_loader
r"""
Indulge Global - Aggressive Contact Number Hunter
===================================================
Focuses exclusively on finding PERSONAL MOBILE numbers for GCC HNIs.
Combines: Apify Google Maps + Tavily Mobile Dorks + Consolidation from CSV.

Output: C:\Users\gozoi\Projects\indulge\data\HNI.xlsx
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os
import re
import json
import time
import hashlib
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
HNI_XLSX = DATA_DIR / "HNI.xlsx"
HNI_CSV = DATA_DIR / "indulge_gcc_hni_master.csv"
LOCK_FILE = DATA_DIR / ".write_lock"

# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")
TAVILY_KEYS = [k.strip() for k in os.environ.get("TAVILY_API_KEYS", "").split(",") if k.strip()]
tavily_idx = 0

ALL_LEADS = []  # Master list


def get_tavily_key():
    global tavily_idx
    key = TAVILY_KEYS[tavily_idx % len(TAVILY_KEYS)]
    tavily_idx += 1
    return key


# ---------------------------------------------------------------------------
# Phone number cleaner & classifier
# ---------------------------------------------------------------------------
UAE_MOBILE_RE = re.compile(r'\+971[\s\-]?5[0245689][\s\-]?\d{3}[\s\-]?\d{4}')
KSA_MOBILE_RE = re.compile(r'\+966[\s\-]?5\d[\s\-]?\d{3}[\s\-]?\d{4}')
QATAR_MOBILE_RE = re.compile(r'\+974[\s\-]?[3567]\d{3}[\s\-]?\d{4}')
BAHRAIN_MOBILE_RE = re.compile(r'\+973[\s\-]?3\d{3}[\s\-]?\d{4}')
KUWAIT_MOBILE_RE = re.compile(r'\+965[\s\-]?[569]\d{3}[\s\-]?\d{4}')
OMAN_MOBILE_RE = re.compile(r'\+968[\s\-]?[79]\d{3}[\s\-]?\d{4}')

# General phone pattern (any international)
PHONE_RE = re.compile(r'\+\d[\d\s\-]{8,15}\d')

MOBILE_PATTERNS = [UAE_MOBILE_RE, KSA_MOBILE_RE, QATAR_MOBILE_RE, BAHRAIN_MOBILE_RE, KUWAIT_MOBILE_RE, OMAN_MOBILE_RE]


def is_mobile(phone):
    """Check if a phone number is a mobile (not landline)."""
    clean = phone.replace(' ', '').replace('-', '')
    for pat in MOBILE_PATTERNS:
        if pat.search(phone):
            return True
    # UAE landlines start with +971 2/3/4/6/7/9 (2-digit area code)
    if re.match(r'\+971\s?[234679]', clean):
        return False
    # KSA landlines start with +966 1
    if re.match(r'\+966\s?1', clean):
        return False
    return True  # Unknown, assume mobile


def extract_phones_from_text(text):
    """Extract all phone numbers from text."""
    phones = PHONE_RE.findall(text)
    return [p.strip() for p in phones if len(p.replace(' ', '').replace('-', '')) >= 10]


def classify_phone(phone):
    """Return 'Personal Mobile / WhatsApp' or 'Office / Landline'."""
    return "Personal Mobile / WhatsApp" if is_mobile(phone) else "Executive Switchboard / Office"


# ---------------------------------------------------------------------------
# Dedup helper
# ---------------------------------------------------------------------------
seen_phones = set()
seen_names = set()


def is_duplicate(phone, name):
    clean_phone = re.sub(r'[\s\-]', '', phone)
    name_key = name.lower().strip()
    if clean_phone in seen_phones:
        return True
    if name_key and name_key in seen_names:
        return True
    if clean_phone:
        seen_phones.add(clean_phone)
    if name_key:
        seen_names.add(name_key)
    return False


# ---------------------------------------------------------------------------
# Name quality filter
# ---------------------------------------------------------------------------
JUNK_WORDS = {
    'breaking', 'news', 'weather', 'forecast', 'wikipedia', 'article', 'update',
    'report', 'latest', 'trending', 'analysis', 'jazeera', 'reuters', 'bloomberg',
    'executive', 'office', 'linkedin', 'average', 'compare', 'online', 'unknown',
    'google', 'facebook', 'twitter', 'instagram', 'youtube', 'review', 'reviews',
    'wikipedia', 'dubai', 'abu', 'dhabi', 'riyadh', 'doha', 'qatar', 'bahrain',
    'kuwait', 'oman', 'muscat', 'jeddah', 'saudi', 'arabia', 'uae', 'emirates',
    'good', 'services', 'best', 'top', 'premium', 'group', 'company', 'holding',
    'limited', 'llc', 'inc', 'corp', 'international', 'investment', 'capital',
    'management', 'australia', 'india', 'pakistan', 'china', 'japan', 'america',
    'director', 'chairman', 'co', 'the', 'hotels', 'pif', 'dr', 'mr', 'mrs',
}


def is_valid_name(first, last):
    """Check if first+last name looks like a real person."""
    if not first or not last:
        return False
    if not first.isalpha() or not last.isalpha():
        return False
    if first.lower() in JUNK_WORDS or last.lower() in JUNK_WORDS:
        return False
    if len(first) < 2 or len(last) < 2:
        return False
    return True


from scripts.phone_verifier import (
    classify_gcc_phone,
    extract_phone_with_proximity,
    clean_corporate_domain,
    clean_and_validate_email,
    is_valid_person_name,
    is_broker_or_retail_trap,
)
from scripts.entity_resolver import resolve_lead_entity
from scripts.lead_store import append_leads_batch, get_all_leads

APIFY_QUERIES = [
    ("Single Family Office DIFC Dubai", "Dubai, UAE"),
    ("Private Investment Group Downtown Dubai", "Dubai, UAE"),
    ("Family Business Holding Dubai", "Dubai, UAE"),
    ("Private Equity Firm DIFC Dubai", "Dubai, UAE"),
    ("Single Family Office ADGM Abu Dhabi", "Abu Dhabi, UAE"),
    ("Investment Holding Company Abu Dhabi", "Abu Dhabi, UAE"),
    ("Family Office Riyadh Olaya", "Riyadh, Saudi Arabia"),
    ("Holding Company KAFD Riyadh", "Riyadh, Saudi Arabia"),
    ("Family Holding Company Jeddah", "Jeddah, Saudi Arabia"),
    ("Family Office Doha West Bay", "Doha, Qatar"),
    ("Family Holding Company Kuwait City", "Kuwait City, Kuwait"),
    ("Family Office Manama Bahrain", "Manama, Bahrain"),
    ("Family Business Conglomerate Muscat Oman", "Muscat, Oman"),
]


def run_apify_query(query, location):
    """Run one Apify Google Maps query and return verified HNI Principal leads."""
    leads = []
    try:
        run_url = "https://api.apify.com/v2/acts/compass~crawler-google-places/runs"
        payload = {
            "searchStringsArray": [query],
            "maxCrawledPlacesPerSearch": 20,
            "language": "en",
            "maxImages": 0,
        }
        resp = requests.post(f"{run_url}?token={APIFY_TOKEN}", json=payload, timeout=30)
        run_data = resp.json()
        run_id = run_data.get("data", {}).get("id", "")
        if not run_id:
            return leads

        status = ""
        for _ in range(36):
            time.sleep(5)
            try:
                sr = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}", timeout=15)
                status = sr.json().get("data", {}).get("status", "")
                if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
                    break
            except Exception:
                continue

        if status != "SUCCEEDED":
            return leads

        dataset_id = sr.json().get("data", {}).get("defaultDatasetId", "")
        items_resp = requests.get(f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}", timeout=30)
        places = items_resp.json()

        for place in places:
            phone = place.get("phone", "")
            if not phone or phone == "No phone listed":
                continue

            title = place.get("title", "")
            website = place.get("website", "")
            address = place.get("address", "")
            category = place.get("categoryName", "Family Office / Holding")

            if is_broker_or_retail_trap(title, category, website):
                continue

            phone_info = classify_gcc_phone(phone, default_region="AE")
            if not phone_info.get("valid"):
                continue

            domain = clean_corporate_domain(website)
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

            name_full = f"{resolved['first_name']} {resolved['last_name']}".strip()
            if is_duplicate(phone_info["e164"], name_full):
                continue

            leads.append({
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
                "Source": "Apify Google Maps - Contact Hunter (Entity Resolved)",
                "Phone Type": phone_info["phone_type"],
                "Carrier": phone_info["carrier"],
                "WhatsApp Link": phone_info["wa_link"] or "",
            })

    except Exception as e:
        print(f"  [!] Apify error: {e}")

    return leads


TAVILY_MOBILE_DORKS = [
    'site:linkedin.com/in/ "Dubai" ("Founder" OR "Chairman") ("Holding" OR "Family Office") ("+971 50" OR "+971 52" OR "+971 54" OR "+971 55" OR "+971 58") -broker -agent',
    'site:linkedin.com/in/ "Abu Dhabi" ("CEO" OR "Chairman") ("Holding" OR "Investment") ("+971 50" OR "+971 52" OR "+971 55") -broker',
    'site:linkedin.com/in/ "Dubai" "Managing Partner" ("Private Equity" OR "Capital") ("+971 50" OR "+971 52" OR "+971 55") -broker',
    'site:linkedin.com/in/ "DIFC" ("Managing Partner" OR "Founder") ("+971 50" OR "+971 55") -broker',
    'site:linkedin.com/in/ "Riyadh" ("CEO" OR "Chairman" OR "Founder") ("Holding" OR "Group") ("+966 50" OR "+966 55" OR "+966 54") -broker',
    'site:linkedin.com/in/ "Jeddah" ("CEO" OR "Chairman" OR "Founder") ("Holding" OR "Group") ("+966 50" OR "+966 55") -broker',
    'site:linkedin.com/in/ "Doha" ("CEO" OR "Chairman" OR "Founder") ("Holding" OR "Group") ("+974 3" OR "+974 5" OR "+974 6") -broker',
    'site:linkedin.com/in/ "Kuwait" ("CEO" OR "Chairman") ("Holding" OR "Capital") ("+965 5" OR "+965 6" OR "+965 9") -broker',
]


def tavily_search(query):
    """Search Tavily and extract verified personal mobile numbers within 120 chars of executive name."""
    leads = []
    key = get_tavily_key()
    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": key,
                "query": query,
                "search_depth": "advanced",
                "max_results": 10,
                "include_raw_content": True,
            },
            timeout=30,
        )

        if resp.status_code == 429:
            print("  [!] Rate limited, waiting 10s...")
            time.sleep(10)
            return leads

        data = resp.json()
        results = data.get("results", [])

        for r in results:
            content = ((r.get("content") or "") + " " + (r.get("raw_content") or ""))[:5000]
            title = r.get("title", "")
            url = r.get("url", "")
            combined_text = f"{title} {content}"

            clean_title = re.sub(r'\|\s*LinkedIn.*$', '', title).strip()
            parts = clean_title.split('-')
            first, last = "", ""
            role = "Chairman & Managing Partner"
            comp = "Private Family Office"

            if len(parts) >= 2:
                name_words = [w for w in re.sub(r'[^a-zA-Z\s]', '', parts[0]).split() if len(w) > 1]
                if len(name_words) >= 2:
                    first, last = name_words[0].capitalize(), name_words[-1].capitalize()
                role = parts[1].strip()
            if len(parts) >= 3:
                comp = parts[2].strip()

            if not is_valid_person_name(first, last, comp):
                continue

            if is_broker_or_retail_trap(comp, role, url):
                continue

            phone_info = extract_phone_with_proximity(
                text=combined_text,
                first_name=first,
                last_name=last,
                url=url,
                default_region="AE",
                max_distance=120,
                require_mobile=True,
            )
            if not phone_info:
                continue

            location = "Dubai, UAE"
            if "abu dhabi" in content.lower():
                location = "Abu Dhabi, UAE"
            elif "riyadh" in content.lower():
                location = "Riyadh, Saudi Arabia"
            elif "jeddah" in content.lower():
                location = "Jeddah, Saudi Arabia"
            elif "doha" in content.lower():
                location = "Doha, Qatar"
            elif "bahrain" in content.lower() or "manama" in content.lower():
                location = "Manama, Bahrain"
            elif "kuwait" in content.lower():
                location = "Kuwait City, Kuwait"
            elif "muscat" in content.lower() or "oman" in content.lower():
                location = "Muscat, Oman"

            domain = clean_corporate_domain(url)
            resolved = resolve_lead_entity(
                first_name=first,
                last_name=last,
                company_name=comp[:80],
                title=role[:60],
                email="",
                domain=domain,
                allow_network=True,
            )
            if not resolved["name_valid"]:
                continue

            name_full = f"{resolved['first_name']} {resolved['last_name']}".strip()
            if is_duplicate(phone_info["e164"], name_full):
                continue

            leads.append({
                "First Name": resolved["first_name"],
                "Last Name": resolved["last_name"],
                "Role": resolved["title"],
                "Company": comp[:80],
                "Domain": resolved["domain"] if resolved["domain"] else "N/A",
                "Phone Number": phone_info["formatted_intl"],
                "E164": phone_info["e164"],
                "Email": resolved["email"],
                "City/Country": location,
                "Deliverability Status": "Verified Mobile & WhatsApp Direct" if resolved["email"] == "N/A" else "Verified Corporate Email & VIP Mobile",
                "Full Address": location,
                "Website": url,
                "Source": "Tavily Direct Mobile Dork",
                "Phone Type": phone_info["phone_type"],
                "Carrier": phone_info["carrier"],
                "WhatsApp Link": phone_info["wa_link"] or "",
            })

    except Exception as e:
        print(f"  [!] Tavily error: {e}")

    return leads


def save_all_leads():
    """Consolidate and save all leads via lead_store to HNI.xlsx + CSV."""
    global ALL_LEADS
    if not ALL_LEADS:
        return len(get_all_leads())
    append_leads_batch(ALL_LEADS, allow_network=True)
    return len(get_all_leads())


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    global ALL_LEADS

    print("=" * 70)
    print("  INDULGE GLOBAL - AGGRESSIVE CONTACT NUMBER HUNTER")
    print("  Finding personal mobile numbers for GCC HNI targets")
    print("=" * 70)

    # Step 0: Load existing leads to avoid duplicates
    if HNI_XLSX.exists():
        try:
            existing = pd.read_excel(str(HNI_XLSX))
            for _, row in existing.iterrows():
                phone = str(row.get("Phone Number", ""))
                name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
                if phone:
                    seen_phones.add(re.sub(r'[\s\-]', '', phone))
                if name:
                    seen_names.add(name.lower())
            print(f"[+] Loaded {len(existing)} existing leads (will skip duplicates)")
        except Exception:
            pass

    if HNI_CSV.exists():
        try:
            existing_csv = pd.read_csv(str(HNI_CSV))
            for _, row in existing_csv.iterrows():
                phone = str(row.get("Phone Number", ""))
                name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
                if phone:
                    seen_phones.add(re.sub(r'[\s\-]', '', phone))
                if name:
                    seen_names.add(name.lower())
        except Exception:
            pass

    # ===================================================================
    # PHASE 1: APIFY GOOGLE MAPS - Luxury Services with Direct Numbers
    # ===================================================================
    print(f"\n{'='*60}")
    print(f"  PHASE 1: APIFY GOOGLE MAPS - {len(APIFY_QUERIES)} Targeted Queries")
    print(f"{'='*60}\n")

    for i, (query, location) in enumerate(APIFY_QUERIES):
        print(f"[{i+1}/{len(APIFY_QUERIES)}] Apify: '{query}' ({location})...")
        leads = run_apify_query(query, location)
        if leads:
            ALL_LEADS.extend(leads)
            mobiles = sum(1 for l in leads if "Mobile" in l.get("Phone Type", ""))
            print(f"  +{len(leads)} contacts ({mobiles} mobiles) | Running total: {len(ALL_LEADS)}")
        else:
            print(f"  No new contacts")

        # Save checkpoint every 5 queries
        if (i + 1) % 5 == 0 and ALL_LEADS:
            total = save_all_leads()
            print(f"  [CHECKPOINT] Saved! Total in HNI.xlsx: {total}")

        time.sleep(1)

    # ===================================================================
    # PHASE 2: TAVILY MOBILE DORKS - Direct Personal Numbers
    # ===================================================================
    print(f"\n{'='*60}")
    print(f"  PHASE 2: TAVILY MOBILE DORKS - {len(TAVILY_MOBILE_DORKS)} Search Queries")
    print(f"{'='*60}\n")

    for i, dork in enumerate(TAVILY_MOBILE_DORKS):
        short = dork[:80] + "..." if len(dork) > 80 else dork
        print(f"[{i+1}/{len(TAVILY_MOBILE_DORKS)}] Tavily: '{short}'")
        leads = tavily_search(dork)
        if leads:
            ALL_LEADS.extend(leads)
            mobiles = sum(1 for l in leads if "Mobile" in l.get("Phone Type", ""))
            print(f"  +{len(leads)} contacts ({mobiles} mobiles) | Running total: {len(ALL_LEADS)}")
        else:
            print(f"  No new numbers")

        # Save checkpoint every 10 queries
        if (i + 1) % 10 == 0 and ALL_LEADS:
            total = save_all_leads()
            print(f"  [CHECKPOINT] Saved! Total in HNI.xlsx: {total}")

        time.sleep(2)  # Rate limit spacing

    # ===================================================================
    # FINAL: Save everything
    # ===================================================================
    print(f"\n{'='*60}")
    print(f"  FINAL SAVE")
    print(f"{'='*60}\n")

    total = save_all_leads()
    mobile_count = sum(1 for l in ALL_LEADS if "Mobile" in l.get("Phone Type", ""))
    office_count = sum(1 for l in ALL_LEADS if "Office" in l.get("Phone Type", "") or "Switchboard" in l.get("Phone Type", ""))

    print(f"\n{'='*60}")
    print(f"  CONTACT HUNTER COMPLETE")
    print(f"  New contacts found: {len(ALL_LEADS)}")
    print(f"    Personal Mobiles:  {mobile_count}")
    print(f"    Office/Switchboard: {office_count}")
    print(f"  Total in HNI.xlsx:   {total}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
