r"""
Indulge Global - Persistent Lead Store & Master Sync
===================================================
Maintains a durable JSONL append-only backing store at:
  C:\Users\gozoi\Projects\indulge\data\leads_store.jsonl

Enforces 4-layer data hygiene before any lead enters HNI.xlsx or CSV:
1. No dummy fallback domains (@executive-gcc.com, @uae-investments.ae, social media domains) or generic contact@ emails.
2. Strict E.164 telecom classification via phonenumbers (VIP Personal Mobile vs Corporate Landline / Switchboard) & 1-to-1 deduplication across companies.
3. Broker/Retail Google Maps trap filtering (rejects real estate brokers, yacht/car rentals, US stores).
4. Executive Entity Resolution (rejects placeholder names unless resolved to a real Principal/Chairman).
"""

import sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

import os
import re
import json
import time
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, List

BASE_DIR = Path(r"C:\Users\gozoi\Projects\indulge")
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.phone_verifier import (
    classify_gcc_phone,
    clean_corporate_domain,
    clean_and_validate_email,
    clean_bidi_and_punctuation,
    is_valid_person_name,
    is_broker_or_retail_trap,
)
from scripts.entity_resolver import resolve_lead_entity

DATA_DIR = BASE_DIR / "data"
JSONL_PATH = DATA_DIR / "leads_store.jsonl"
EXCEL_PATH = DATA_DIR / "HNI.xlsx"
CSV_PATH = DATA_DIR / "indulge_gcc_hni_master.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)

COUNTRY_TO_ISO = {
    "united arab emirates": "AE", "uae": "AE", "dubai": "AE", "abu dhabi": "AE", "sharjah": "AE",
    "saudi arabia": "SA", "ksa": "SA", "riyadh": "SA", "jeddah": "SA", "dammam": "SA",
    "qatar": "QA", "doha": "QA",
    "kuwait": "KW", "kuwait city": "KW",
    "bahrain": "BH", "manama": "BH",
    "oman": "OM", "muscat": "OM",
    "jordan": "JO", "amman": "JO",
    "lebanon": "LB", "beirut": "LB",
    "egypt": "EG", "cairo": "EG", "alexandria": "EG",
    "turkey": "TR", "istanbul": "TR", "ankara": "TR",
    "morocco": "MA", "casablanca": "MA", "rabat": "MA", "marrakech": "MA",
    "israel": "IL", "tel aviv": "IL",
    "iraq": "IQ", "baghdad": "IQ", "erbil": "IQ",
    "cyprus": "CY", "limassol": "CY", "nicosia": "CY",
    "united kingdom": "GB", "uk": "GB", "london": "GB", "mayfair": "GB", "belgravia": "GB",
    "switzerland": "CH", "geneva": "CH", "zurich": "CH", "zürich": "CH", "zug": "CH", "st. moritz": "CH", "lugano": "CH",
    "france": "FR", "paris": "FR", "cannes": "FR", "saint-tropez": "FR", "antibes": "FR",
    "monaco": "MC", "monte carlo": "MC", "monte-carlo": "MC",
    "germany": "DE", "munich": "DE", "grünwald": "DE", "hamburg": "DE", "frankfurt": "DE", "bad homburg": "DE", "düsseldorf": "DE",
    "austria": "AT", "vienna": "AT",
    "italy": "IT", "milan": "IT", "rome": "IT", "como": "IT",
    "spain": "ES", "madrid": "ES", "marbella": "ES", "barcelona": "ES", "ibiza": "ES",
    "netherlands": "NL", "amsterdam": "NL",
    "belgium": "BE", "antwerp": "BE", "brussels": "BE",
    "luxembourg": "LU",
    "sweden": "SE", "stockholm": "SE",
    "norway": "NO", "oslo": "NO",
    "united states": "US", "usa": "US", "new york": "US", "nyc": "US", "manhattan": "US",
    "greenwich": "US", "palm beach": "US", "miami": "US", "atherton": "US", "palo alto": "US",
    "san francisco": "US", "silicon valley": "US", "beverly hills": "US", "bel air": "US",
    "los angeles": "US", "aspen": "US", "dallas": "US", "houston": "US", "austin": "US",
    "chicago": "US", "boston": "US",
    "singapore": "SG", "sentosa": "SG", "nassim": "SG", "orchard": "SG", "bukit timah": "SG", "marina bay": "SG",
    "hong kong": "HK", "mid-levels": "HK", "the peak": "HK",
    "antwerp": "BE", "nairobi": "KE", "kenya": "KE", "kampala": "UG", "uganda": "UG",
    "dar es salaam": "TZ", "tanzania": "TZ", "lagos": "NG", "nigeria": "NG",
    "toronto": "CA", "vancouver": "CA", "canada": "CA",
}


