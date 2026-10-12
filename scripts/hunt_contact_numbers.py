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


# ---------------------------------------------------------------------------
# APIFY Google Maps - Targeted for contact numbers
# ---------------------------------------------------------------------------
APIFY_QUERIES = [
    # High-value personal services (more likely to have personal mobiles)
    ("Luxury Real Estate Agent Dubai", "Dubai, UAE"),
    ("Private Wealth Advisor Dubai DIFC", "Dubai, UAE"),
    ("Personal Shopper Dubai", "Dubai, UAE"),
    ("Luxury Car Dealer Dubai", "Dubai, UAE"),
    ("Yacht Broker Dubai Marina", "Dubai, UAE"),
    ("Private Jet Charter Dubai", "Dubai, UAE"),
    ("Luxury Interior Designer Dubai", "Dubai, UAE"),
    ("Private Chef Dubai", "Dubai, UAE"),
    ("Luxury Wedding Planner Dubai", "Dubai, UAE"),
    ("Fine Art Gallery Dubai", "Dubai, UAE"),
    ("Bespoke Tailor Dubai", "Dubai, UAE"),
    ("Luxury Travel Agent Dubai", "Dubai, UAE"),
    ("Private Tutor Dubai", "Dubai, UAE"),
    ("Concierge Service Dubai", "Dubai, UAE"),
    ("VIP Event Planner Dubai", "Dubai, UAE"),
    ("Luxury Spa Dubai Jumeirah", "Dubai, UAE"),

    # Abu Dhabi luxury
    ("Private Wealth Advisor Abu Dhabi", "Abu Dhabi, UAE"),
    ("Luxury Real Estate Agent Abu Dhabi", "Abu Dhabi, UAE"),
    ("Yacht Broker Abu Dhabi", "Abu Dhabi, UAE"),
    ("Private Jet Charter Abu Dhabi", "Abu Dhabi, UAE"),
    ("Luxury Interior Designer Abu Dhabi", "Abu Dhabi, UAE"),

    # Saudi Arabia
    ("Luxury Real Estate Agent Riyadh", "Riyadh, Saudi Arabia"),
    ("Private Wealth Manager Riyadh", "Riyadh, Saudi Arabia"),
    ("Luxury Car Dealer Riyadh", "Riyadh, Saudi Arabia"),
    ("VIP Event Planner Riyadh", "Riyadh, Saudi Arabia"),
    ("Luxury Real Estate Jeddah", "Jeddah, Saudi Arabia"),
    ("Yacht Broker Jeddah", "Jeddah, Saudi Arabia"),

    # Qatar
    ("Luxury Real Estate Agent Doha", "Doha, Qatar"),
    ("Private Wealth Manager Doha", "Doha, Qatar"),
    ("Luxury Interior Designer Doha", "Doha, Qatar"),
    ("VIP Concierge Doha", "Doha, Qatar"),

    # Bahrain/Kuwait/Oman
    ("Luxury Real Estate Bahrain", "Manama, Bahrain"),
    ("Private Wealth Advisor Kuwait City", "Kuwait City, Kuwait"),
    ("Luxury Real Estate Muscat", "Muscat, Oman"),
]


def run_apify_query(query, location):
    """Run one Apify Google Maps query and return leads."""
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

        # Wait for completion (max 3 min)
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

        # Fetch results
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
            domain = ""
            if website:
                try:
                    domain = urlparse(website).netloc.replace("www.", "")
                except Exception:
                    pass

            # Try to get a real name from the place
            first_name = title.split()[0] if title.split() else title
            last_name = " ".join(title.split()[1:]) if len(title.split()) > 1 else ""

            name_full = f"{first_name} {last_name}".strip()
            if is_duplicate(phone, name_full):
                continue

            leads.append({
                "First Name": first_name,
                "Last Name": last_name,
                "Role": "Luxury Service Provider / HNI Contact",
                "Company": title,
                "Domain": domain,
                "Phone Number": phone,
                "Email": f"info@{domain}" if domain else "",
                "City/Country": location,
                "Deliverability Status": "Pending Verification",
                "Full Address": address,
                "Website": website,
                "Source": "Apify Google Maps - Contact Hunter",
                "Phone Type": classify_phone(phone),
            })

    except Exception as e:
        print(f"  [!] Apify error: {e}")

    return leads


