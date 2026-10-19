r"""
=============================================================================
INDULGE GLOBAL - 3-LAYER MOBILE, WHATSAPP & CALLER-ID VERIFICATION ENGINE
=============================================================================
Implements the 3 verification layers and data hygiene filters from the Audit:
  Layer A: Strict Telecom Carrier & Line-Type Filtering (phonenumbers + ITU-T)
           - Separates "VIP Personal Mobile" from "Corporate Landline / Switchboard"
           - Generates wa.me/ links ONLY for verified mobile numbers
  Layer B: Live WhatsApp Existence, Pushname & Profile Picture Verification
           - Supports Whapi.cloud, Green-API, Maytapi, and Evolution API
  Layer C: Reverse Caller-ID OSINT Validation (Truecaller / Eyecon / Apify)
           - Confirms registered owner identity against scraped mobile number
  Hygiene:
           - 120-character 1-to-1 Name-to-Phone Proximity Matcher
           - Dummy Domain & Social Email Blocker (@executive-gcc.com -> N/A)
           - "Broker vs. Buyer" Google Maps Trap Filter
=============================================================================
"""

import os
import re
import requests
from urllib.parse import urlparse

try:
    import env_loader
except ImportError:
    from scripts import env_loader


try:
    import phonenumbers
    from phonenumbers import PhoneNumberType, carrier, geocoder
    HAS_PHONENUMBERS = True
except ImportError:
    HAS_PHONENUMBERS = False

# ---------------------------------------------------------------------------
# EMEA Sovereign Country Codes & Priority Wealth Regions (Europe + Middle East)
# ---------------------------------------------------------------------------
ME_ALLOWED_COUNTRY_CODES = {
    # Middle East & Eastern Med (17 Nations)
    971: ("AE", "UAE"),
    966: ("SA", "Saudi Arabia"),
    974: ("QA", "Qatar"),
    965: ("KW", "Kuwait"),
    973: ("BH", "Bahrain"),
    968: ("OM", "Oman"),
    357: ("CY", "Cyprus"),
    20:  ("EG", "Egypt"),
    98:  ("IR", "Iran"),
    964: ("IQ", "Iraq"),
    972: ("IL", "Israel"),
    962: ("JO", "Jordan"),
    961: ("LB", "Lebanon"),
    970: ("PS", "Palestine"),
    963: ("SY", "Syria"),
    90:  ("TR", "Turkey"),
    967: ("YE", "Yemen"),
    # Europe Priority Wealth Hubs (UK, DACH, France, Monaco, Med, Benelux, Nordics)
    44:  ("GB", "United Kingdom"),
    41:  ("CH", "Switzerland"),
    33:  ("FR", "France"),
    377: ("MC", "Monaco"),
    49:  ("DE", "Germany"),
    43:  ("AT", "Austria"),
    39:  ("IT", "Italy"),
    34:  ("ES", "Spain"),
    31:  ("NL", "Netherlands"),
    32:  ("BE", "Belgium"),
    352: ("LU", "Luxembourg"),
    46:  ("SE", "Sweden"),
    47:  ("NO", "Norway"),
    30:  ("GR", "Greece"),
    356: ("MT", "Malta"),
    351: ("PT", "Portugal"),
    353: ("IE", "Ireland"),
    # United States & Canada Priority Wealth Hubs
    1:   ("US", "United States / Canada"),
    # Global NRI Wealth Hubs (Singapore MAS 13O/13U / VCC Single Family Offices & Hong Kong)
    65:  ("SG", "Singapore"),
    852: ("HK", "Hong Kong"),
    # Corridor 5: East & West Africa Indian Industrial Conglomerate Diaspora
    254: ("KE", "Kenya"),
    256: ("UG", "Uganda"),
    255: ("TZ", "Tanzania"),
    234: ("NG", "Nigeria"),
}

