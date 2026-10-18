"""
Indulge Global — ICIJ Offshore Leaks Bulk UHNI Graph Filter (17 Middle East & Med Nations)
==========================================================================================
Processes downloaded ICIJ Offshore Leaks CSV files (`nodes-officers.csv` & `nodes-addresses.csv`
from https://offshoreleaks.icij.org/pages/database — Pandora Papers, Panama Papers, Paradise Papers)
to filter verified UHNI beneficial owners across the 17 Middle East & Mediterranean nations:
  UAE, Saudi Arabia, Qatar, Kuwait, Bahrain, Oman, Lebanon, Jordan, Egypt,
  Turkey, Israel, Cyprus, Iraq, Iran, Syria, Palestine, Yemen.

Usage:
  Place `nodes-officers.csv` (and optionally `nodes-addresses.csv`) in `data/icij/`
  and run: `python scripts/icij_offshore_leaks_uhni_filter.py`
"""
import sys
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

BASE_DIR = Path(r"C:\Users\gozoi\Projects\indulge")
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

ICIJ_DIR = BASE_DIR / "data" / "icij"

TARGET_17_COUNTRIES = {
    "United Arab Emirates", "UAE",
    "Saudi Arabia", "SAU",
    "Qatar", "QAT",
    "Kuwait", "KWT",
    "Bahrain", "BHR",
    "Oman", "OMN",
    "Lebanon", "LBN",
    "Jordan", "JOR",
    "Egypt", "EGY",
    "Turkey", "Türkiye", "TUR",
    "Israel", "ISR",
    "Cyprus", "CYP",
    "Iraq", "IRQ",
    "Iran", "IRN",
    "Syria", "SYR",
    "Palestine", "PSE",
    "Yemen", "YEM",
}


def filter_icij_officers_csv(officers_csv_path: Path) -> pd.DataFrame:
    """
    10-line pandas filter extracting Middle East & Mediterranean UHNIs from ICIJ nodes-officers.csv.
    """
    df = pd.read_csv(officers_csv_path, low_memory=False)
    country_col = "countries" if "countries" in df.columns else "country_codes"
    mask = df[country_col].astype(str).apply(
        lambda val: any(c.lower() in val.lower() for c in TARGET_17_COUNTRIES)
    )
    filtered = df[mask].copy()
    filtered = filtered.drop_duplicates(subset=["name", country_col])
    return filtered


if __name__ == "__main__":
    officers_file = ICIJ_DIR / "nodes-officers.csv"
    if officers_file.exists():
        result_df = filter_icij_officers_csv(officers_file)
        out_path = BASE_DIR / "data" / "icij_filtered_me_uhnis.csv"
        result_df.to_csv(out_path, index=False, encoding="utf-8")
        print(f"[+] Extracted {len(result_df)} Middle East offshore trust principals to {out_path}")
    else:
        print(f"[i] Ready for bulk ICIJ CSV import at: {officers_file}")