# ---------------------------------------------------------------------------
# TAVILY - Direct mobile number dorking
# ---------------------------------------------------------------------------
TAVILY_MOBILE_DORKS = [
    # UAE mobiles - founder/CEO personal numbers
    'site:linkedin.com/in/ "Dubai" "Founder" ("+971 50" OR "+971 52" OR "+971 54" OR "+971 55" OR "+971 58")',
    'site:linkedin.com/in/ "Abu Dhabi" "CEO" ("+971 50" OR "+971 52" OR "+971 55")',
    'site:linkedin.com/in/ "Dubai" "Managing Director" ("+971 50" OR "+971 52" OR "+971 55")',
    'site:linkedin.com/in/ "DIFC" "Partner" ("+971 50" OR "+971 55")',

    # Contact pages with personal mobiles
    '"contact" "Dubai" "+971 50" "luxury"',
    '"contact" "Dubai" "+971 55" "private"',
    '"contact" "Abu Dhabi" "+971 50" "wealth"',
    '"whatsapp" "Dubai" "+971 50"',
    '"whatsapp" "Dubai" "+971 55"',
    '"whatsapp" "Dubai" "+971 52" "real estate"',

    # Real estate agents (high value, always list personal mobiles)
    '"real estate" "Dubai" "+971 50" "broker"',
    '"real estate" "Dubai" "+971 55" "agent"',
    '"property" "Dubai Marina" "+971 50"',
    '"property" "Palm Jumeirah" "+971 50"',
    '"property" "Downtown Dubai" "+971 55"',
    '"villa" "Dubai" "+971 50" "sale"',
    '"penthouse" "Dubai" "+971 52"',

    # Luxury services
    '"yacht" "Dubai" "+971 50"',
    '"private jet" "Dubai" "+971 55"',
    '"luxury car" "Dubai" "+971 50"',
    '"bespoke" "Dubai" "+971 55"',
    '"concierge" "Dubai" "+971 50"',

    # Saudi mobiles
    'site:linkedin.com/in/ "Riyadh" "CEO" ("+966 50" OR "+966 55" OR "+966 54")',
    '"contact" "Riyadh" "+966 50" "luxury"',
    '"real estate" "Riyadh" "+966 55"',
    '"real estate" "Jeddah" "+966 50"',

    # Qatar
    '"contact" "Doha" "+974 33" "luxury"',
    '"real estate" "Doha" "+974 55"',
    'site:linkedin.com/in/ "Doha" "CEO" "+974"',

    # Business cards / vCards / contact directories
    'filetype:vcf "Dubai" "+971 5"',
    '"vcard" "Dubai" "+971 50"',
    '"business card" "Dubai" "+971 55"',

    # WhatsApp groups and directories
    '"whatsapp" "+971 50" "luxury" "Dubai"',
    '"whatsapp" "+971 55" "VIP" "Dubai"',
    '"call us" "+971 50" "Dubai" "luxury"',
    '"call us" "+971 55" "Dubai" "private"',

    # Real estate portals with agent numbers
    'site:bayut.com "+971 50"',
    'site:propertyfinder.ae "+971 55"',
    'site:dubizzle.com "+971 50" "luxury"',
    'site:bayut.com "+971 55" "villa"',

    # Networking / events
    '"networking" "Dubai" "+971 50" "CEO"',
    '"speaker" "Dubai" "+971 55" "founder"',
]


def tavily_search(query):
    """Search Tavily and extract phone numbers from results."""
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
            content = (r.get("content", "") + " " + r.get("raw_content", ""))[:5000]
            title = r.get("title", "")
            url = r.get("url", "")

            # Extract phone numbers
            phones = extract_phones_from_text(content)
            if not phones:
                continue

            # Try to extract names
            # Look for patterns like "Name - Title" or "Name, Title"
            name_match = re.search(r'([A-Z][a-z]+)\s+([A-Z][a-z]+)', title)
            first = name_match.group(1) if name_match else ""
            last = name_match.group(2) if name_match else ""

            # If no name from title, try content
            if not first:
                name_in_content = re.search(r'([A-Z][a-z]{2,})\s+([A-Z][a-z]{2,})', content[:500])
                if name_in_content:
                    first = name_in_content.group(1)
                    last = name_in_content.group(2)

            domain = ""
            if url:
                try:
                    domain = urlparse(url).netloc.replace("www.", "")
                except Exception:
                    pass

            # Determine location from content
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

            for phone in phones[:3]:  # Max 3 per result
                name_full = f"{first} {last}".strip()
                if is_duplicate(phone, name_full):
                    continue

                leads.append({
                    "First Name": first if first else "Contact",
                    "Last Name": last if last else title[:30],
                    "Role": "HNI / Luxury Contact",
                    "Company": title[:80],
                    "Domain": domain,
                    "Phone Number": phone,
                    "Email": "",
                    "City/Country": location,
                    "Deliverability Status": "Pending",
                    "Full Address": "",
                    "Website": url,
                    "Source": "Tavily Mobile Dork",
                    "Phone Type": classify_phone(phone),
                })

    except Exception as e:
        print(f"  [!] Tavily error: {e}")

    return leads


# ---------------------------------------------------------------------------
# Safe Excel/CSV writer with file locking
# ---------------------------------------------------------------------------
def save_all_leads():
    """Consolidate and save all leads to HNI.xlsx + CSV."""
    global ALL_LEADS

    if not ALL_LEADS:
        print("[!] No leads to save")
        return 0

    new_df = pd.DataFrame(ALL_LEADS)

    # Try to read existing data
    existing_dfs = []
    if HNI_XLSX.exists():
        try:
            existing_dfs.append(pd.read_excel(str(HNI_XLSX)))
        except Exception:
            pass
    if HNI_CSV.exists():
        try:
            existing_dfs.append(pd.read_csv(str(HNI_CSV)))
        except Exception:
            pass

    if existing_dfs:
        combined = pd.concat(existing_dfs + [new_df], ignore_index=True)
    else:
        combined = new_df

    # Dedup on phone number
    combined = combined.drop_duplicates(subset=["Phone Number"], keep="first")
    # Remove rows with no phone
    combined = combined[combined["Phone Number"].notna() & (combined["Phone Number"] != "")]

    total = len(combined)

    # Write with retries
    for attempt in range(15):
        try:
            combined.to_excel(str(HNI_XLSX), index=False, engine="openpyxl")
            break
        except PermissionError:
            if attempt < 14:
                time.sleep(2)
            else:
                print(f"[!] Could not write to HNI.xlsx after 15 attempts")

    # Also write CSV backup
    for attempt in range(5):
        try:
            combined.to_csv(str(HNI_CSV), index=False, encoding="utf-8")
            break
        except PermissionError:
            time.sleep(1)

    return total


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
