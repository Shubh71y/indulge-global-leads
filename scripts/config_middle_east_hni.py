"""
=============================================================================
INDULGE GLOBAL - MIDDLE EAST HNI & UHNI MASTER TARGET CONFIGURATION
=============================================================================
Curated target database for GCC & Middle East wealth hubs:
- UAE (Dubai, Abu Dhabi)
- Saudi Arabia (Riyadh, Jeddah)
- Qatar (Doha)
- Kuwait, Bahrain, Oman
=============================================================================
"""

GCC_LOCATIONS = [
    "Dubai", "Abu Dhabi", "UAE", "United Arab Emirates",
    "Riyadh", "Jeddah", "Saudi Arabia", "KSA",
    "Doha", "Qatar", "Kuwait", "Bahrain", "Manama", "Oman", "Muscat"
]

HNI_TITLES = [
    # Tier S: Family Office & Sovereign/Holding Leadership
    "Family Office Principal",
    "Family Office Founder",
    "Family Office CEO",
    "Family Office Managing Director",
    "Family Office Director",
    "Head of Family Office",
    "Chief Investment Officer",
    "Group Chairman",
    "Executive Chairman",
    "Holding Company Chairman",
    "Holding Company CEO",
    "Group Managing Director",
    "Group CEO",
    "Managing Partner",
    "Senior Partner",
    
    # Tier A: Direct HNI / UHNI Founders & Promoters
    "Founder",
    "Co-Founder",
    "Founder & CEO",
    "Founder & Chairman",
    "Chairman",
    "Managing Director",
    "Business Owner",
    "Owner",
    "Entrepreneur",
    "Serial Entrepreneur",
    "Family Business Owner",
    "Family Business Executive",
    "Promoter",
    
    # Tier B: Private Equity, Venture & Wealth
    "Private Equity Partner",
    "Venture Partner",
    "Investment Partner",
    "Investment Director",
    "Head of Investments",
    "Portfolio Manager",
    "Private Wealth Director",
    "Head of Private Wealth",
    "Private Banker",
    "Managing Director - Wealth Management"
]

GCC_COMPANIES = [
    # UAE Family Offices & Sovereign / Investment Holdings
    ("Al Futtaim Group", "alfuttaim.com", "UAE"),
    ("Al Habtoor Group", "habtoor.com", "UAE"),
    ("Al Tayer Group", "altayer.com", "UAE"),
    ("Majid Al Futtaim", "majidalfuttaim.com", "UAE"),
    ("Al Ghurair Group", "al-ghurair.com", "UAE"),
    ("Sobha Realty", "sobharealty.com", "UAE"),
    ("Damac Properties", "damacproperties.com", "UAE"),
    ("Emaar Properties", "emaar.com", "UAE"),
    ("Aldar Properties", "aldar.com", "UAE"),
    ("Nakheel", "nakheel.com", "UAE"),
    ("Mubadala Investment Company", "mubadala.com", "UAE"),
    ("ADQ", "adq.ae", "UAE"),
    ("Chimera Investment", "chimerainvestment.com", "UAE"),
    ("Ithmar Capital", "ithmar.com", "UAE"),
    ("Waha Capital", "wahacapital.com", "UAE"),
    ("Jumeirah Group", "jumeirah.com", "UAE"),
    ("Chalhoub Group", "chalhoubgroup.com", "UAE"),
    ("Al Jaber Group", "aljaber.com", "UAE"),
    ("Shamal Holding", "shamalholding.com", "UAE"),
    ("Dubai Holding", "dubaiholding.com", "UAE"),
    ("Lootah Holding", "sslootah.com", "UAE"),
    ("Al Rostamani Group", "alrostamanigroup.ae", "UAE"),
    ("Gargash Group", "gargash.ae", "UAE"),
    ("Al Batha Group", "albatha.com", "UAE"),
    ("Danube Group", "aldanube.com", "UAE"),
    ("Al Naboodah Group", "alnaboodah.com", "UAE"),
    ("Binghatti Holding", "binghatti.com", "UAE"),
    ("Omniyat", "omniyat.com", "UAE"),
    ("Azizi Developments", "azizidevelopments.com", "UAE"),

    # Saudi Arabia (KSA) Conglomerates & Family Offices
    ("Olayan Group", "olayan.com", "Saudi Arabia"),
    ("Al Rajhi Holding", "alrajhi-holding.com", "Saudi Arabia"),
    ("Dallah Albaraka", "albaraka.com", "Saudi Arabia"),
    ("Zahid Group", "zahid.com", "Saudi Arabia"),
    ("Sedco Holding", "sedco.com", "Saudi Arabia"),
    ("Abdul Latif Jameel", "alj.com", "Saudi Arabia"),
    ("Al Muhaidib Group", "muhaidib.com", "Saudi Arabia"),
    ("Al Faisaliah Group", "alfaisaliah.com", "Saudi Arabia"),
    ("Savola Group", "savola.com", "Saudi Arabia"),
    ("Kingdom Holding Company", "kingdom.com.sa", "Saudi Arabia"),
    ("Dar Al Arkan", "daralarkan.com", "Saudi Arabia"),
    ("Nesma Holding", "nesma.com", "Saudi Arabia"),
    ("Almarai", "almarai.com", "Saudi Arabia"),
    ("Rawabi Holding", "rawabiholding.com", "Saudi Arabia"),
    ("Astra Group", "astra.com.sa", "Saudi Arabia"),
    ("Red Sea Global", "redseaglobal.com", "Saudi Arabia"),
    ("Diriyah Company", "diriyah.sa", "Saudi Arabia"),
    ("Roshn Group", "roshn.sa", "Saudi Arabia"),

    # Qatar, Kuwait, Bahrain & Oman
    ("Al Faisal Holding", "alfaisalholding.com", "Qatar"),
    ("Power International Holding", "powerholding-intl.com", "Qatar"),
    ("Alfardan Group", "alfardan.com.qa", "Qatar"),
    ("Alshaya Group", "alshaya.com", "Kuwait"),
    ("Kanoo Group", "kanoo.com", "Bahrain"),
    ("Zubair Corporation", "zubaircorp.com", "Oman"),
    ("Khimji Ramdas", "khimji.com", "Oman"),
    ("Saud Bahwan Group", "saudbahwan.com", "Oman")
]

BOOLEAN_SEARCH_TEMPLATES = [
    '"{title}" "{location}" site:linkedin.com/in/',
    '"{company}" "{title}" site:linkedin.com/in/',
    '"{company}" "Family Office" site:linkedin.com/in/',
    '"{company}" "Managing Director" OR "Founder" site:linkedin.com/in/',
    '"{title}" "Dubai" OR "Riyadh" site:linkedin.com/in/',
    '"{title}" "Real Estate" "Dubai" site:linkedin.com/in/',
    '"{title}" "Investment" "Abu Dhabi" site:linkedin.com/in/'
]