LOCATION_TO_REGION = {
    # Middle East
    "dubai": "AE", "abu dhabi": "AE", "sharjah": "AE", "uae": "AE", "emirates": "AE", "difc": "AE", "adgm": "AE",
    "riyadh": "SA", "jeddah": "SA", "khobar": "SA", "dammam": "SA", "saudi": "SA", "ksa": "SA", "kafd": "SA",
    "doha": "QA", "lusail": "QA", "qatar": "QA",
    "kuwait": "KW",
    "manama": "BH", "bahrain": "BH", "seef": "BH",
    "muscat": "OM", "oman": "OM",
    "limassol": "CY", "nicosia": "CY", "cyprus": "CY",
    "cairo": "EG", "giza": "EG", "egypt": "EG", "zamalek": "EG",
    "tehran": "IR", "iran": "IR",
    "baghdad": "IQ", "erbil": "IQ", "iraq": "IQ",
    "tel aviv": "IL", "herzliya": "IL", "jerusalem": "IL", "israel": "IL",
    "amman": "JO", "jordan": "JO", "abdoun": "JO",
    "beirut": "LB", "lebanon": "LB", "achrafieh": "LB",
    "ramallah": "PS", "palestine": "PS",
    "damascus": "SY", "syria": "SY",
    "istanbul": "TR", "ankara": "TR", "bodrum": "TR", "turkey": "TR", "türkiye": "TR",
    "sanaa": "YE", "aden": "YE", "yemen": "YE",
    # Europe Priority Hubs
    "london": "GB", "mayfair": "GB", "belgravia": "GB", "knightsbridge": "GB", "chelsea": "GB", "st john's wood": "GB", "hampstead": "GB", "surrey": "GB", "wentworth": "GB", "leicester": "GB", "birmingham": "GB", "united kingdom": "GB", "uk": "GB",
    "geneva": "CH", "zurich": "CH", "zürich": "CH", "zug": "CH", "lugano": "CH", "st. moritz": "CH", "gstaad": "CH", "switzerland": "CH",
    "paris": "FR", "neuilly": "FR", "cannes": "FR", "saint-tropez": "FR", "antibes": "FR", "france": "FR",
    "monaco": "MC", "monte carlo": "MC", "monte-carlo": "MC",
    "munich": "DE", "münchen": "DE", "grünwald": "DE", "hamburg": "DE", "frankfurt": "DE", "bad homburg": "DE", "düsseldorf": "DE", "germany": "DE",
    "vienna": "AT", "wien": "AT", "austria": "AT",
    "milan": "IT", "milano": "IT", "rome": "IT", "como": "IT", "italy": "IT",
    "madrid": "ES", "marbella": "ES", "barcelona": "ES", "ibiza": "ES", "mallorca": "ES", "spain": "ES",
    "amsterdam": "NL", "rotterdam": "NL", "netherlands": "NL",
    "brussels": "BE", "antwerp": "BE", "knokke": "BE", "belgium": "BE",
    "luxembourg": "LU",
    "stockholm": "SE", "sweden": "SE",
    "oslo": "NO", "norway": "NO",
    # United States & Canada Priority Hubs
    "new york": "US", "nyc": "US", "manhattan": "US", "hamptons": "US", "greenwich": "US", "scarsdale": "US", "alpine": "US", "new jersey": "US",
    "palm beach": "US", "miami": "US", "indian creek": "US", "fisher island": "US", "florida": "US",
    "atherton": "US", "palo alto": "US", "los altos hills": "US", "saratoga": "US", "san jose": "US", "san francisco": "US", "silicon valley": "US", "menlo park": "US", "bay area": "US",
    "beverly hills": "US", "bel air": "US", "malibu": "US", "los angeles": "US", "newport beach": "US",
    "aspen": "US", "jackson hole": "US", "dallas": "US", "plano": "US", "highland park": "US", "houston": "US", "austin": "US", "texas": "US",
    "seattle": "US", "bellevue": "US", "medina": "US",
    "chicago": "US", "boston": "US", "united states": "US", "usa": "US",
    "toronto": "CA", "vancouver": "CA", "canada": "CA",
    # Global NRI Hubs (APAC & Corridor 5 East/West Africa)
    "singapore": "SG", "sentosa": "SG", "nassim": "SG", "orchard": "SG", "bukit timah": "SG", "marina bay": "SG",
    "hong kong": "HK", "mid-levels": "HK", "the peak": "HK", "kowloon": "HK",
    "nairobi": "KE", "kenya": "KE",
    "kampala": "UG", "uganda": "UG",
    "dar es salaam": "TZ", "tanzania": "TZ",
    "lagos": "NG", "nigeria": "NG",
}

# Known Poisoned / Hardcoded Dummy Numbers
POISONED_PHONES = {
    "+97143691700",
    "+96891234567",
    "+35722123456",
    "+96264651234",
}

# ITU-T, European, US/Canada NANP, APAC & East Africa Strict Mobile Prefix Regexes per Country Code (E.164 without spaces)
# Explicitly excludes +4470 personal numbering, +4122/+4144 Swiss fixed, +331 Paris fixed, +3779 Monaco fixed, +4989/+4969 German fixed, and US 800/888/877/866/855/844/833/900 toll-free.
STRICT_MOBILE_E164_RE = re.compile(
    r'^(?:'
    # Middle East
    r'\+971(?:50|52|54|55|56|58)\d{7}|'          # UAE Mobile (9 digits after +971)
    r'\+9665[013456789]\d{7}|'                   # KSA Mobile (9 digits after +966)
    r'\+974(?:30|31|33|50|51|55|60|66|70|71|74|77)\d{6}|'  # Qatar Mobile (8 digits)
    r'\+965[4569]\d{7}|'                         # Kuwait Mobile (8 digits)
    r'\+973(?:3\d|66)\d{6}|'                     # Bahrain Mobile (8 digits)
    r'\+968[79]\d{7}|'                           # Oman Mobile (8 digits)
    r'\+3579[45679]\d{6}|'                       # Cyprus Mobile (+357 95/96/97/99)
    r'\+201[0125]\d{8}|'                         # Egypt Mobile (10 digits)
    r'\+989\d{9}|'                               # Iran Mobile (10 digits)
    r'\+9647[5789]\d{8}|'                        # Iraq Mobile (10 digits)
    r'\+9725[0123458]\d{7}|'                     # Israel Mobile (9 digits)
    r'\+9627[789]\d{7}|'                         # Jordan Mobile (9 digits)
    r'\+961(?:3\d{6}|(?:70|71|76|78|79|81)\d{6})|'  # Lebanon Mobile (7-8 digits)
    r'\+9705[69]\d{7}|'                          # Palestine Mobile (9 digits)
    r'\+9639[345689]\d{7}|'                      # Syria Mobile (9 digits)
    r'\+905[0345]\d{8}|'                         # Turkey Mobile (10 digits)
    r'\+9677[01378]\d{7}|'                       # Yemen Mobile (9 digits)
    # Europe Priority Hubs
    r'\+447[12345789]\d{8}|'                     # UK Mobile (+44 71-75, 77-79; excludes +44 70 personal numbering)
    r'\+417[56789]\d{7}|'                        # Switzerland Mobile (+41 75, 76, 77, 78, 79)
    r'\+33[67]\d{8}|'                            # France Mobile (+33 6, +33 7)
    r'\+377[46]\d{7}|'                           # Monaco Mobile (+377 6, +377 4; excludes +377 9 fixed)
    r'\+491[567]\d{8,9}|'                        # Germany Mobile (+49 15, 16, 17)
    r'\+436[56789]\d{7,9}|'                      # Austria Mobile (+43 650, 660, 664, 676, 699)
    r'\+393\d{8,9}|'                             # Italy Mobile (+39 3...)
    r'\+34[67]\d{8}|'                            # Spain Mobile (+34 6..., +34 7...)
    r'\+316\d{8}|'                               # Netherlands Mobile (+31 6...)
    r'\+324[56789]\d{7}|'                        # Belgium / Antwerp Mobile (+32 4...)
    r'\+3526[269]1\d{6}|'                        # Luxembourg Mobile (+352 621, 661, 691)
    r'\+467[02369]\d{7}|'                        # Sweden Mobile (+46 7...)
    r'\+47[49]\d{7}|'                            # Norway Mobile (+47 4..., +47 9...)
    r'\+3069\d{8}|'                              # Greece Mobile (+30 69...)
    r'\+356[79]\d{7}|'                           # Malta Mobile (+356 79, 99)
    r'\+3519[1236]\d{7}|'                        # Portugal Mobile (+351 9...)
    r'\+3538[35679]\d{7}|'                       # Ireland Mobile (+353 8...)
    # United States & Canada (+1 NANP valid 10-digit numbers excluding 800/888/877/866/855/844/833/900 toll-free and 555 exchange)
    r'\+1(?!(?:800|888|877|866|855|844|833|900))[2-9]\d{2}(?!555)[2-9]\d{6}|'
    # Singapore (+65 8/9 mobile) & Hong Kong (+852 5/6/9 mobile)
    r'\+65[89]\d{7}|'
    r'\+852[569]\d{7}|'
    # Corridor 5: East & West Africa Diaspora Mobile (+254 7/1 Kenya, +256 7 Uganda, +255 7/6 Tanzania, +234 7/8/9 Nigeria)
    r'\+254[17]\d{8}|'
    r'\+2567\d{8}|'
    r'\+255[67]\d{8}|'
    r'\+234[789][01]\d{8}'
    r')$'
)

