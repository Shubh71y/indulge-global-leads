r"""
=============================================================================
INDULGE GLOBAL - THREAD-SAFE DUAL DEDUPLICATING STORAGE
=============================================================================
Manages persistent CSV storage for Indulge Global GCC HNI/UHNI prospects:
- data/indulge_gcc_hni_master.csv
Strictly isolated within C:\Users\gozoi\Projects\indulge
=============================================================================
"""

import os
import sys
import csv
import time

csv.field_size_limit(2147483647)

INDULGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(INDULGE_DIR, "data")
MASTER_CSV = os.path.join(DATA_DIR, "indulge_gcc_hni_master.csv")

HEADERS = [
    "First Name", "Last Name", "Email", "Company", "Domain",
    "Role", "Country/City", "Status", "Source", "LinkedIn URL"
]

def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(MASTER_CSV) or os.path.getsize(MASTER_CSV) == 0:
        with open(MASTER_CSV, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)

def get_existing_keys():
    init_db()
    existing = set()
    if os.path.exists(MASTER_CSV):
        try:
            with open(MASTER_CSV, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for r in reader:
                    if len(r) > 2 and '@' in r[2]:
                        existing.add(r[2].strip().lower())
                    if len(r) > 1:
                        fn = r[0].strip().lower()
                        ln = r[1].strip().lower() if len(r) > 1 else ""
                        comp = r[3].strip().lower() if len(r) > 3 else ""
                        if fn and ln:
                            existing.add(f"{fn}|{ln}|{comp}")
        except Exception:
            pass
    return existing

def append_leads(new_rows):
    init_db()
    existing = get_existing_keys()
    to_add = []

    for r in new_rows:
        fn = r[0].strip().lower() if len(r) > 0 else ""
        ln = r[1].strip().lower() if len(r) > 1 else ""
        email = r[2].strip().lower() if len(r) > 2 else ""
        comp = r[3].strip().lower() if len(r) > 3 else ""

        key_email = email if email else None
        key_name = f"{fn}|{ln}|{comp}" if fn and ln else None

        # Check if already present on disk
        if (key_email and key_email in existing) or (key_name and key_name in existing):
            continue

        if key_email:
            existing.add(key_email)
        if key_name:
            existing.add(key_name)
        to_add.append(r)

    if not to_add:
        return 0

    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            with open(MASTER_CSV, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(to_add)
            return len(to_add)
        except PermissionError:
            time.sleep(0.5)
        except Exception as e:
            time.sleep(0.5)

    return 0
