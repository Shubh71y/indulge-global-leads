"""
GCC & Middle East Executive Entity Resolver (Apollo.io + Parallel AI + Curated Sovereign/Family Office Registry).
Eliminates placeholder names ("Executive Office", "Chairman / Managing Director (Company)", "Executive Principal")
and dummy domains ("executive-gcc.com", "uae-investments.ae") by resolving real C-Suite/Principal names
and verified corporate domains.
"""
import os
import re
import requests
from typing import Dict, Any, Optional, Tuple
from scripts.env_loader import load_env
from scripts.phone_verifier import (
    clean_corporate_domain,
    clean_and_validate_email,
    clean_bidi_and_punctuation,
    is_valid_person_name,
    is_broker_or_retail_trap,
)

load_env()

# Verified GCC / Middle East Family Office, Conglomerate, Sovereign & Developer Principal Registry
# Maps normalized company/group keywords -> (First Name, Last Name, Title, Verified Corporate Domain)
VERIFIED_GCC_EXECUTIVES: Dict[str, Tuple[str, str, str, str]] = {
    "al futtaim": ("Omar", "Al Futtaim", "Vice Chairman & CEO", "alfuttaim.com"),
    "majid al futtaim": ("Ahmed", "Galal Ismail", "Chief Executive Officer", "majidalfuttaim.com"),
    "al ghurair": ("Abdul Aziz", "Al Ghurair", "Chairman", "al-ghurair.com"),
    "al habtoor": ("Khalaf", "Al Habtoor", "Founding Chairman", "habtoor.com"),
    "al rostamani": ("Marwan", "Al Rostamani", "Chairman", "alrostamanigroup.ae"),
    "al tayer": ("Saeed", "Al Tayer", "Managing Director", "altayer.com"),
    "chalhoub": ("Patrick", "Chalhoub", "Group President", "chalhoubgroup.com"),
    "emaar": ("Mohamed", "Alabbar", "Founder & Managing Director", "emaar.ae"),
    "damac": ("Hussain", "Sajwani", "Founder & Chairman", "damacproperties.com"),
    "sobharealty": ("PNC", "Menon", "Founder & Chairman", "sobharealty.com"),
    "sobha": ("PNC", "Menon", "Founder & Chairman", "sobharealty.com"),
    "nakheel": ("Mohammed", "Al Shaibani", "Chairman", "nakheel.com"),
    "aldar": ("Mohamed", "Al Mubarak", "Chairman", "aldar.com"),
    "azizi": ("Mirwais", "Azizi", "Founder & Chairman", "azizidevelopments.com"),
    "danube": ("Rizwan", "Sajan", "Founder & Chairman", "danubeproperties.ae"),
    "binghatti": ("Muhammad", "Binghatti", "Chairman", "binghatti.com"),
    "omniyat": ("Mahdi", "Amjad", "Founder & Executive Chairman", "omniyat.com"),
    "ellington": ("Robert", "Booth", "Co-Founder & Managing Director", "ellingtonproperties.ae"),
    "arada": ("Sheikh Sultan", "Al Qasimi", "Chairman", "arada.com"),
    "select group": ("Rahail", "Aslam", "Founder & Group CEO", "select-group.ae"),
    "deyaar": ("Saeed", "Al Qatami", "Chief Executive Officer", "deyaar.ae"),
    "meraas": ("Sheikh Ahmed", "bin Saeed Al Maktoum", "Chairman", "meraas.com"),
    "dubai holding": ("Amit", "Kaushal", "Group Chief Executive Officer", "dubaiholding.com"),
    "mubadala": ("Khaldoon", "Al Mubarak", "Managing Director & Group CEO", "mubadala.ae"),
    "abu dhabi investment authority": ("Sheikh Tahnoun", "bin Zayed Al Nahyan", "Chairman", "adia.ae"),
    "adq": ("Mohamed Hassan", "Alsuwaidi", "Managing Director & Group CEO", "adq.ae"),
    "international holding company": ("Syed Basar", "Shueb", "Chief Executive Officer", "ihcuae.com"),
    "bin butti": ("Sheikh Butti", "bin Suhail Al Maktoum / Al Qubaisi", "Chairman", "binbutti.com"),
    "royal group": ("Sheikh Tahnoun", "bin Zayed Al Nahyan", "Chairman", "royalgroupuae.com"),
    "lulu group": ("Yusuff Ali", "M.A.", "Chairman & Managing Director", "lulugroupinternational.com"),
    "landmark group": ("Renuka", "Jagtiani", "Chairwoman", "landmarkgroup.com"),
    "apparel group": ("Nilesh", "Ved", "Founder & Chairman", "apparelglobal.com"),
    "gargash": ("Shehab", "Gargash", "Managing Director & Group CEO", "gargash.ae"),
    "galadari": ("Suhail", "Galadari", "Co-Chairman", "galadarigroup.com"),
    "juma al majid": ("Juma", "Al Majid", "Founder & Chairman", "al-majid.com"),
    "al serkal": ("Isa", "Alserkal", "Chairman", "alserkal.ae"),
    "binhendi": ("Mohi-Din", "BinHendi", "President & Chairman", "binhendi.com"),
    "al shirawi": ("Abdulla", "Al Shirawi", "Chairman", "alshirawi.com"),
    "al naboodah": ("Abdullah", "Al Naboodah", "Chairman", "alnaboodah.com"),
    "al ghandi": ("Saeed", "Al Ghandi", "Chairman", "alghandi.com"),
    "al masaood": ("Masaood", "Ahmed Al Masaood", "Chairman", "masaood.com"),
    "al fahim": ("Mohammed", "Abdul Jalil Al Fahim", "Chairman", "alfahim.ae"),
    "bin jabr": ("Saeed", "Bin Jabr Al Suwaidi", "Chairman", "binjabr.com"),
    "suhail bahwan": ("Suhail", "Bahwan", "Founder & Chairman", "suhailbahwangroup.com"),
    "saud bahwan": ("Mohammed", "Saud Bahwan", "Chairman", "saudbahwangroup.com"),
    "zubair": ("Rashad", "Al Zubair", "Chairman", "zubaircorp.com"),
    "wj towell": ("Hussain", "Jawad", "Chairman", "wjtowell.com"),
    "khimji ramdas": ("Nailesh", "Khimji", "Director", "khimji.com"),
    "zain group": ("Badr", "Al-Kharafi", "Vice Chairman & Group CEO", "zain.com"),
    "alshaya": ("Mohammed", "Alshaya", "Executive Chairman", "alshaya.com"),
    "alghanim": ("Kutayba", "Alghanim", "Executive Chairman", "alghanim.com"),
    "kipco": ("Sheikha Dana", "Naser Sabah Al Ahmad", "Group CEO", "kipco.com"),
    "national bank of kuwait": ("Isam", "Al-Sager", "Vice Chairman & Group CEO", "nbk.com"),
    "kamco": ("Faisal", "Mansour Sarkhou", "Chief Executive Officer", "kamcoinvest.com"),
    "wafra": ("Bader", "Al-Sumait", "Chief Executive Officer", "wafra.com"),
    "dangote": ("Aliko", "Dangote", "Founder & President", "dangote.com"),
    "sawiris": ("Nassef", "Sawiris", "Executive Chairman", "orascom.com"),
    "orascom": ("Naguib", "Sawiris", "Executive Chairman", "orascom.com"),
    "mansour group": ("Mohamed", "Mansour", "Chairman", "mansourgroup.com"),
    "talaat moustafa": ("Hisham", "Talaat Moustafa", "CEO & Managing Director", "talaatmoustafa.com"),
    "palm hills": ("Yasseen", "Mansour", "Chairman & Group CEO", "palmhillsdevelopments.com"),
    "efg hermes": ("Karim", "Awad", "Group Chief Executive Officer", "efgholding.com"),
    "qatar investment authority": ("Mohammed", "Al-Sowaidi", "Chief Executive Officer", "qia.qa"),
    "alfardan": ("Hussain", "Ibrahim Alfardan", "Chairman", "alfardan.com.qa"),
    "al mana group": ("Hisham", "Saleh Al Mana", "Chairman & Managing Director", "almanagroup.com"),
    "darwish holding": ("Bader", "Abdullah Al-Darwish", "Chairman & Managing Director", "darwishholding.com"),
    "faisal holding": ("Sheikh Faisal", "bin Qassim Al Thani", "Chairman", "al-faisalholding.com"),
    "alrabban": ("Khalid", "Al Rabban", "Chairman", "alrabbanprojects.com"),
    "investcorp": ("Mohammed", "Alardhi", "Executive Chairman", "investcorp.com"),
    "gfh financial": ("Hisham", "Alrayes", "Group Chief Executive Officer", "gfh.com"),
    "mumtalakat": ("Shaikh Abdulla", "bin Khalifa Al Khalifa", "Chief Executive Officer", "mumtalakat.bh"),
    "kanoo": ("Mishal", "Kanoo", "Chairman", "kanoogroup.com"),
    "zayani": ("Khalid", "Rashid Al Zayani", "Honorary Chairman", "alzayani.com"),
    "nass corporation": ("Sameer", "Abdulla Nass", "Chairman", "nasscorporation.com"),
    "almoayyed": ("Farouk", "Yousuf Almoayyed", "Chairman", "almoayyedintl.com.bh"),
    "olayan": ("Lubna", "Olayan", "Chair of the Executive Committee", "olayan.com"),
    "kingdom holding": ("Prince Alwaleed", "bin Talal", "Founder & Chairman", "kingdom.com.sa"),
    "al rajhi": ("Abdullah", "bin Sulaiman Al Rajhi", "Chairman", "alrajhibank.com.sa"),
    "zamil": ("Khalid", "Abdullah Al Zamil", "Chairman", "zamil.com"),
    "abdul latif jameel": ("Mohammed", "Abdul Latif Jameel", "Chairman & CEO", "alj.com"),
    "al jomaih": ("Hamad", "Abdulaziz Al Jomaih", "Chairman", "aljomaih.com"),
    "sedco": ("Rayyan", "Nagadi", "Chief Executive Officer", "sedco.com"),
    "savola": ("Waleed", "Fatani", "Group Chief Executive Officer", "savola.com"),
    "almarai": ("Prince Naif", "bin Sultan Al Saud", "Chairman", "almarai.com"),
    "alhokair": ("Fawaz", "Abdulaziz Alhokair", "Founder & Chairman", "cenomi.com"),
    "cenomi": ("Fawaz", "Abdulaziz Alhokair", "Founder & Chairman", "cenomi.com"),
    "al muhaidib": ("Sulaiman", "Al Muhaidib", "Chairman", "muhaidib.com"),
    "al subeaei": ("Ibrahim", "bin Abdullah Al Subeaei", "Chairman", "alsubeaei.com"),
    "yousuf naghi": ("Mohamed", "Yousuf Naghi", "Chairman", "mynaghi.com"),
    "jarir": ("Muhammad", "Al-Agil", "Chairman", "jarir.com"),
    "ajlan": ("Ajlan", "bin Abdulaziz Al Ajlan", "Chairman", "ajlanbros.com"),
    "alireza": ("Teymour", "Alireza", "Chairman", "rezayat.com"),
    "rezayat": ("Teymour", "Alireza", "Chairman", "rezayat.com"),
    "juffali": ("Khaled", "Juffali", "Chairman", "juffali.com"),
    "dabbagh": ("Amr", "Al-Dabbagh", "Chairman & CEO", "aldabbagh.com"),
    "binladin": ("Saad", "Al-Ladhani", "Chief Executive Officer", "sbg.com.sa"),
    "roshn": ("David", "Grover", "Group CEO", "roshn.sa"),
    "dar al arkan": ("Yousef", "Al Shelash", "Chairman", "daralarkan.com"),
    "jabal omar": ("Saeed", "Al Ghamdi", "Chairman", "jabalomar.com.sa"),
    "public investment fund": ("Yasir", "Al-Rumayyan", "Governor", "pif.gov.sa"),
    "sanabil": ("Abdullah", "Al-abduljabbar", "Chief Executive Officer", "sanabil.com"),
    "hassana": ("Saad", "Al-Fadly", "Chief Executive Officer", "hassana.com.sa"),
    "saudi national bank": ("Saeed", "Al-Ghamdi", "Chairman", "alahli.com"),
    "riyad bank": ("Tareq", "Al-Sadhan", "Chief Executive Officer", "riyadbank.com"),
    "bank albilad": ("Nasser", "Al-Subeaei", "Chairman", "bankalbilad.com"),
    "alinma": ("Abdulmalek", "Al-Hugail", "Chairman", "alinma.com"),
    "jadwa": ("Tariq", "Al-Sudairy", "Managing Director & CEO", "jadwa.com"),
    "derayah": ("Mohammed", "Al-Shammasi", "Chief Executive Officer", "derayah.com"),
    "arab bank": ("Sabih", "Al-Masri", "Chairman", "arabbank.com"),
    "hikma": ("Said", "Darwazah", "Executive Chairman", "hikma.com"),
    "nuqul": ("Ghassan", "Nuqul", "Chairman", "nuqulgroup.com"),
    "manaseer": ("Ziad", "Al-Manaseer", "Founder & Chairman", "manaseergroup.com"),
    "edgo": ("Omar", "Masri", "Chief Executive Officer", "edgo.com"),
    "mikati": ("Najib", "Mikati", "Co-Founder & Chairman", "m1group.com"),
    "m1 group": ("Taha", "Mikati", "Co-Founder", "m1group.com"),
    "bank audi": ("Khalil", "Debs", "Chairman", "bankaudi.com.lb"),
    "blom bank": ("Saad", "Azhari", "Chairman & General Manager", "blombank.com"),
    "solidere": ("Nasser", "Chammaa", "Chairman & General Manager", "solidere.com"),
    "koc holding": ("Omer", "Koc", "Chairman", "koc.com.tr"),
    "sabanci": ("Guler", "Sabanci", "Chairwoman", "sabanci.com"),
    "eczacibasi": ("Bulent", "Eczacibasi", "Chairman", "eczacibasi.com.tr"),
    "dogus": ("Ferit", "Sahenk", "Chairman & CEO", "dogusgrubu.com.tr"),
    "anadolu": ("Tuncay", "Ozilhan", "Chairman", "anadolugrubu.com.tr"),
    "zorlu": ("Ahmet", "Nazif Zorlu", "Chairman", "zorlu.com.tr"),
    "limak": ("Ebru", "Ozdemir", "Chairwoman", "limak.com.tr"),
    "cengiz": ("Mehmet", "Cengiz", "Chairman", "cengiz.com.tr"),
    "kalyon": ("Cemal", "Kalyoncu", "Chairman", "kalyonholding.com"),
    "ronesans": ("Erman", "Ilicak", "President", "ronesans.com"),
    "enka": ("Mehmet", "Tara", "Chairman", "enka.com"),
    "deugro": ("Thomas", "Press", "Chairman & CEO", "deugro.com"),
    "julius baer": ("Alireza", "Valizadeh", "CEO Julius Baer Middle East", "juliusbaer.com"),
    "ubs": ("Niels", "Zilkens", "Head Wealth Management Middle East", "ubs.com"),
    "lombard odier": ("Arnaud", "Leclercq", "Partner & Head of New Markets", "lombardodier.com"),
    "pictet": ("Fawzi", "Kyriakos-Saad", "Senior Executive Middle East", "pictet.com"),
    "mirabaud": ("Thiago", "Frazao", "Managing Partner Middle East", "mirabaud.com"),
    "rothschild": ("Saeed", "Al Awar", "Partner & Head of Middle East", "rothschildandco.com"),
    "lazard": ("Farah", "Foustok", "CEO Lazard Gulf", "lazard.com"),
    "goldman sachs": ("Fadi", "Abuali", "Co-CEO MENA", "gs.com"),
    "jp morgan": ("Khaled", "Hobballah", "Senior Country Officer MENA", "jpmorgan.com"),
    "morgan stanley": ("Abdulaziz", "Alajaji", "CEO Saudi Arabia & Co-Head MENA", "morganstanley.com"),
    "hsbc": ("Stephen", "Moss", "Regional CEO MENAT", "hsbc.com"),
    "standard chartered": ("Sunil", "Kaushal", "Regional CEO Africa & Middle East", "sc.com"),
    "first abu dhabi bank": ("Hana", "Al Rostamani", "Group Chief Executive Officer", "bankfab.com"),
    "emirates nbd": ("Shayne", "Nelson", "Group Chief Executive Officer", "emiratesnbd.com"),
    "adcb": ("Ala'a", "Eraiqat", "Group Chief Executive Officer", "adcb.com"),
    "mashreq": ("Ahmed", "Abdelaal", "Group Chief Executive Officer", "mashreq.com"),
    "dubai islamic bank": ("Adnan", "Chilwan", "Group Chief Executive Officer", "dib.ae"),
    "adib": ("Mohamed", "Abdelbary", "Group Chief Executive Officer", "adib.ae"),
    "rakbank": ("Raheel", "Ahmed", "Chief Executive Officer", "rakbank.ae"),
    "commercial bank of dubai": ("Bernd", "van Linder", "Chief Executive Officer", "cbd.ae"),
    "shuaa": ("Wafik", "Ben Mansour", "Group Chief Executive Officer", "shuaa.com"),
    "waha capital": ("Mohamed", "Al Nowais", "Managing Director", "wahacapital.com"),
    "gulf capital": ("Karim", "El Solh", "Co-Founder & CEO", "gulfcapital.com"),
    "fajr capital": ("Iqbal", "Khan", "Chief Executive Officer", "fajrcapital.com"),
    "global ventures": ("Noor", "Sweid", "Founder & Managing Partner", "globalventures.vc"),
    "beco capital": ("Dany", "Farha", "Co-Founder & CEO", "becocapital.com"),
    "wamda": ("Fadi", "Ghandour", "Executive Chairman", "wamda.com"),
    "shorooq": ("Mahmoud", "Adi", "Founding Partner", "shorooq.com"),
    "stv": ("Abdulrahman", "Tarabzouni", "Founder & CEO", "stv.vc"),
    "waed": ("Fahad", "Alidi", "Managing Director", "waed.net"),
    "aramco": ("Amin", "Nasser", "President & Chief Executive Officer", "aramco.com"),
    "sabic": ("Abdulrahman", "Al-Fageeh", "Chief Executive Officer", "sabic.com"),
    "maaden": ("Bob", "Wilt", "Chief Executive Officer", "maaden.com.sa"),
    "acwa power": ("Mohammad", "Abunayyan", "Founder & Chairman", "acwapower.com"),
    "saudi telecom": ("Olayan", "Alwetaid", "Group Chief Executive Officer", "stc.com.sa"),
    "etisalat": ("Hatem", "Dowidar", "Group Chief Executive Officer", "eand.com"),
    "emirates integrated telecommunications": ("Fahad", "Al Hassawi", "Chief Executive Officer", "du.ae"),
    "ooredoo": ("Aziz", "Aluthman Fakhroo", "Managing Director & Group CEO", "ooredoo.com"),
    "dp world": ("Sultan", "Ahmed bin Sulayem", "Group Chairman & CEO", "dpworld.com"),
    "emirates airline": ("Sheikh Ahmed", "bin Saeed Al Maktoum", "Chairman & Chief Executive", "emirates.com"),
    "etihad": ("Antonoaldo", "Neves", "Chief Executive Officer", "etihad.com"),
    "qatar airways": ("Badr", "Mohammed Al-Meer", "Group Chief Executive Officer", "qatarairways.com"),
    "saudia": ("Ibrahim", "Al-Omar", "Director General", "saudia.com"),
    "flydubai": ("Ghaith", "Al Ghaith", "Chief Executive Officer", "flydubai.com"),
    "air arabia": ("Adel", "Al Ali", "Group Chief Executive Officer", "airarabia.com"),
    "adnoc": ("Sultan", "Ahmed Al Jaber", "Managing Director & Group CEO", "adnoc.ae"),
    "taqa": ("Jasim", "Husain Thabet", "Group Chief Executive Officer", "taqa.com"),
    "masdar": ("Mohamed", "Jameel Al Ramahi", "Chief Executive Officer", "masdar.ae"),
    "aluminium bahrain": ("Ali", "Al Baqali", "Chief Executive Officer", "albasmelter.com"),
    "bapco": ("Mark", "Thomas", "Group Chief Executive Officer", "bapcoenergies.com"),
    "oq group": ("Ashraf", "Al Mamari", "Group Chief Executive Officer", "oq.com"),
    "petroleum development oman": ("Abla", "Al Riyami", "Managing Director", "pdo.co.om"),
    "bank muscat": ("Waleed", "Al Hashar", "Chief Executive Officer", "bankmuscat.com"),
    "national bank of oman": ("Abdullah", "Al Hinai", "Chief Executive Officer", "nbo.om"),
    "sohar international": ("Abdulwahid", "Al Murshidi", "Chief Executive Officer", "soharinternational.com"),
    "omantel": ("Talal", "Al Mamari", "Chief Executive Officer", "omantel.om"),
    "asyad": ("Abdulrahman", "Al Hatmi", "Group Chief Executive Officer", "asyad.om"),
}