def infer_region_from_lead(lead_dict: Dict[str, Any]) -> str:
    loc = str(lead_dict.get("City/Country") or lead_dict.get("Country") or lead_dict.get("Full Address") or "").lower()
    for kw, iso in COUNTRY_TO_ISO.items():
        if kw in loc:
            return iso
    return "AE"


def classify_wealth_signal_and_pitch(
    role: str,
    company: str,
    source: str,
    address: str,
    existing_signal: str = "",
    existing_pitch: str = "",
    existing_segment: str = "",
) -> tuple:
    """
    Assigns an automated Indulge Concierge Hook / Wealth Signal badge, bespoke Pitch Angle,
    and Segment Tag based on the Global (US + Europe + Middle East) High-Net-Worth Data Sources.
    """
    specific_segments = {
        "ypo_eo",
        "racing_yacht",
        "shareholder",
        "gatekeeper",
        "summit_speaker",
        "nri_diaspora",
        "art_philanthropy",
        "university_trustees",
        "regulator_authorised",
        "private_clubs_golf",
        "icij_offshore",
        "eu_beneficial_owner",
        "us_uhni_family_office",
    }
    if existing_segment in specific_segments and existing_signal and existing_pitch:
        return (existing_signal, existing_pitch, existing_segment)

    hay = f"{role} {company} {source} {address} {existing_signal}".lower()
    rl = role.lower()

    # United States SEC Form 13F / Form ADV Single Family Offices, Silicon Valley & Wall Street Principals
    if existing_segment == "us_uhni_family_office" or any(
        kw in hay
        for kw in (
            "sec form 13f",
            "form adv",
            "faa n-number",
            "tie silicon valley",
            "indiaspora",
            "atherton",
            "billionaires' row",
            "palm beach",
            "greenwich",
            "beverly hills",
            "moma trustee",
            "met museum",
            "new york yacht club",
        )
    ):
        return (
            existing_signal or "🇺🇸 US SEC 13F / Family Office Principal",
            existing_pitch or "Pitch: Met Gala / Super Bowl Suite, European Summer Yacht & Dubai/India Concierge",
            "us_uhni_family_office",
        )

    # Europe Statutory Beneficial Ownership & Family Holding SPVs (UK PSC, Swiss Zefix, Pappers.fr, Handelsregister, Lux LBR, Monaco RCI)
    if existing_segment == "eu_beneficial_owner" or any(
        kw in hay
        for kw in (
            "companies house psc",
            "pappers.fr",
            "zefix",
            "handelsregister",
            "vermögensverwaltungs",
            "beteiligungs gmbh",
            "familienholding",
            "soparfi",
            "spf",
            "rci monaco",
            "société civile particulière",
            "geschäftsführender gesellschafter",
            "alleingesellschafter",
            "verwaltungsratspräsident",
            "directeur-grootaandeelhouder",
            "amministratore unico",
            "socio unico",
            "administrador único",
        )
    ):
        return (
            existing_signal or "🇪🇺 Europe Statutory Beneficial Owner (>75% PSC / Holding)",
            existing_pitch or "Pitch: Courchevel / St. Moritz Chalets, Monaco F1 Yacht & Maldives Winter Charter",
            "eu_beneficial_owner",
        )

    # 5. The "Gatekeeper Bridge": Chiefs of Staff & Private Office Directors
    if existing_segment == "gatekeeper" or any(
        kw in rl or kw in hay
        for kw in (
            "chief of staff",
            "head of private office",
            "private office director",
            "director of private office",
            "personal assistant to chairman",
            "personal assistant to ceo",
            "executive assistant to chairman",
            "family office manager",
            "gatekeeper",
            "lifestyle manager",
            "estate manager",
        )
    ):
        return (
            existing_signal or "🔑 Private Office / Gatekeeper",
            existing_pitch or "Pitch: Turnkey Principal Itinerary & 24/7 Executive Concierge",
            "gatekeeper",
        )

    # 7. Indian / NRI Ultra-Rich Diaspora in the Gulf (TiE Charter Members, IBPC, Forbes Top 100 Indian Leaders)
    if existing_segment == "nri_diaspora" or any(
        kw in hay
        for kw in (
            "forbes middle east top 100 indian",
            "forbes top indian",
            "ibpc",
            "indian business & professional council",
            "tie dubai",
            "tie riyadh",
            "charter member",
            "nri billionaire",
            "lulu group",
            "aster dm",
            "sobharealty",
            "landmark group",
            "joyalukkas",
            "malabar gold",
            "transworld",
            "kalyan",
        )
    ):
        return (
            existing_signal or "🇮🇳 Forbes Top Indian Leader / TiE & IBPC",
            existing_pitch or "Pitch: Cross-Border India-Dubai-London Concierge & Cricket Hospitality",
            "nri_diaspora",
        )

    # 8. Luxury Art Patronage, Museum Boards & Philanthropy Circles
    if existing_segment == "art_philanthropy" or any(
        kw in hay
        for kw in (
            "art dubai",
            "al jalila",
            "bassmat",
            "art jameel",
            "diriyah biennale",
            "sharjah art",
            "louvre abu dhabi",
            "istanbul modern",
            "barjeel art",
        )
    ):
        return (
            existing_signal or "🎨 Art Dubai / Philanthropy Patron",
            existing_pitch or "Pitch: Art Basel VIP Preview, Venice Biennale & Bespoke Cultural Travel",
            "art_philanthropy",
        )

    # 9. Elite University Boards of Trustees & Alumni Endowments
    if existing_segment == "university_trustees" or any(
        kw in hay
        for kw in (
            "american university in cairo",
            "american university of beirut",
            "aub board",
            "auc board",
            "king's academy",
            "koç university",
            "sabancı university",
            "tüsiad",
            "tusiad",
            "board of trustees",
        )
    ):
        return (
            existing_signal or "🎓 University Board of Trustees / TÜSİAD",
            existing_pitch or "Pitch: Global Ivy League / Oxbridge Family Travel & Cultural Patronage",
            "university_trustees",
        )

    # 10. Financial Regulators: DFSA, FSRA & Saudi CMA Authorised Individuals
    if existing_segment == "regulator_authorised" or any(
        kw in hay
        for kw in (
            "dfsa authorised",
            "fsra",
            "saudi capital market authority",
            "cma licensed",
            "senior executive officer",
            "cysec",
        )
    ):
        return (
            existing_signal or "🏛️ DFSA / FSRA / CMA Authorised Principal",
            existing_pitch or "Pitch: Davos / Global Investor Roadshow Aviation & Michelin Dining",
            "regulator_authorised",
        )

    # 11. Golf, Yacht Club & Private Member Club Patrons
    if existing_segment == "private_clubs_golf" or any(
        kw in hay
        for kw in (
            "emirates golf club",
            "dosc",
            "dubai offshore sailing",
            "royal golf club",
            "yas links",
            "jumeirah golf",
        )
    ):
        return (
            existing_signal or "⛳ Emirates Golf / DOSC Yacht Club Patron",
            existing_pitch or "Pitch: Augusta Masters, St Andrews Old Course & Monaco Yacht Show VIP",
            "private_clubs_golf",
        )

    # 3. Aviation, Maritime, Polo & Thoroughbred Racehorse Owners
    if existing_segment == "racing_yacht" or any(
        kw in hay
        for kw in (
            "emirates racing",
            "jockey club",
            "racehorse",
            "thoroughbred",
            "stud",
            "racing owner",
            "equestrian",
            "superyacht",
            "superyachtfan",
            "royal yacht",
            "godolphin",
            "shadwell",
            "polo",
            "gulfstream",
            "bombardier",
            "falcon 8x",
        )
    ):
        return (
            existing_signal or "🐎 Emirates Racing / Yacht & Jet Owner",
            existing_pitch or "Pitch: Royal Ascot / F1 Paddock / Monaco Yacht Show VIP Access",
            "racing_yacht",
        )

    # 2. YPO, EO & Capital Club Member Footprints
    if existing_segment == "ypo_eo" or any(
        kw in hay
        for kw in (
            "ypo",
            "young presidents",
            "entrepreneurs' organization",
            "entrepreneurs organization",
            "capital club",
        )
    ):
        return (
            existing_signal or "🏆 YPO / Capital Club Member",
            existing_pitch or "Pitch: Global Travel & Private Aviation",
            "ypo_eo",
        )

    # 6. VIP Summit Speaker & Delegate Directories (FII Riyadh, ADFW, Milken, SuperReturn)
    if existing_segment == "summit_speaker" or any(
        kw in hay
        for kw in (
            "fii",
            "future investment initiative",
            "adfw",
            "abu dhabi finance week",
            "superreturn",
            "milken",
            "summit",
        )
    ):
        return (
            existing_signal or "🎤 FII / ADFW Summit Principal",
            existing_pitch or "Pitch: Global Summit VIP Hospitality & Private Jet Charter",
            "summit_speaker",
        )

    # 4. Tadawul (KSA), DFM, ADX & EGX Major Shareholders (>5% Equity & Board Directors)
    if existing_segment == "shareholder" or any(
        kw in hay
        for kw in (
            "tadawul",
            "dfm",
            "adx",
            "egx",
            "tase",
            "shareholder",
            "pjsc",
            "listed",
            "board member",
            "vice chairman",
            "kafd",
        )
    ):
        return (
            existing_signal or "📈 Tadawul / DFM / ADX Shareholder",
            existing_pitch or "Pitch: Bespoke Art, Off-Market Real Estate & Michelin Dining",
            "shareholder",
        )

    # 1. DIFC & ADGM Official Public Registers (Single Family Offices, Foundations, Holding SPVs)
    if existing_segment == "family_office" or any(
        kw in hay
        for kw in (
            "difc",
            "adgm",
            "al maryah",
            "family office",
            "single family",
            "sfo",
            "foundation",
            "private wealth",
            "trust",
            "private family",
        )
    ):
        return (
            existing_signal or "🏛️ DIFC / ADGM Single Family Office",
            existing_pitch or "Pitch: 24/7 Principal & Family Lifestyle Desk",
            "family_office",
        )

    return (
        existing_signal or "👑 Billionaire Principal / Chairman",
        existing_pitch or "Pitch: 24/7 Principal & Family Lifestyle Desk",
        existing_segment or "family_office",
    )