# Carrier Prefix Fallback Map for EMEA & US when libphonenumber carrier DB is generic
GCC_CARRIER_PREFIXES = [
    # Middle East
    ("+97150", "e& (Etisalat UAE)"),
    ("+97154", "e& (Etisalat UAE)"),
    ("+97156", "e& (Etisalat UAE)"),
    ("+97152", "du (EITC UAE)"),
    ("+97155", "du (EITC UAE)"),
    ("+97158", "du / Virgin Mobile UAE"),
    ("+96650", "STC (Saudi Telecom)"),
    ("+96653", "STC (Saudi Telecom)"),
    ("+96655", "STC (Saudi Telecom)"),
    ("+96654", "Mobily KSA"),
    ("+96656", "Mobily KSA"),
    ("+96658", "Zain KSA"),
    ("+96659", "Zain KSA"),
    ("+96657", "Virgin / Lebara KSA"),
    ("+97433", "Ooredoo Qatar"),
    ("+97455", "Ooredoo Qatar"),
    ("+97466", "Ooredoo Qatar"),
    ("+97477", "Vodafone Qatar"),
    ("+97430", "Vodafone Qatar"),
    ("+97470", "Vodafone Qatar"),
    ("+9659",  "Zain Kuwait"),
    ("+9656",  "Ooredoo Kuwait"),
    ("+9655",  "stc Kuwait"),
    ("+97339", "Batelco Bahrain"),
    ("+97338", "Batelco Bahrain"),
    ("+97336", "Zain Bahrain"),
    ("+97337", "Zain Bahrain"),
    ("+97333", "stc Bahrain"),
    ("+97334", "stc Bahrain"),
    ("+9689",  "Omantel / Ooredoo Oman"),
    ("+9687",  "Vodafone / Omantel Oman"),
    ("+35799", "CYTA Mobile Cyprus"),
    ("+35797", "CYTA Mobile Cyprus"),
    ("+35796", "Epic Cyprus"),
    ("+35795", "PrimeTel Cyprus"),
    ("+2010",  "Vodafone Egypt"),
    ("+2012",  "Orange Egypt"),
    ("+2011",  "e& Egypt"),
    ("+2015",  "WE (Telecom Egypt)"),
    ("+96279", "Zain Jordan"),
    ("+96277", "Orange Jordan"),
    ("+96278", "Umniah Jordan"),
    ("+9613",  "Alfa / Touch Lebanon"),
    ("+96170", "Alfa / Touch Lebanon"),
    ("+96171", "Alfa / Touch Lebanon"),
    ("+96176", "Alfa / Touch Lebanon"),
    ("+9053",  "Turkcell"),
    ("+9054",  "Vodafone Turkey"),
    ("+9050",  "Türk Telekom"),
    ("+9055",  "Türk Telekom"),
    ("+97250", "Pelephone"),
    ("+97252", "Cellcom"),
    ("+97254", "Partner"),
    # Europe
    ("+4477",  "Vodafone / EE UK"),
    ("+4478",  "Vodafone / O2 UK"),
    ("+4479",  "EE / O2 UK"),
    ("+4474",  "Three / Vodafone UK"),
    ("+4475",  "O2 / EE UK"),
    ("+4179",  "Swisscom Switzerland"),
    ("+4178",  "Salt Switzerland"),
    ("+4176",  "Sunrise Switzerland"),
    ("+4177",  "Swisscom / M-Budget CH"),
    ("+336",   "Orange / SFR France"),
    ("+337",   "Bouygues / Free Mobile France"),
    ("+3776",  "Monaco Telecom VIP"),
    ("+3774",  "Monaco Telecom Mobile"),
    ("+4917",  "Telekom Deutschland (D1) / Vodafone"),
    ("+4915",  "Telekom / Vodafone Germany"),
    ("+4916",  "Telekom / O2 Germany"),
    ("+43664", "A1 Telekom Austria"),
    ("+43676", "Magenta Telekom Austria"),
    ("+393",   "TIM / Vodafone Italia"),
    ("+346",   "Movistar / Vodafone Spain"),
    ("+347",   "Orange / Movistar Spain"),
    ("+316",   "KPN / Odido Netherlands"),
    ("+324",   "Proximus / Orange Belgium"),
    ("+352691", "POST Luxembourg Mobile"),
    ("+352621", "POST Luxembourg Mobile"),
    ("+352661", "Orange Luxembourg"),
    ("+467",   "Telia / Tele2 Sweden"),
    ("+479",   "Telenor Norway"),
    ("+474",   "Telia Norway"),
    # United States Super-Prime Area Codes
    ("+1917",  "Verizon / AT&T Wireless NYC"),
    ("+1646",  "Verizon / T-Mobile Wireless NYC"),
    ("+1212",  "Verizon / AT&T Manhattan VIP"),
    ("+1203",  "Verizon / AT&T Greenwich CT"),
    ("+1561",  "AT&T / Verizon Palm Beach FL"),
    ("+1305",  "AT&T / Verizon Miami Beach FL"),
    ("+1650",  "Verizon / AT&T Silicon Valley (Atherton)"),
    ("+1408",  "Verizon / AT&T Silicon Valley (Saratoga/San Jose)"),
    ("+1415",  "Verizon / AT&T San Francisco"),
    ("+1310",  "Verizon / AT&T Beverly Hills / Bel Air"),
    ("+1970",  "Verizon / AT&T Aspen CO"),
    ("+1214",  "AT&T / Verizon Highland Park Dallas"),
    ("+1512",  "AT&T / Verizon Austin TX"),
    ("+1713",  "AT&T / Verizon River Oaks Houston"),
    ("+1425",  "Verizon / T-Mobile Bellevue / Medina WA"),
    ("+1312",  "Verizon / AT&T Chicago Gold Coast"),
    ("+1617",  "Verizon / AT&T Boston Beacon Hill"),
    ("+1416",  "Rogers / Bell Toronto VIP"),
    ("+1604",  "Telus / Rogers Vancouver VIP"),
    # APAC & Corridor 5 Diaspora Hubs
    ("+659",   "Singtel / StarHub Singapore VIP"),
    ("+658",   "Singtel / M1 Singapore Mobile"),
    ("+8529",  "CSL / SmarTone Hong Kong VIP"),
    ("+8526",  "3 HK / China Mobile HK"),
    ("+2547",  "Safaricom / Airtel Kenya VIP"),
    ("+2567",  "MTN / Airtel Uganda VIP"),
    ("+2557",  "Vodacom / Airtel Tanzania VIP"),
    ("+2348",  "MTN / Airtel Nigeria VIP"),
]