def lookup_curated_executive(company_name: str, existing_domain: str = "") -> Optional[Dict[str, str]]:
    """
    Checks if a company matches our verified GCC/Middle East HNI & Family Office registry
    using strict word-boundary matching.
    Returns dict with first_name, last_name, title, domain, email if found.
    """
    if not company_name:
        return None
    comp_lower = clean_bidi_and_punctuation(company_name).lower()
    for keyword, (fn, ln, title, dom) in VERIFIED_GCC_EXECUTIVES.items():
        if re.search(rf"\b{re.escape(keyword)}\b", comp_lower):
            clean_fn = fn.capitalize() if fn.islower() else fn
            domain_to_use = clean_corporate_domain(existing_domain) or dom
            return {
                "first_name": clean_fn,
                "last_name": ln,
                "title": title,
                "domain": domain_to_use,
                "email": "N/A",
                "source": "Verified GCC Executive Registry",
            }
    return None


def resolve_via_apollo(
    company_name: str,
    domain: str = "",
    first_name: str = "",
    last_name: str = "",
) -> Optional[Dict[str, str]]:
    """
    Uses Apollo.io API (APOLLO_API_KEY synced from coldmail-agent) to resolve C-Suite / Principal
    decision-maker and verified corporate email/domain.
    """
    apollo_key = os.getenv("APOLLO_API_KEY", "").strip()
    if not apollo_key:
        return None

    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": apollo_key,
    }

    clean_dom = clean_corporate_domain(domain)

    # 1. If we already have a valid person name, try Apollo People Match
    if is_valid_person_name(first_name, last_name, company_name):
        try:
            payload: Dict[str, Any] = {
                "first_name": first_name,
                "last_name": last_name,
                "organization_name": company_name,
                "reveal_personal_emails": True,
            }
            if clean_dom:
                payload["domain"] = clean_dom

            resp = requests.post(
                "https://api.apollo.io/v1/people/match",
                headers=headers,
                json=payload,
                timeout=8,
            )
            if resp.status_code == 200:
                person = resp.json().get("person") or {}
                if person:
                    p_fn = person.get("first_name") or first_name
                    p_ln = person.get("last_name") or last_name
                    p_title = person.get("title") or "Chairman & Managing Director"
                    org = person.get("organization") or {}
                    p_dom = clean_corporate_domain(org.get("primary_domain") or clean_dom)
                    raw_email = person.get("email") or ""
                    valid_email = clean_and_validate_email(raw_email, p_fn, p_ln, p_dom)
                    return {
                        "first_name": p_fn,
                        "last_name": p_ln,
                        "title": p_title,
                        "domain": p_dom,
                        "email": valid_email,
                        "linkedin": person.get("linkedin_url") or "",
                        "source": "Apollo.io Match",
                    }
        except Exception:
            pass

    # 2. Search for C-Suite / Founder / Chairman at the organization
    try:
        search_payload: Dict[str, Any] = {
            "page": 1,
            "per_page": 3,
            "person_seniorities": ["owner", "founder", "c_suite", "partner", "vp"],
        }
        if clean_dom:
            search_payload["q_organization_domains"] = clean_dom
        else:
            search_payload["q_organization_name"] = company_name

        resp = requests.post(
            "https://api.apollo.io/v1/mixed_people/search",
            headers=headers,
            json=search_payload,
            timeout=8,
        )
        if resp.status_code == 200:
            people = resp.json().get("people") or []
            for p in people:
                p_fn = (p.get("first_name") or "").strip()
                p_ln = (p.get("last_name") or "").strip()
                if is_valid_person_name(p_fn, p_ln, company_name):
                    org = p.get("organization") or {}
                    p_dom = clean_corporate_domain(org.get("primary_domain") or clean_dom)
                    raw_email = p.get("email") or ""
                    valid_email = clean_and_validate_email(raw_email, p_fn, p_ln, p_dom)
                    return {
                        "first_name": p_fn,
                        "last_name": p_ln,
                        "title": p.get("title") or "Chairman & Managing Partner",
                        "domain": p_dom,
                        "email": valid_email,
                        "linkedin": p.get("linkedin_url") or "",
                        "source": "Apollo.io Executive Search",
                    }
    except Exception:
        pass

    return None