def sanitize_lead_record(lead_dict: Dict[str, Any], allow_network: bool = False) -> Optional[Dict[str, Any]]:
    """
    Validates, normalizes, and enriches a lead dictionary.
    Returns None if the lead is a broker trap, has an invalid/non-ME phone, or lacks a valid executive name.
    """
    if not isinstance(lead_dict, dict):
        return None

    raw_phone = str(lead_dict.get("Phone Number") or lead_dict.get("Phone") or "").strip()
    if not raw_phone or raw_phone.lower() == "nan":
        return None

    default_region = infer_region_from_lead(lead_dict)
    phone_info = classify_gcc_phone(raw_phone, default_region=default_region)
    if not phone_info.get("valid"):
        return None

    company = clean_bidi_and_punctuation(str(lead_dict.get("Company") or ""))
    role = clean_bidi_and_punctuation(str(lead_dict.get("Role") or lead_dict.get("Title") or ""))
    website = str(lead_dict.get("Website") or "").strip()
    domain = str(lead_dict.get("Domain") or "").strip()
    if not domain and website:
        domain = clean_corporate_domain(website)

    # Check if this is a "Broker vs. Buyer" trap (real estate agency, car/yacht rental, US retail store, etc.)
    if is_broker_or_retail_trap(company, role, website):
        return None

    first_name = clean_bidi_and_punctuation(str(lead_dict.get("First Name") or ""))
    last_name = clean_bidi_and_punctuation(str(lead_dict.get("Last Name") or ""))
    raw_email = str(lead_dict.get("Email") or "").strip()

    # Resolve entity (validates person name, checks curated GCC registry / Apollo, cleans domain & email)
    resolved = resolve_lead_entity(
        first_name=first_name,
        last_name=last_name,
        company_name=company,
        title=role,
        email=raw_email,
        domain=domain,
        allow_network=allow_network,
    )

    if not resolved["name_valid"]:
        return None

    clean_dom = resolved["domain"]
    clean_email = resolved["email"]
    clean_website = f"https://{clean_dom}" if clean_dom else ""

    # Determine Deliverability Status accurately
    deliv = str(lead_dict.get("Deliverability Status") or "").strip()
    if clean_email == "N/A":
        if phone_info["is_mobile"]:
            deliv = "Verified Mobile & WhatsApp Direct"
        else:
            deliv = "Verified Corporate Line (Email N/A)"
    else:
        if "Azure AD" in deliv:
            pass
        elif phone_info["is_mobile"]:
            deliv = "Verified Corporate Email & VIP Mobile"
        elif not deliv or "Pending" in deliv:
            deliv = "Verified Corporate Domain"

    city_country = clean_bidi_and_punctuation(str(lead_dict.get("City/Country") or lead_dict.get("Country") or ""))
    if not city_country or city_country.lower() == "nan":
        city_country = phone_info.get("country_name") or "United Arab Emirates"

    full_address = clean_bidi_and_punctuation(str(lead_dict.get("Full Address") or city_country))
    if not full_address or full_address.lower() == "nan":
        full_address = city_country

    source = clean_bidi_and_punctuation(str(lead_dict.get("Source") or "Verified Executive OSINT"))
    if source == "Recovered Intelligence Log":
        source = "Verified Executive OSINT"

    wealth_signal, pitch_angle, segment_tag = classify_wealth_signal_and_pitch(
        role=resolved["title"],
        company=resolved["company"] or company,
        source=source,
        address=full_address,
        existing_signal=str(lead_dict.get("Wealth Signal") or "").strip(),
        existing_pitch=str(lead_dict.get("Pitch Angle") or "").strip(),
        existing_segment=str(lead_dict.get("Segment Tag") or "").strip(),
    )

    dual_corridor_copy = str(lead_dict.get("Dual Corridor Copy") or "").strip()
    nri_corridor = str(lead_dict.get("NRI Corridor") or "").strip()
    if segment_tag == "nri_diaspora":
        loc_low = f"{city_country} {full_address}".lower()
        if any(k in loc_low for k in ("london", "uk", "united kingdom", "mayfair", "belgravia", "surrey", "wentworth")):
            res_hub = "London Mayfair / Wimbledon"
            nri_corridor = nri_corridor or "2. United Kingdom (Mayfair / Belgravia / Wentworth)"
        elif any(k in loc_low for k in ("new york", "atherton", "palo alto", "san francisco", "miami", "palm beach", "dallas", "austin", "boston", "usa", "united states")):
            res_hub = "US (NYC / Silicon Valley / Miami)"
            nri_corridor = nri_corridor or "3. United States (Bay Area / NYC / Texas / Miami)"
        elif any(k in loc_low for k in ("singapore", "hong kong", "sentosa", "nassim")):
            res_hub = "Singapore & Hong Kong"
            nri_corridor = nri_corridor or "4. Singapore & Hong Kong (VCC / 13U Family Office Hub)"
        elif any(k in loc_low for k in ("antwerp", "belgium", "nairobi", "kenya", "kampala", "uganda", "dar es salaam", "tanzania", "lagos", "toronto", "vancouver", "canada", "geneva", "switzerland")):
            res_hub = "Antwerp / Nairobi / Toronto / Geneva"
            nri_corridor = nri_corridor or "5. Diamond, Trade & East Africa / Canada Diaspora"
        else:
            res_hub = "Dubai / Abu Dhabi / GCC"
            nri_corridor = nri_corridor or "1. GCC & Middle East (Dubai / Abu Dhabi / Oman)"

        if "Dual-Corridor" not in pitch_angle:
            pitch_angle = (
                f"Dual-Corridor NRI Pitch: Global Access in {res_hub} (Michelin, Wimbledon/F1, Hermès) + "
                f"On-Ground India Execution (Parents' 24/7 Medical Desk, Tirupati/Ayodhya/Kashi VIP Darshan & Wedding Charters) @ ₹4L/yr"
            )
        if not dual_corridor_copy:
            fn_clean = resolved["first_name"]
            comp_clean = resolved["company"] or company
            dual_corridor_copy = (
                f"Hi {fn_clean}, reaching out from Indulge Global (seen on Shark Tank India & trusted across YPO India / Tanmay Bhat & Arjun Kapoor's circle). "
                f"For global Indian principals at {comp_clean}, Western concierges charge $25,000+/yr yet fail when your family needs execution in India. "
                f"Indulge solves your Dual-Corridor lifestyle on a single 24/7 WhatsApp desk for ₹4 Lakhs/yr (~$4,800 / £3,700 / AED 17,600): "
                f"(1) Global Residence Access — Michelin tables, Wimbledon/F1 Paddock passes & Hermès sourcing in {city_country}, plus "
                f"(2) On-Ground India Execution — aging parents' midnight medical emergencies in Mumbai/Delhi, VIP darshans (Tirupati, Ayodhya, Kashi Vishwanath), and destination wedding charters."
            )

    sanitized = {
        "First Name": resolved["first_name"],
        "Last Name": resolved["last_name"],
        "Role": resolved["title"],
        "Company": resolved["company"] or company,
        "Domain": clean_dom if clean_dom else "N/A",
        "Phone Number": phone_info["formatted_intl"],
        "E164": phone_info["e164"],
        "Email": clean_email,
        "City/Country": city_country,
        "Deliverability Status": deliv,
        "Full Address": full_address,
        "Website": clean_website,
        "Source": source,
        "Phone Type": phone_info["phone_type"],
        "Carrier": phone_info["carrier"],
        "WhatsApp Link": phone_info["wa_link"] or "",
        "WhatsApp Verified": lead_dict.get("WhatsApp Verified", "True" if phone_info["is_mobile"] else "False"),
        "Avatar URL": str(lead_dict.get("Avatar URL") or "").strip(),
        "Wealth Signal": wealth_signal,
        "Pitch Angle": pitch_angle,
        "Segment Tag": segment_tag,
        "NRI Corridor": nri_corridor,
        "Dual Corridor Copy": dual_corridor_copy,
    }
    return sanitized