def infer_region_from_location(location_str: str) -> str:
    loc_lower = str(location_str or "").lower()
    for key, reg in LOCATION_TO_REGION.items():
        if key in loc_lower:
            return reg
    return "AE"


def _fallback_carrier(e164: str) -> str:
    for prefix, name in GCC_CARRIER_PREFIXES:
        if e164.startswith(prefix):
            return name
    return "Global Telecom Operator"


# ---------------------------------------------------------------------------
# LAYER A: Strict Telecom Carrier & Line-Type Filtering (phonenumbers)
# ---------------------------------------------------------------------------
def classify_gcc_phone(raw_phone: str, default_region: str = "AE") -> dict:
    """
    Validates, normalizes to E.164, and classifies Global (EMEA + US) UHNI phone numbers.
    Ensures landlines (+44 20, +41 22, +41 44, +33 1, +377 9, +49 89, +39 02, +971 4, +971 2, +966 11),
    personal numbering (+44 70), and toll-free (+1 800/888/877, +44 800, +971 800, +966 9200)
    never receive wa.me/ links or 'VIP Personal Mobile' badges.
    """
    if not raw_phone:
        return {"valid": False}

    s = str(raw_phone).strip()
    # Strip extensions like "ext. 113"
    s = re.sub(r'(?i)\bext\.?\s*\d+.*$', '', s).strip()
    # Convert 00 international prefix to +
    if s.startswith("00"):
        s = "+" + s[2:]

    # Fix duplicated country code artifacts like "+965-965 2464862"
    s = re.sub(r'^\+(971|966|974|965|973|968|357|20|964|972|962|961|90|44|41|33|377|49|43|39|34|31|32|352|46|47)[\s\-]+\1\b', r'+\1 ', s)

    clean_digits = re.sub(r'[^\d+]', '', s)
    if clean_digits in POISONED_PHONES:
        return {"valid": False, "reason": "Poisoned fallback phone number"}

    # Check toll-free / shared cost / UK +4470 personal numbering / US 800-888-877-900 patterns explicitly
    is_toll_free_or_non_mobile = bool(
        re.match(
            r'^\+(?:'
            r'(?:971|966|974|968|973|965)(?:800|600|9200)|'
            r'44(?:70|800|808|330|845|870|20)|'
            r'41(?:22|44|41|21|31|61|91|800)|'
            r'33(?:1|2|3|4|5|8|9)|'
            r'3779|'
            r'49(?:89|69|40|30|211|221|711|800)|'
            r'39(?:02|06|800)|'
            r'34(?:91|93|95|800)|'
            r'31(?:20|10|70|800)|'
            r'357(?:22|25)|'
            r'1(?:800|888|877|866|855|844|833|900|\d{3}555)'
            r')',
            clean_digits,
        )
    )

    if HAS_PHONENUMBERS:
        try:
            parsed = phonenumbers.parse(s, default_region)
            if parsed.country_code not in ME_ALLOWED_COUNTRY_CODES:
                return {"valid": False, "reason": f"Country code +{parsed.country_code} outside supported regions"}

            if not phonenumbers.is_valid_number(parsed) and not is_toll_free_or_non_mobile:
                return {"valid": False, "reason": "Invalid number structure"}

            num_type = phonenumbers.number_type(parsed)
            e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            formatted_intl = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

            if e164 in POISONED_PHONES:
                return {"valid": False, "reason": "Poisoned fallback phone number"}

            telco = carrier.name_for_number(parsed, "en")

            # Strict mobile verification: must match MOBILE or FIXED_LINE_OR_MOBILE (standard for US NANP +1)
            # AND STRICT_MOBILE_E164_RE, and NEVER be a landline or toll-free
            is_mobile = (
                (num_type in (PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE_OR_MOBILE))
                and bool(STRICT_MOBILE_E164_RE.match(e164))
                and not is_toll_free_or_non_mobile
            )

            if is_mobile and not telco:
                telco = _fallback_carrier(e164)
            elif not is_mobile:
                telco = telco or "Corporate PSTN / Fixed Line"

            return {
                "valid": True,
                "e164": e164,
                "formatted": formatted_intl,
                "formatted_intl": formatted_intl,
                "is_mobile": is_mobile,
                "wa_link": f"https://wa.me/{e164.lstrip('+')}" if is_mobile else None,
                "phone_type": "VIP Personal Mobile" if is_mobile else "Corporate Landline / Switchboard",
                "carrier": telco or "Global Carrier",
                "region": ME_ALLOWED_COUNTRY_CODES[parsed.country_code][0],
                "country_name": ME_ALLOWED_COUNTRY_CODES[parsed.country_code][1],
            }
        except Exception:
            pass

    # Fallback ITU-T parser if phonenumbers is not installed or number is toll-free
    if not clean_digits.startswith("+"):
        return {"valid": False}

    matched_cc = None
    for cc in sorted(ME_ALLOWED_COUNTRY_CODES.keys(), key=lambda x: -len(str(x))):
        if clean_digits.startswith(f"+{cc}"):
            matched_cc = cc
            break

    if not matched_cc:
        return {"valid": False, "reason": "Outside supported regions"}

    if len(clean_digits) < 10 or len(clean_digits) > 15:
        return {"valid": False, "reason": "Invalid length"}

    is_mobile = bool(STRICT_MOBILE_E164_RE.match(clean_digits)) and not is_toll_free_or_non_mobile
    telco = _fallback_carrier(clean_digits) if is_mobile else "Corporate PSTN / Fixed Line"

    return {
        "valid": True,
        "e164": clean_digits,
        "formatted": s,
        "formatted_intl": s,
        "is_mobile": is_mobile,
        "wa_link": f"https://wa.me/{clean_digits.lstrip('+')}" if is_mobile else None,
        "phone_type": "VIP Personal Mobile" if is_mobile else "Corporate Landline / Switchboard",
        "carrier": telco,
        "region": ME_ALLOWED_COUNTRY_CODES[matched_cc][0],
        "country_name": ME_ALLOWED_COUNTRY_CODES[matched_cc][1],
    }