def resolve_lead_entity(
    first_name: str,
    last_name: str,
    company_name: str,
    title: str = "",
    email: str = "",
    domain: str = "",
    allow_network: bool = False,
) -> Dict[str, str]:
    """
    Comprehensive entity resolution for an HNI lead:
    1. Validates existing person name (`is_valid_person_name`).
    2. If missing/placeholder, resolves against Curated GCC Registry (and optionally Apollo API).
    3. Cleans and validates corporate domain (`clean_corporate_domain`).
    4. Strictly validates email (`clean_and_validate_email`); sets to "N/A" unless verified against a real domain.
    """
    clean_dom = clean_corporate_domain(domain)
    if not clean_dom and email and "@" in email:
        clean_dom = clean_corporate_domain(email.split("@")[-1])

    fn = clean_bidi_and_punctuation(first_name or "")
    ln = clean_bidi_and_punctuation(last_name or "")
    comp = clean_bidi_and_punctuation(company_name or "")
    ttl = clean_bidi_and_punctuation(title or "")

    # Check if name is already valid
    name_ok = is_valid_person_name(fn, ln, comp)

    # Check curated registry if name is invalid OR domain is missing
    curated = lookup_curated_executive(comp, clean_dom)
    if curated:
        if not name_ok:
            fn = curated["first_name"]
            ln = curated["last_name"]
            ttl = curated["title"]
            name_ok = True
        if not clean_dom:
            clean_dom = curated["domain"]

    # Optional live Apollo lookup when network calls are enabled
    if allow_network and (not name_ok or not clean_dom or email in ("", "N/A")):
        apollo_res = resolve_via_apollo(comp, clean_dom, fn, ln)
        if apollo_res:
            if not name_ok:
                fn = apollo_res["first_name"]
                ln = apollo_res["last_name"]
                ttl = apollo_res["title"]
                name_ok = True
            if not clean_dom and apollo_res.get("domain"):
                clean_dom = apollo_res["domain"]
            if apollo_res.get("email") and apollo_res["email"] != "N/A":
                email = apollo_res["email"]

    # Validate email strictly (no @executive-gcc.com, no social media domains, no contact@)
    validated_email = clean_and_validate_email(email, fn, ln, clean_dom)

    return {
        "first_name": fn if name_ok else "",
        "last_name": ln if name_ok else "",
        "name_valid": name_ok,
        "title": ttl or "Chairman & Managing Partner",
        "company": comp,
        "domain": clean_dom,
        "email": validated_email,
    }