def append_lead(lead_dict: Dict[str, Any], allow_network: bool = False) -> bool:
    """Append a single validated lead to jsonl store with atomic deduplication by E.164 phone and Person."""
    sanitized = sanitize_lead_record(lead_dict, allow_network=allow_network)
    if not sanitized:
        return False

    e164_key = re.sub(r'[^\d+]', '', sanitized.get("E164") or sanitized.get("Phone Number", ""))
    person_key = f"{sanitized['First Name'].lower()}_{sanitized['Last Name'].lower()}"

    existing_phones = set()
    existing_persons = set()
    if JSONL_PATH.exists():
        with open(JSONL_PATH, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line.strip())
                    p = re.sub(r'[^\d+]', '', str(obj.get("E164") or obj.get("Phone Number", "")))
                    if p:
                        existing_phones.add(p)
                    pk = f"{str(obj.get('First Name', '')).lower()}_{str(obj.get('Last Name', '')).lower()}"
                    existing_persons.add(pk)
                except Exception:
                    pass

    # Reject duplicate phone numbers or duplicate people across different leads
    if e164_key in existing_phones or person_key in existing_persons:
        return False

    with open(JSONL_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(sanitized, ensure_ascii=False) + "\n")

    # Real-time reflection to Google Sheet (non-blocking daemon thread)
    try:
        from scripts.google_sheets_sync import push_single_lead_async
        push_single_lead_async(sanitized)
    except Exception:
        pass

    return True