# ---------------------------------------------------------------------------
# PROXIMITY MATCHING: Prevent Cross-Lead Phone Bleeding (Bug #2)
# ---------------------------------------------------------------------------
PHONE_CANDIDATE_RE = re.compile(
    r'(?:\+|00)(?:971|966|974|965|973|968|357|20|98|964|972|962|961|970|963|90|967|44|41|33|377|49|43|39|34|31|32|352|46|47|30|356|351|353|1)[\s\-\.]?\d{1,3}[\s\-\.]?\d{3,4}[\s\-\.]?\d{3,5}'
    r'|wa\.me/(?:971|966|974|965|973|968|357|20|98|964|972|962|961|970|963|90|967|44|41|33|377|49|43|39|34|31|32|352|46|47|30|356|351|353|1)\d{7,10}'
)


def extract_phone_with_proximity(
    text: str,
    first_name: str,
    last_name: str,
    url: str = "",
    default_region: str = "AE",
    max_distance: int = 120,
    require_mobile: bool = False,
) -> dict:
    """
    Enforces 1-to-1 proximity matching between a person's name and a scraped phone number.
    - On multi-name pages (directories, event lists), the phone number MUST appear within
      `max_distance` (120) characters of the person's first or last name.
    - On dedicated single-person LinkedIn profile URLs (`linkedin.com/in/`), the bio belongs
      to that single individual, so we still check proximity in `title + snippet` first.
    Returns the classified phone dict if valid, or None.
    """
    if not text or not first_name:
        return None

    fn_low = first_name.strip().lower()
    ln_low = last_name.strip().lower() if last_name else ""
    text_low = text.lower()

    # Locate all occurrences of the person's name in text
    name_positions = []
    for token in [f"{fn_low} {ln_low}".strip(), fn_low, ln_low]:
        if len(token) < 3:
            continue
        start = 0
        while True:
            idx = text_low.find(token, start)
            if idx == -1:
                break
            name_positions.append((idx, idx + len(token)))
            start = idx + len(token)

    is_single_linkedin_profile = "/in/" in (url or "").lower() and "linkedin.com" in (url or "").lower()

    for match in PHONE_CANDIDATE_RE.finditer(text):
        raw_match = match.group(0)
        if raw_match.lower().startswith("wa.me/"):
            raw_match = "+" + raw_match.split("/", 1)[1]

        p_start, p_end = match.start(), match.end()

        # Check 120-character proximity to any occurrence of the person's name
        within_proximity = False
        for n_start, n_end in name_positions:
            dist = min(abs(p_start - n_end), abs(n_start - p_end))
            if dist <= max_distance:
                within_proximity = True
                break

        # If not within 120 chars, only allow if it's a single-person LinkedIn /in/ snippet under 400 chars
        if not within_proximity:
            if is_single_linkedin_profile and len(text) <= 450 and name_positions:
                within_proximity = True
            else:
                continue

        classified = classify_gcc_phone(raw_match, default_region=default_region)
        if not classified.get("valid"):
            continue
        if require_mobile and not classified.get("is_mobile"):
            continue
        return classified

    return None


