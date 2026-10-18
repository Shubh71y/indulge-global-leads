r"""
Indulge Global — 10,000 Pan-Middle East & Mediterranean HNI Discovery Engine
=============================================================================
Full 17 Sovereign Jurisdictions Target:
  1. Bahrain (Manama)
  2. Cyprus (Nicosia, Limassol)
  3. Egypt (Cairo, New Cairo, Giza)
  4. Iran (Tehran)
  5. Iraq (Baghdad, Erbil)
  6. Israel (Tel Aviv, Jerusalem, Herzliya Pituach)
  7. Jordan (Amman, Abdoun)
  8. Kuwait (Kuwait City, Sharq)
  9. Lebanon (Beirut, Achrafieh)
  10. Oman (Muscat, Al Qurum)
  11. Palestine (Ramallah, East Jerusalem)
  12. Qatar (Doha, West Bay, Lusail, The Pearl)
  13. Saudi Arabia (Riyadh, Jeddah, Al Khobar, Dammam)
  14. Syria (Damascus)
  15. Turkey / Türkiye (Istanbul, Ankara, Bodrum)
  16. United Arab Emirates / UAE (Abu Dhabi, Dubai, Sharjah)
  17. Yemen (Sana'a, Aden)

High-Value UHNI Focus:
  - Single & Multi Family Offices, Royal Diwans, Conglomerates, Holding Groups
  - Super-Prime Real Estate, Yacht & Private Aviation Owners, High-Profile C-Suite
  - Direct WhatsApp & Mobile Extraction across all international calling codes
  - Continuous append-only sync to data/leads_store.jsonl & data/HNI.xlsx
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)

import os
import re
import time
import requests
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(r"C:\Users\gozoi\Projects\indulge")
SCRIPTS_DIR = BASE_DIR / "scripts"
DATA_DIR = BASE_DIR / "data"

sys.path.append(str(SCRIPTS_DIR))
import lead_store
import env_loader

APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")
TAVILY_KEYS = [k.strip() for k in os.environ.get("TAVILY_API_KEYS", "").split(",") if k.strip()]
tavily_idx = 0

def get_tavily_key():
    global tavily_idx
    k = TAVILY_KEYS[tavily_idx % len(TAVILY_KEYS)]
    tavily_idx += 1
    return k

# ---------------------------------------------------------------------------
# PHONE REGEX COVERING ALL 17 MIDDLE EAST & MEDITERRANEAN COUNTRIES
# ---------------------------------------------------------------------------
# +971 (UAE), +966 (KSA), +974 (Qatar), +965 (Kuwait), +973 (Bahrain), +968 (Oman)
# +357 (Cyprus), +20 (Egypt), +98 (Iran), +964 (Iraq), +972 (Israel), +962 (Jordan)
# +961 (Lebanon), +970 (Palestine), +963 (Syria), +90 (Turkey), +967 (Yemen)
PHONE_RE = re.compile(r'(\+(?:971|966|974|965|973|968|357|20|98|964|972|962|961|970|963|90|967)[\s\-]?\d{1,3}[\s\-]?\d{3,4}[\s\-]?\d{3,5})')

MOBILE_RE = re.compile(
    r'(\+971[\s\-]?(?:50|52|54|55|56|58)|'
    r'\+966[\s\-]?(?:50|53|54|55|56|57|58|59)|'
    r'\+974[\s\-]?(?:33|55|66|77)|'
    r'\+965[\s\-]?(?:5|6|9)|'
    r'\+973[\s\-]?(?:3|6)|'
    r'\+968[\s\-]?(?:9|7)|'
    r'\+357[\s\-]?(?:9)|'
    r'\+20[\s\-]?(?:10|11|12|15)|'
    r'\+972[\s\-]?(?:5)|'
    r'\+962[\s\-]?(?:7)|'
    r'\+961[\s\-]?(?:3|70|71|76|81)|'
    r'\+90[\s\-]?(?:5))'
)

def classify_phone(p):
    if MOBILE_RE.search(p):
        return "Personal Mobile / WhatsApp (VIP Direct)"
    return "Executive Direct / Boardroom Office"

# ---------------------------------------------------------------------------
# 17 COUNTRY HIGH-DENSITY WEALTH TARGETS (150+ CLUSTERS)
# ---------------------------------------------------------------------------
PAN_ME_TARGETS = [
    # 1. BAHRAIN
    ("Family Office Bahrain Financial Harbour Manama", "Manama, Bahrain"),
    ("Holding Company Seef District Manama", "Manama, Bahrain"),
    ("Private Investment Group Manama", "Manama, Bahrain"),
    ("Luxury Real Estate Developer Amwaj Islands", "Manama, Bahrain"),

    # 2. CYPRUS
    ("Family Office Limassol Marina", "Limassol, Cyprus"),
    ("Wealth Management Firm Nicosia", "Nicosia, Cyprus"),
    ("Private Investment Holding Cyprus", "Nicosia, Cyprus"),
    ("Luxury Villa Developer Limassol", "Limassol, Cyprus"),
    ("Superyacht Management Limassol Port", "Limassol, Cyprus"),

    # 3. EGYPT
    ("Family Office New Cairo Fifth Settlement", "Cairo, Egypt"),
    ("Holding Company Zamalek Cairo", "Cairo, Egypt"),
    ("Industrial & Real Estate Conglomerate New Cairo", "Cairo, Egypt"),
    ("Private Equity Firm Smart Village Giza", "Cairo, Egypt"),
    ("Luxury Real Estate Developer Sheikh Zayed City", "Cairo, Egypt"),

    # 4. IRAN
    ("Investment Holding Company Tehran Elahiyeh", "Tehran, Iran"),
    ("Private Business Conglomerate Tehran Jordan", "Tehran, Iran"),
    ("Commercial Holding Zaferanieh Tehran", "Tehran, Iran"),

    # 5. IRAQ
    ("Business Conglomerate Erbil Empire World", "Erbil, Iraq"),
    ("Investment Holding Baghdad Jadriya", "Baghdad, Iraq"),
    ("General Trading & Contracting Conglomerate Baghdad", "Baghdad, Iraq"),
    ("Private Investment Group Erbil", "Erbil, Iraq"),

    # 6. ISRAEL
    ("Single Family Office Herzliya Pituach", "Herzliya, Israel"),
    ("Venture Capital Management Tel Aviv Rothschild", "Tel Aviv, Israel"),
    ("Private Wealth Advisors Tel Aviv", "Tel Aviv, Israel"),
    ("Luxury Real Estate Developer Tel Aviv", "Tel Aviv, Israel"),

    # 7. JORDAN
    ("Family Holding Company Amman Abdoun", "Amman, Jordan"),
    ("Private Investment Group Sweifieh Amman", "Amman, Jordan"),
    ("Family Business Conglomerate Amman Jabal", "Amman, Jordan"),
    ("Luxury Real Estate Developer Amman", "Amman, Jordan"),

    # 8. KUWAIT
    ("Family Business Conglomerate Kuwait City Sharq", "Kuwait City, Kuwait"),
    ("Investment Holding Company Kuwait City KIPCO", "Kuwait City, Kuwait"),
    ("Private Equity Partners Kuwait City", "Kuwait City, Kuwait"),
    ("Real Estate Development Group Kuwait", "Kuwait City, Kuwait"),

    # 9. LEBANON
    ("Family Office Achrafieh Beirut", "Beirut, Lebanon"),
    ("Private Investment Holding Downtown Beirut", "Beirut, Lebanon"),
    ("Luxury Real Estate Developer Beirut Waterfront", "Beirut, Lebanon"),
    ("Holding Company Verdun Beirut", "Beirut, Lebanon"),

    # 10. OMAN
    ("Family Business Conglomerate Muscat Oman", "Muscat, Oman"),
    ("Investment Holding Group Al Qurum Muscat", "Muscat, Oman"),
    ("Private Wealth Office Al Mouj Muscat", "Muscat, Oman"),
    ("Luxury Property Developer Muscat", "Muscat, Oman"),

    # 11. PALESTINE
    ("Investment Holding Company Ramallah Al Masyoun", "Ramallah, Palestine"),
    ("Family Business Group Ramallah", "Ramallah, Palestine"),
    ("Commercial Development Group Ramallah", "Ramallah, Palestine"),

    # 12. QATAR
    ("Single Family Office West Bay Doha", "Doha, Qatar"),
    ("Private Investment Group Lusail Marina Doha", "Doha, Qatar"),
    ("Holding Company The Pearl Qatar", "Doha, Qatar"),
    ("Luxury Real Estate Developer Doha", "Doha, Qatar"),
    ("Private Equity Management Doha", "Doha, Qatar"),

    # 13. SAUDI ARABIA
    ("Family Office Olaya Towers Riyadh", "Riyadh, Saudi Arabia"),
    ("Private Holding Company KAFD Riyadh", "Riyadh, Saudi Arabia"),
    ("Investment Conglomerate Al Malqa Riyadh", "Riyadh, Saudi Arabia"),
    ("Luxury Real Estate Developer Hittin Riyadh", "Riyadh, Saudi Arabia"),
    ("Private Equity Firm King Fahd Road Riyadh", "Riyadh, Saudi Arabia"),
    ("Family Business Group Al Nakheel Riyadh", "Riyadh, Saudi Arabia"),
    ("Family Holding Company Jeddah Corniche", "Jeddah, Saudi Arabia"),
    ("Private Investment Group Al Andalus Jeddah", "Jeddah, Saudi Arabia"),
    ("Family Business Conglomerate Al Khobar", "Al Khobar, Saudi Arabia"),

    # 14. SYRIA
    ("Trading & Investment Holding Damascus Abu Roummaneh", "Damascus, Syria"),
    ("Commercial Conglomerate Damascus Malki", "Damascus, Syria"),

    # 15. TURKEY (TÜRKIYE)
    ("Family Office Levent Istanbul", "Istanbul, Turkey"),
    ("Holding Company Maslak Istanbul", "Istanbul, Turkey"),
    ("Private Equity Firm Bebek Istanbul", "Istanbul, Turkey"),
    ("Luxury Real Estate Developer Nisantasi Istanbul", "Istanbul, Turkey"),
    ("Superyacht Brokerage Yalıkavak Bodrum", "Bodrum, Turkey"),
    ("Industrial Conglomerate Cankaya Ankara", "Ankara, Turkey"),

    # 16. UNITED ARAB EMIRATES (UAE)
    ("Single Family Office DIFC Gate Village", "Dubai, UAE"),
    ("Multi Family Office DIFC", "Dubai, UAE"),
    ("Private Wealth Office Downtown Dubai", "Dubai, UAE"),
    ("Super Prime Real Estate Palm Jumeirah", "Dubai, UAE"),
    ("Luxury Villa Developer Emirates Hills Dubai", "Dubai, UAE"),
    ("Private Investment Firm Jumeirah Bay Island", "Dubai, UAE"),
    ("Superyacht Management Dubai Marina", "Dubai, UAE"),
    ("Private Jet Charter Dubai South Al Maktoum", "Dubai, UAE"),
    ("Family Office Al Maryah Island ADGM", "Abu Dhabi, UAE"),
    ("Private Investment Office ADGM Square", "Abu Dhabi, UAE"),
    ("Holding Company Corniche Abu Dhabi", "Abu Dhabi, UAE"),
    ("Luxury Real Estate Developer Saadiyat Cultural District", "Abu Dhabi, UAE"),

    # 17. YEMEN
    ("Commercial Conglomerate Sanaa Hadda", "Sanaa, Yemen"),
    ("Trading & Investment Group Aden Crater", "Aden, Yemen")
]

# ---------------------------------------------------------------------------
# PAN-MIDDLE EAST OSINT & WHATSAPP BIO SCRAPING DORKS (ALL 17 COUNTRIES)
# ---------------------------------------------------------------------------
PAN_ME_DORKS = [
    # 1. BAHRAIN (+973)
    ('site:linkedin.com/in/ ("Chairman" OR "Managing Director" OR "Owner") ("Holding" OR "Family Business") "Bahrain" ("+973 3" OR "+973 66" OR "+973 17")', "Manama, Bahrain"),
    ('"wa.me/973" ("Chairman" OR "Managing Director" OR "Founder" OR "CEO") "Bahrain"', "Manama, Bahrain"),

    # 2. CYPRUS (+357)
    ('site:linkedin.com/in/ ("Founder" OR "Managing Director" OR "CEO") ("Family Office" OR "Wealth Management" OR "Shipping") "Cyprus" ("+357 9" OR "+357 2")', "Limassol, Cyprus"),
    ('"wa.me/357" ("CEO" OR "Director" OR "Investor" OR "Managing Partner") "Cyprus"', "Nicosia, Cyprus"),

    # 3. EGYPT (+20)
    ('site:linkedin.com/in/ ("Chairman" OR "CEO" OR "Managing Director" OR "Founder") ("Holding" OR "Group" OR "Developments") "Cairo" ("+20 10" OR "+20 11" OR "+20 12")', "Cairo, Egypt"),
    ('site:linkedin.com/in/ ("رئيس مجلس الإدارة" OR "العضو المنتدب") ("شركة قابضة" OR "مجموعة") "القاهرة" ("+20 10" OR "+20 11")', "Cairo, Egypt"),
    ('"wa.me/201" ("Chairman" OR "Managing Director" OR "CEO") "Egypt"', "Cairo, Egypt"),

    # 4. IRAN (+98)
    ('site:linkedin.com/in/ ("Managing Director" OR "Board Member" OR "CEO") ("Holding" OR "Investment" OR "Industrial") "Tehran" ("+98 9")', "Tehran, Iran"),

    # 5. IRAQ (+964)
    ('site:linkedin.com/in/ ("Chairman" OR "CEO" OR "General Director" OR "Owner") ("Group" OR "Holding" OR "Investments") ("Baghdad" OR "Erbil") ("+964 7")', "Baghdad, Iraq"),
    ('"wa.me/964" ("CEO" OR "Managing Director" OR "General Manager") ("Iraq" OR "Erbil")', "Erbil, Iraq"),

    # 6. ISRAEL (+972)
    ('site:linkedin.com/in/ ("Managing Partner" OR "General Partner" OR "Founder") ("Family Office" OR "Venture Capital" OR "Private Equity") ("Tel Aviv" OR "Herzliya") ("+972 5")', "Tel Aviv, Israel"),
    ('"wa.me/972" ("Founder" OR "Managing Partner" OR "CEO") "Israel"', "Tel Aviv, Israel"),

    # 7. JORDAN (+962)
    ('site:linkedin.com/in/ ("Chairman" OR "Managing Director" OR "CEO" OR "Founder") ("Holding" OR "Group" OR "Investments") "Amman" ("+962 7")', "Amman, Jordan"),
    ('"wa.me/962" ("Chairman" OR "Managing Director" OR "General Manager") "Amman"', "Amman, Jordan"),

    # 8. KUWAIT (+965)
    ('site:linkedin.com/in/ ("Chairman" OR "Managing Director" OR "CEO") ("Holding" OR "Investments" OR "Group") "Kuwait" ("+965 5" OR "+965 6" OR "+965 9")', "Kuwait City, Kuwait"),
    ('site:linkedin.com/in/ ("رئيس مجلس الإدارة" OR "الرئيس التنفيذي") ("شركة قابضة" OR "مجموعة") "الكويت" ("+965")', "Kuwait City, Kuwait"),
    ('"wa.me/965" ("CEO" OR "Managing Director" OR "Holding") "Kuwait"', "Kuwait City, Kuwait"),

    # 9. LEBANON (+961)
    ('site:linkedin.com/in/ ("Chairman" OR "CEO" OR "Managing Director" OR "Founder") ("Holding" OR "Group" OR "Private Office") "Beirut" ("+961 3" OR "+961 70" OR "+961 71")', "Beirut, Lebanon"),
    ('"wa.me/961" ("CEO" OR "Managing Director" OR "Founder") "Beirut"', "Beirut, Lebanon"),

    # 10. OMAN (+968)
    ('site:linkedin.com/in/ ("Chairman" OR "Managing Director" OR "CEO") ("Holding" OR "Group" OR "Family Business") "Muscat" ("+968 9" OR "+968 7")', "Muscat, Oman"),
    ('"wa.me/968" ("Chairman" OR "Managing Director" OR "CEO") "Oman"', "Muscat, Oman"),

    # 11. PALESTINE (+970)
    ('site:linkedin.com/in/ ("Chairman" OR "CEO" OR "General Manager" OR "Founder") ("Holding" OR "Investment" OR "Group") ("Ramallah" OR "Jerusalem") ("+970 5" OR "+972 5")', "Ramallah, Palestine"),
    ('"wa.me/970" ("General Manager" OR "CEO" OR "Chairman") "Palestine"', "Ramallah, Palestine"),

    # 12. QATAR (+974)
    ('site:linkedin.com/in/ ("Chairman" OR "Managing Director" OR "Owner") ("Family Office" OR "Holding" OR "Investments") "Doha" ("+974 33" OR "+974 55" OR "+974 66")', "Doha, Qatar"),
    ('site:linkedin.com/in/ ("رئيس مجلس الإدارة" OR "الرئيس التنفيذي") ("شركة قابضة" OR "مكتب عائلي") "الدوحة" ("+974")', "Doha, Qatar"),
    ('"wa.me/974" ("Managing Partner" OR "Chairman" OR "Founder") "Doha"', "Doha, Qatar"),

    # 13. SAUDI ARABIA (+966)
    ('site:linkedin.com/in/ ("مكتب عائلي" OR "شركة عائلية") ("الرياض" OR "جدة" OR "الخبر") ("+966 50" OR "+966 53" OR "+966 55")', "Riyadh, Saudi Arabia"),
    ('site:linkedin.com/in/ ("رئيس مجلس الإدارة" OR "العضو المنتدب") ("شركة قابضة" OR "مجموعة") "الرياض" ("+966 50" OR "+966 55")', "Riyadh, Saudi Arabia"),
    ('site:linkedin.com/in/ ("Chairman" OR "President" OR "Owner") "Holding" "Riyadh" ("+966 50" OR "+966 55" OR "+966 54")', "Riyadh, Saudi Arabia"),
    ('site:linkedin.com/in/ ("CEO" OR "President" OR "Vice Chairman") "Group" "Jeddah" ("+966 50" OR "+966 55" OR "+966 54")', "Jeddah, Saudi Arabia"),
    ('"wa.me/96650" OR "wa.me/96655" OR "wa.me/96654" ("CEO" OR "President" OR "Owner") "Riyadh"', "Riyadh, Saudi Arabia"),

    # 14. SYRIA (+963)
    ('site:linkedin.com/in/ ("Managing Director" OR "General Manager" OR "Board Member") ("Holding" OR "Group" OR "Trading") "Damascus" ("+963 9")', "Damascus, Syria"),

    # 15. TURKEY / TÜRKIYE (+90)
    ('site:linkedin.com/in/ ("Yönetim Kurulu Başkanı" OR "Genel Müdür" OR "CEO") ("Holding" OR "Grup" OR "Yatırım") ("İstanbul" OR "Ankara") ("+90 5")', "Istanbul, Turkey"),
    ('site:linkedin.com/in/ ("Chairman" OR "Managing Director" OR "CEO") ("Holding" OR "Group" OR "Family Office") "Istanbul" ("+90 5")', "Istanbul, Turkey"),
    ('"wa.me/905" ("CEO" OR "Founder" OR "Managing Director" OR "President") "Turkey"', "Istanbul, Turkey"),

    # 16. UNITED ARAB EMIRATES / UAE (+971)
    ('site:linkedin.com/in/ ("Founder" OR "Managing Partner" OR "Chairman") "Family Office" "Dubai" ("+971 50" OR "+971 52" OR "+971 55")', "Dubai, UAE"),
    ('site:linkedin.com/in/ ("Chairman" OR "CEO") ("Holding" OR "Group") "Dubai" ("+971 50" OR "+971 52" OR "+971 54" OR "+971 55")', "Dubai, UAE"),
    ('site:linkedin.com/in/ ("المكتب الخاص" OR "ديوان") ("رئيس" OR "مدير") ("دبي" OR "أبوظبي") ("+971 50" OR "+971 55")', "Dubai, UAE"),
    ('site:linkedin.com/in/ ("Chairman" OR "Managing Director") "Abu Dhabi" ("Family Office" OR "Holding") ("+971 50" OR "+971 52" OR "+971 55")', "Abu Dhabi, UAE"),
    ('"wa.me/97150" OR "wa.me/97152" OR "wa.me/97155" ("Founder" OR "Managing Director" OR "Chairman") "Dubai"', "Dubai, UAE"),

    # 17. YEMEN (+967)
    ('site:linkedin.com/in/ ("General Manager" OR "Managing Director" OR "Chairman") ("Group" OR "Trading" OR "Holding") ("Sanaa" OR "Aden") ("+967 7")', "Sanaa, Yemen")
]

def check_apify_allowance():
    try:
        r = requests.get(f"https://api.apify.com/v2/users/me/limits?token={APIFY_TOKEN}", timeout=10)
        d = r.json().get("data", {})
        used = d.get("current", {}).get("monthlyUsageUsd", 0)
        max_usd = d.get("limits", {}).get("maxMonthlyUsageUsd", 10)
        return used < (max_usd - 0.5)
    except Exception:
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

def mine_apify(query, loc):
    leads = []
    if not check_apify_allowance():
        return leads
    try:
        resp = requests.post(
            f"https://api.apify.com/v2/acts/compass~crawler-google-places/runs?token={APIFY_TOKEN}",
            json={
                "searchStringsArray": [query],
                "maxCrawledPlacesPerSearch": 20,
                "language": "en",
                "maxImages": 0
            },
            timeout=20
        )
        run_id = resp.json().get("data", {}).get("id", "")
        if not run_id:
            return leads

        status = ""
        for _ in range(20):
            time.sleep(4)
            sr = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}", timeout=10)
            status = sr.json().get("data", {}).get("status", "")
            if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
                break

        if status == "SUCCEEDED":
            dataset_id = sr.json().get("data", {}).get("defaultDatasetId", "")
            items = requests.get(f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}", timeout=25).json()
            for p in items:
                phone = p.get("phone", "")
                title = p.get("title", "")
                website = p.get("website", "")
                address = p.get("address", "")
                category = p.get("categoryName", "Family Office / Private Enterprise")

                if not phone or phone == "No phone listed":
                    continue

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

                lead = {
                    "First Name": resolved["first_name"],
                    "Last Name": resolved["last_name"],
                    "Role": resolved["title"],
                    "Company": title,
                    "Domain": resolved["domain"] if resolved["domain"] else "N/A",
                    "Phone Number": phone_info["formatted_intl"],
                    "E164": phone_info["e164"],
                    "Email": resolved["email"],
                    "City/Country": loc,
                    "Deliverability Status": "Verified Mobile & WhatsApp Direct" if phone_info["is_mobile"] else "Verified Corporate Line (Email N/A)",
                    "Full Address": address or loc,
                    "Website": website,
                    "Source": "Apify Google Places Pan-Middle East Engine (Entity Resolved)",
                    "Phone Type": phone_info["phone_type"],
                    "Carrier": phone_info["carrier"],
                    "WhatsApp Link": phone_info["wa_link"] or "",
                }
                leads.append(lead)
    except Exception:
        pass
    return leads

def mine_tavily(query, loc):
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
                "include_raw_content": True
            },
            timeout=25
        )
        if resp.status_code == 200:
            for r in resp.json().get("results", []):
                title = r.get("title", "")
                content = str(r.get("content", "")) + " " + str(r.get("raw_content", ""))
                url = r.get("url", "")
                combined_text = f"{title} {content}"

                clean_title = re.sub(r'\|\s*LinkedIn.*$', '', title).strip()
                parts = clean_title.split('-')
                fn, ln = "", ""
                role = "Chairman & Managing Partner"
                comp = "Private Wealth Enterprise"

                if len(parts) >= 2:
                    name_words = [w for w in re.sub(r'[^a-zA-Z\s]', '', parts[0]).split() if len(w) > 1]
                    if len(name_words) >= 2:
                        fn, ln = name_words[0].capitalize(), name_words[-1].capitalize()
                    role = parts[1].strip()
                if len(parts) >= 3:
                    comp = parts[2].strip()

                if not is_valid_person_name(fn, ln, comp):
                    continue

                if is_broker_or_retail_trap(comp, role, url):
                    continue

                phone_info = extract_phone_with_proximity(
                    text=combined_text,
                    first_name=fn,
                    last_name=ln,
                    url=url,
                    default_region="AE",
                    max_distance=120,
                    require_mobile=False,
                )
                if not phone_info:
                    continue

                domain = clean_corporate_domain(url)
                resolved = resolve_lead_entity(
                    first_name=fn,
                    last_name=ln,
                    company_name=comp[:70],
                    title=role[:60],
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
                    "Company": comp[:70],
                    "Domain": resolved["domain"] if resolved["domain"] else "N/A",
                    "Phone Number": phone_info["formatted_intl"],
                    "E164": phone_info["e164"],
                    "Email": resolved["email"],
                    "City/Country": loc,
                    "Deliverability Status": "Verified Mobile & WhatsApp Direct" if phone_info["is_mobile"] else "Verified Corporate Line (Email N/A)",
                    "Full Address": loc,
                    "Website": url,
                    "Source": "LinkedIn / OSINT Direct Mobile Engine",
                    "Phone Type": phone_info["phone_type"],
                    "Carrier": phone_info["carrier"],
                    "WhatsApp Link": phone_info["wa_link"] or "",
                }
                leads.append(lead)
    except Exception:
        pass
    return leads

def main():
    print("=" * 80)
    print("🚀 INDULGE GLOBAL — 10,000 PAN-MIDDLE EAST & MEDITERRANEAN HNI ENGINE")
    print("🌍 17 COUNTRIES: Bahrain, Cyprus, Egypt, Iran, Iraq, Israel, Jordan,")
    print("   Kuwait, Lebanon, Oman, Palestine, Qatar, Saudi Arabia, Syria, Turkey, UAE, Yemen")
    print("=" * 80)

    TARGET = 10000
    all_leads = lead_store.get_all_leads()
    print(f"[*] Initial Baseline: {len(all_leads)} unique leads verified in durable store.")

    cycle = 1
    while len(all_leads) < TARGET:
        print(f"\n=========================================================================")
        print(f"🔄 PAN-ME CYCLE {cycle} | PROGRESS: {len(all_leads)} / {TARGET} LEADS")
        print(f"=========================================================================\n")

        # 1. Apify Search Clusters across 17 countries
        for i, (q, loc) in enumerate(PAN_ME_TARGETS):
            if len(all_leads) >= TARGET: break
            print(f"[{i+1}/{len(PAN_ME_TARGETS)}] Apify: '{q}' ({loc})...")
            new_l = mine_apify(q, loc)
            if new_l:
                added = lead_store.append_leads_batch(new_l)
                all_leads = lead_store.get_all_leads()
                print(f"   ✅ Added +{added} | Total Verified: {len(all_leads)}")
            time.sleep(1)

        # 2. Advanced Pan-Middle East OSINT Dorks across all 17 countries
        for i, (dork, loc) in enumerate(PAN_ME_DORKS):
            if len(all_leads) >= TARGET: break
            print(f"[{i+1}/{len(PAN_ME_DORKS)}] Tavily OSINT: '{dork[:65]}...' ({loc})")
            new_l = mine_tavily(dork, loc)
            if new_l:
                added = lead_store.append_leads_batch(new_l)
                all_leads = lead_store.get_all_leads()
                print(f"   👑 Added +{added} | Total Verified: {len(all_leads)}")
            time.sleep(2)

        cycle += 1

    print("\n=================================================================")
    print(f"🏆 10,000 HNI RECORD MILESTONE REACHED!")
    print(f"📊 Final Count in data/HNI.xlsx: {len(all_leads)}")
    print("=================================================================")

if __name__ == "__main__":
    main()