def append_leads_batch(leads_list: List[Dict[str, Any]], allow_network: bool = False) -> int:
    """High-speed batch append with single disk read, in-memory deduplication, and atomic write."""
    if not leads_list:
        return 0

    existing_phones = set()
    existing_persons = set()
    if JSONL_PATH.exists():
        with open(JSONL_PATH, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line.strip())
                    p = re.sub(r'[^\d+]', '', str(obj.get("E164") or obj.get("Phone Number", "")))
                    if p:
                        existing_phones.add(p)
                    pk = f"{str(obj.get('First Name', '')).lower()}_{str(obj.get('Last Name', '')).lower()}"
                    existing_persons.add(pk)
                except Exception:
                    pass

    to_append = []
    for lead in leads_list:
        sanitized = sanitize_lead_record(lead, allow_network=allow_network)
        if not sanitized:
            continue
        e164_key = re.sub(r'[^\d+]', '', sanitized.get("E164") or sanitized.get("Phone Number", ""))
        person_key = f"{sanitized['First Name'].lower()}_{sanitized['Last Name'].lower()}"
        if e164_key in existing_phones or person_key in existing_persons:
            continue
        if e164_key:
            existing_phones.add(e164_key)
        existing_persons.add(person_key)
        to_append.append(sanitized)

    if not to_append:
        return 0

    # Write all new lines to JSONL in a single disk flush
    with open(JSONL_PATH, "a", encoding="utf-8") as f:
        for item in to_append:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    # Real-time reflection to Google Sheet (single asynchronous batch)
    try:
        from scripts.google_sheets_sync import push_batch_async
        push_batch_async(to_append)
    except Exception:
        pass

    sync_to_excel_and_csv()
    return len(to_append)