# ---------------------------------------------------------------------------
# LAYER B: Live WhatsApp Existence, Pushname & Avatar Verification
# ---------------------------------------------------------------------------
def verify_whatsapp_live(e164_phone: str) -> dict:
    """
    Programmatically checks whether an E.164 mobile number has an active WhatsApp inbox,
    and fetches pushname + profile_pic_url + is_business via configured gateway:
      1. Whapi.cloud (WHAPI_TOKEN)
      2. Green-API (GREEN_API_INSTANCE + GREEN_API_TOKEN)
      3. Evolution API (EVOLUTION_API_URL + EVOLUTION_API_KEY + EVOLUTION_INSTANCE)
    """
    digits = re.sub(r'[^\d]', '', str(e164_phone or ""))
    if not digits:
        return {"checked": False, "exists": None}

    # 1. Whapi.cloud (/contacts)
    whapi_token = os.environ.get("WHAPI_TOKEN", "").strip()
    if whapi_token:
        try:
            resp = requests.post(
                "https://gate.whapi.cloud/contacts",
                headers={"Authorization": f"Bearer {whapi_token}", "Content-Type": "application/json"},
                json={"blocking": "wait", "contacts": [digits]},
                timeout=10,
            )
            if resp.status_code == 200:
                contacts = resp.json().get("contacts", [])
                if contacts:
                    c = contacts[0]
                    exists = c.get("status") == "valid"
                    return {
                        "checked": True,
                        "provider": "Whapi.cloud",
                        "exists": exists,
                        "pushname": c.get("pushname", ""),
                        "profile_pic_url": c.get("profile_pic", ""),
                        "is_business": bool(c.get("is_business", False)),
                    }
        except Exception:
            pass

    # 2. Green-API (checkWhatsapp)
    green_inst = os.environ.get("GREEN_API_INSTANCE", "").strip()
    green_token = os.environ.get("GREEN_API_TOKEN", "").strip()
    if green_inst and green_token:
        try:
            url = f"https://api.green-api.com/waInstance{green_inst}/checkWhatsapp/{green_token}"
            resp = requests.post(url, json={"phoneNumber": int(digits)}, timeout=10)
            if resp.status_code == 200:
                exists = bool(resp.json().get("existsWhatsapp", False))
                avatar_url = ""
                if exists:
                    av_url = f"https://api.green-api.com/waInstance{green_inst}/getAvatar/{green_token}"
                    av_resp = requests.post(av_url, json={"chatId": f"{digits}@c.us"}, timeout=8)
                    if av_resp.status_code == 200:
                        avatar_url = av_resp.json().get("urlAvatar", "")
                return {
                    "checked": True,
                    "provider": "Green-API",
                    "exists": exists,
                    "pushname": "",
                    "profile_pic_url": avatar_url,
                    "is_business": False,
                }
        except Exception:
            pass

    # 3. Evolution API (Self-hosted Baileys)
    evo_url = os.environ.get("EVOLUTION_API_URL", "").strip().rstrip("/")
    evo_key = os.environ.get("EVOLUTION_API_KEY", "").strip()
    evo_inst = os.environ.get("EVOLUTION_INSTANCE", "").strip()
    if evo_url and evo_key and evo_inst:
        try:
            resp = requests.post(
                f"{evo_url}/chat/whatsappNumbers/{evo_inst}",
                headers={"apikey": evo_key, "Content-Type": "application/json"},
                json={"numbers": [digits]},
                timeout=10,
            )
            if resp.status_code == 200:
                arr = resp.json()
                if isinstance(arr, list) and arr:
                    item = arr[0]
                    exists = bool(item.get("exists", False))
                    return {
                        "checked": True,
                        "provider": "Evolution API",
                        "exists": exists,
                        "pushname": item.get("name", ""),
                        "profile_pic_url": item.get("profilePictureUrl", ""),
                        "is_business": bool(item.get("isBusiness", False)),
                    }
        except Exception:
            pass

    return {"checked": False, "exists": None, "pushname": "", "profile_pic_url": "", "is_business": False}


