r"""
=============================================================================
INDULGE GLOBAL - MASTER DATABASE INSPECTION & SUMMARY STATS
=============================================================================
Quick diagnostic utility to view the health, totals, and distributions
of mined Middle East HNI / UHNI leads in C:\Users\gozoi\Projects\indulge
=============================================================================
"""

import os
import sys
import csv
from collections import Counter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DB_PATH = r"C:\Users\gozoi\Projects\indulge\data\indulge_gcc_hni_master.csv"

def inspect_db():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file does not exist yet: {DB_PATH}")
        return

    with open(DB_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        rows = list(reader)

    print("=" * 65)
    print("💎 INDULGE GLOBAL - MIDDLE EAST HNI / UHNI PIPELINE STATS")
    print("=" * 65)
    print(f"📁 Target Database: {DB_PATH}")
    print(f"📊 Total Leads Collected: {len(rows):,}")

    countries = Counter()
    statuses = Counter()
    companies = Counter()

    for r in rows:
        country = r[6] if len(r) > 6 else "Unknown"
        status = r[7] if len(r) > 7 else "Unknown"
        comp = r[3] if len(r) > 3 else "Unknown"

        countries[country] += 1
        statuses[status] += 1
        companies[comp] += 1

    print("\n🌍 Geographic Distribution:")
    for c, cnt in countries.most_common(8):
        print(f"  • {c}: {cnt:,} leads")

    print("\n⚡ Deliverability Statuses:")
    for s, cnt in statuses.most_common():
        print(f"  • {s}: {cnt:,} leads")

    print("\n🏢 Top Represented Entities:")
    for comp, cnt in companies.most_common(10):
        print(f"  • {comp}: {cnt} leads")

    print("=" * 65)

    if rows:
        print("\n🔍 Sample Mined Prospects (Last 5):")
        for r in rows[-5:]:
            fn = r[0] if len(r) > 0 else ""
            ln = r[1] if len(r) > 1 else ""
            em = r[2] if len(r) > 2 else ""
            co = r[3] if len(r) > 3 else ""
            ro = r[5] if len(r) > 5 else ""
            print(f"  ⭐ {fn} {ln} | {ro} @ {co} -> {em}")
        print("=" * 65)

if __name__ == "__main__":
    inspect_db()