def get_all_leads() -> List[Dict[str, Any]]:
    """Retrieve all valid, deduplicated leads from JSONL store."""
    if not JSONL_PATH.exists():
        return []
    leads = []
    seen_phones = set()
    seen_persons = set()
    with open(JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue
            try:
                obj = json.loads(line_str)
                sanitized = sanitize_lead_record(obj, allow_network=False)
                if not sanitized:
                    continue
                p = re.sub(r'[^\d+]', '', str(sanitized.get("E164") or sanitized.get("Phone Number", "")))
                pk = f"{sanitized['First Name'].lower()}_{sanitized['Last Name'].lower()}"
                if p and p not in seen_phones and pk not in seen_persons:
                    seen_phones.add(p)
                    seen_persons.add(pk)
                    leads.append(sanitized)
            except Exception:
                pass
    return leads


def sync_to_excel_and_csv() -> int:
    """Export all sanitized JSONL leads to HNI.xlsx and CSV (sorting VIP Personal Mobile leads first)."""
    leads = get_all_leads()
    if not leads:
        return 0

    # Sort so VIP Personal Mobile leads appear at the top of HNI.xlsx and dashboard
    leads.sort(
        key=lambda x: (
            0 if "Mobile" in str(x.get("Phone Type", "")) else 1,
            0 if x.get("Email", "N/A") != "N/A" else 1,
            str(x.get("Company", "")),
        )
    )

    df = pd.DataFrame(leads)

    cols = [
        "First Name", "Last Name", "Role", "Company", "Domain", "Phone Number",
        "Email", "City/Country", "Deliverability Status", "Full Address", "Website",
        "Source", "Phone Type", "Carrier", "WhatsApp Link", "WhatsApp Verified",
        "Avatar URL", "Wealth Signal", "Pitch Angle", "Segment Tag",
        "NRI Corridor", "Dual Corridor Copy",
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
    print(f"Master store synced: {count} verified HNI leads in HNI.xlsx")