# ---------------------------------------------------------------------------
# LAYER C: Reverse Caller-ID Validation (Truecaller / Eyecon OSINT Layer)
# ---------------------------------------------------------------------------
def reverse_caller_id_lookup(e164_phone: str, expected_name: str = "") -> dict:
    """
    Queries Truecaller REST API (if TRUECALLER_TOKEN set) to confirm the registered
    owner's name and personal email for a Middle East mobile number.
    """
    truecaller_token = os.environ.get("TRUECALLER_TOKEN", "").strip()
    if not truecaller_token or not e164_phone:
        return {"checked": False}

    classified = classify_gcc_phone(e164_phone)
    if not classified.get("valid"):
        return {"checked": False}

    region = classified.get("region", "AE")
    q_phone = classified["e164"].lstrip("+")

    try:
        resp = requests.get(
            "https://search5-noneu.truecaller.com/v2/search",
            params={
                "q": q_phone,
                "countryCode": region,
                "type": 4,
                "locAddr": "",
                "placement": "SEARCHRESULTS,HISTORY,DETAILS",
                "encoding": "json",
            },
            headers={
                "Authorization": f"Bearer {truecaller_token}",
                "User-Agent": "Truecaller/13.32.6 (Android;13)",
            },
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            if data:
                entry = data[0]
                owner_name = entry.get("name", "").strip()
                emails = [
                    ib.get("id")
                    for ib in entry.get("internetAddresses", [])
                    if ib.get("service") == "email" and ib.get("id")
                ]
                avatar = entry.get("image", "")
                identity_match = True
                if expected_name and owner_name:
                    exp_tokens = {t.lower() for t in expected_name.split() if len(t) > 2}
                    own_tokens = {t.lower() for t in owner_name.split() if len(t) > 2}
                    identity_match = bool(exp_tokens & own_tokens)

                return {
                    "checked": True,
                    "registered_name": owner_name,
                    "identity_match": identity_match,
                    "email": emails[0] if emails else "",
                    "avatar_url": avatar,
                }
    except Exception:
        pass

    return {"checked": False}


# ---------------------------------------------------------------------------
# EMAIL & DOMAIN HYGIENE (Fixes Bug #1: Dummy Fallback Domains)
# ---------------------------------------------------------------------------
DUMMY_OR_SOCIAL_DOMAINS = {
    "executive-gcc.com",
    "uae-investments.ae",
    "familyoffice.ae",
    "familyoffice.sa",
    "linkedin.com",
    "ae.linkedin.com",
    "sa.linkedin.com",
    "qa.linkedin.com",
    "kw.linkedin.com",
    "bh.linkedin.com",
    "om.linkedin.com",
    "eg.linkedin.com",
    "il.linkedin.com",
    "jo.linkedin.com",
    "lb.linkedin.com",
    "sy.linkedin.com",
    "uk.linkedin.com",
    "ca.linkedin.com",
    "in.linkedin.com",
    "cn.linkedin.com",
    "instagram.com",
    "facebook.com",
    "m.facebook.com",
    "wa.me",
    "youtube.com",
    "tiktok.com",
    "twitter.com",
    "x.com",
    "linktr.ee",
    "zoominfo.com",
    "rocketreach.co",
    "lusha.com",
    "soopage.com",
    "kwt.soopage.com",
    "bh.soopage.com",
    "justcall.io",
    "diallink.com",
    "legal500.com",
    "directorycy.com",
    "saudiayp.com",
    "consultingcase101.com",
    "countryguides.andersen.com",
    "pharmaboardroom.com",
    "privacyshield.gov",
    "bayut.com",
    "propertyfinder.ae",
    "dubizzle.com",
}

GENERIC_EMAIL_PREFIXES = {
    "contact", "info", "support", "sales", "admin", "office", "hello", "enquiries",
    "inquiries", "marketing", "careers", "hr", "help", "mail", "reception",
    "executive.principal", "executive.director", "executive.office", "contact.us",
    "about.business", "business.opportunities", "qatari.businessmen", "board.of",
}


def clean_corporate_domain(raw_domain_or_url: str) -> str:
    if not raw_domain_or_url:
        return ""
    s = str(raw_domain_or_url).strip().lower()
    if "://" in s:
        try:
            s = urlparse(s).netloc
        except Exception:
            s = s.split("/")[0]
    else:
        s = s.split("/")[0]
    s = s.replace("www.", "").strip()
    if not s or "|" in s or " " in s or "." not in s:
        return ""
    if s in DUMMY_OR_SOCIAL_DOMAINS:
        return ""
    for blocked in DUMMY_OR_SOCIAL_DOMAINS:
        if s.endswith("." + blocked):
            return ""
    return s


def clean_and_validate_email(raw_email: str, first_name: str = "", last_name: str = "", corporate_domain: str = "") -> str:
    """
    Fixes Bug #1: Never returns @executive-gcc.com, social media emails, or generic
    unverified role-based addresses. Sets Email to 'N/A' unless resolved against a
    real corporate domain or verified personal inbox.
    """
    if not raw_email or str(raw_email).strip().upper() in ("", "N/A", "NAN", "NONE", "—"):
        return "N/A"

    em = str(raw_email).strip().lower()
    if "@" not in em or " " in em or "[" in em or "]" in em or "|" in em:
        return "N/A"

    local_part, dom_part = em.split("@", 1)
    if not local_part or not dom_part or "." not in dom_part:
        return "N/A"

    # Reject dummy or social domains
    if dom_part in DUMMY_OR_SOCIAL_DOMAINS:
        return "N/A"
    for blocked in DUMMY_OR_SOCIAL_DOMAINS:
        if dom_part.endswith("." + blocked):
            return "N/A"

    # Reject generic role prefixes and fabricated placeholder prefixes
    if local_part in GENERIC_EMAIL_PREFIXES:
        return "N/A"
    for bad_prefix in ("executive.", "chairman.", "contact.", "info@", "[pdf]"):
        if local_part.startswith(bad_prefix):
            return "N/A"

    # Reject fabricated name combinations like seattle.times@ or compare.online@
    if first_name and last_name and not is_valid_person_name(first_name, last_name):
        return "N/A"

    return em


# ---------------------------------------------------------------------------
# HUMAN NAME & "BROKER VS. BUYER" TRAP FILTER (Fixes Bug #3)
# ---------------------------------------------------------------------------
INVALID_NAME_TOKENS = {
    "executive", "office", "director", "principal", "chairman", "managing",
    "partner", "founder", "ceo", "cfo", "coo", "president", "owner", "leader",
    "manager", "holding", "holdings", "group", "company", "companies", "llc", "ltd", "inc",
    "corp", "corporation", "capital", "wealth", "investment", "investments",
    "developments", "development", "properties", "property", "realty", "real",
    "estate", "homes", "luxury", "dubai", "abu", "dhabi", "riyadh", "jeddah",
    "doha", "qatar", "kuwait", "bahrain", "manama", "oman", "muscat", "cairo",
    "egypt", "cyprus", "limassol", "nicosia", "amman", "jordan", "beirut",
    "lebanon", "tehran", "iran", "baghdad", "erbil", "iraq", "israel", "istanbul",
    "turkey", "damascus", "syria", "yemen", "sanaa", "saudi", "arabia", "uae",
    "emirates", "gcc", "middle", "east", "international", "global", "world",
    "seattle", "times", "wikipedia", "compare", "online", "average", "setups",
    "linkedin", "instagram", "facebook", "whatsapp", "contact", "about",
    "business", "opportunities", "bahrainbanksdirectory", "qatari", "businessmen",
    "board", "engineering", "services", "trust", "china", "low", "iosh",
    "lawyer", "startup", "prime", "movers", "helpline", "otis", "elevator",
    "pdf", "dr", "mr", "mrs", "ms", "prof", "von",
    "st", "co", "the", "one", "in", "on", "of", "to", "e", "c", "pif", "ai",
    "club", "hotels", "staywell", "financial", "projects", "states", "australia",
    "security", "management", "trading", "alhilal", "coach", "and", "or", "for",
    "with", "from", "at", "by", "sales", "engineer", "consultant", "advisory",
    "marketing", "operations", "project", "admin", "administrative", "secretary",
}

# Google Maps Categories & Keywords that represent Retail / Service Brokers or Non-HNI Staff rather than HNI Buyers / Principals
BROKER_OR_RETAIL_TRAP_PATTERNS = [
    r'\breal estate agen(?:t|cy)\b',
    r'\breal estate broker\b',
    r'\bproperty management\b',
    r'\bshort term apartment rental\b',
    r'\bapartment rental\b',
    r'\boffice space rental\b',
    r'\bserviced office\b',
    r'\bcoworking\b',
    r'\bregus\b',
    r'\bthe executive centre\b',
    r'\byacht broker\b',
    r'\byacht rental\b',
    r'\bboat rental\b',
    r'\bboat tour\b',
    r'\bcar rental\b',
    r'\bcar dealer\b',
    r'\bmoving\b',
    r'\bmovers\b',
    r'\bhelpline\b',
    r'\bstarbucks\b',
    r'\bpak mail\b',
    r'\bsephora\b',
    r'\bwine bar\b',
    r'\bsteakhouse\b',
    r'\brooftop lounge\b',
    r'\bdelta dental\b',
    r'\bcornell tech\b',
    r'\btravel agency\b',
    r'\btourism agency\b',
    r'\bholiday\b',
    r'\bvacation club\b',
    r'\bstaff accommodation\b',
    r'\bplumbing\b',
    r'\belevator\b',
    r'\bair freight\b',
    r'\bu\.?s\.?\s*embassy\b',
    r'\bconsulate\b',
    r'\bsales engineer\b',
    r'\bsystem engineer\b',
    r'\bproject engineer\b',
    r'\bexecutive secretary\b',
    r'\badministrative manager\b',
    r'\boperations manager\b',
    r'\benvironmental consultant\b',
    r'\bsecurity compliance\b',
    r'\bkarmal brokerage\b',
    r'\bbuy luxury properties\b',
]
BROKER_TRAP_RE = re.compile("|".join(BROKER_OR_RETAIL_TRAP_PATTERNS), re.IGNORECASE)


def clean_bidi_and_punctuation(text: str) -> str:
    if not text:
        return ""
    # Remove RTL/LTR marks, zero-width spaces, and stray punctuation
    s = re.sub(r'[\u200b-\u200f\u202a-\u202e\ufeff]', '', str(text))
    return s.strip()


def is_valid_person_name(first_name: str, last_name: str, company_name: str = "") -> bool:
    """
    Strictly validates that First Name + Last Name represent a real human executive,
    not 'Diego Executive', 'Executive Office', 'Chairman / Managing Director (Sol)',
    'Seattle Times', 'Dubai Wikipedia', 'Security Companies', 'Arif Management', etc.
    """
    fn = clean_bidi_and_punctuation(first_name)
    ln = clean_bidi_and_punctuation(last_name)

    if not fn or not ln:
        return False

    if "(" in fn or ")" in fn or "(" in ln or ")" in ln or "/" in fn or "/" in ln or "[" in fn:
        return False

    # Strip dots/hyphens/spaces/apostrophes for alpha check
    fn_clean = re.sub(r'[\.\-\s\']', '', fn)
    ln_clean = re.sub(r'[\.\-\s\']', '', ln)

    if len(fn_clean) < 2 or len(ln_clean) < 2:
        return False

    if not fn_clean.isalpha() or not ln_clean.isalpha():
        return False

    fn_low = fn.lower()
    ln_low = ln.lower()

    if fn_low in INVALID_NAME_TOKENS or ln_low in INVALID_NAME_TOKENS:
        return False

    fn_tokens = [t.lower() for t in re.split(r'[\s\-]+', fn) if t]
    for tok in fn_tokens:
        if tok in INVALID_NAME_TOKENS and tok not in ("al", "el", "bin", "ibn", "prince", "sheikh", "sheikha", "shaikh"):
            return False

    # Check all tokens in last name
    ln_tokens = [t.lower() for t in re.split(r'[\s\-]+', ln) if t]
    if not ln_tokens:
        return False
    for tok in ln_tokens:
        if tok in INVALID_NAME_TOKENS and tok not in ("al", "el", "bin", "ibn", "m.a."):
            return False

    if fn_low == ln_low:
        return False

    # Ensure name is not literally the company name split into two words
    if company_name:
        comp_norm = re.sub(r'[^a-z]', '', company_name.lower())
        name_norm = re.sub(r'[^a-z]', '', f"{fn_low}{ln_low}")
        if comp_norm and name_norm == comp_norm:
            return False

    return True


def is_broker_or_retail_trap(company: str, role: str, website: str = "") -> bool:
    """
    Detects Google Maps 'Broker vs. Buyer' traps (real estate agents/brokers, boat/car rentals,
    moving companies, restaurants, serviced offices, social media reels, non-HNI mid-level roles).
    """
    comp_clean = clean_bidi_and_punctuation(company)
    role_clean = clean_bidi_and_punctuation(role)

    # Reject corrupted company/role fields that are just phone digits or "WhatsApp"
    if re.match(r'^[\+\d\s\-\|]+$', comp_clean) or re.match(r'^[\+\d\s\-\|]+$', role_clean):
        return True
    if comp_clean.lower() in ("whatsapp", "corp", "board member", "syria", "qatar", "class+ families") or role_clean.lower() in ("whatsapp",):
        return True

    combined = f"{comp_clean} {role_clean} {website or ''}"
    if BROKER_TRAP_RE.search(combined):
        return True

    w_low = (website or "").lower()
    if any(p in w_low for p in ("instagram.com/reel/", "instagram.com/p/", "tiktok.com/@", "facebook.com/groups/", "/posts/", "youtube.com/shorts/", "usembassy.gov")):
        return True

    return False
