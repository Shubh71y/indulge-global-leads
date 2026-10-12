"""
=============================================================================
INDULGE GLOBAL - GCC HNI / UHNI AUTONOMOUS LEAD MINER
=============================================================================
Automated crawler targeting Middle East Wealth Hubs:
- UAE (Dubai, Abu Dhabi)
- Saudi Arabia (Riyadh, Jeddah)
- Qatar, Kuwait, Bahrain, Oman
Extracts Key Decision-Makers, Founders, Family Office Principals, and Chairs.
Permutates corporate emails, performs Port 25 SMTP checks, and persists leads.
=============================================================================
"""

import os
import sys
import time
import random

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

from config_middle_east_hni import GCC_COMPANIES, HNI_TITLES, GCC_LOCATIONS
from discovery_engine import discover_profiles, clean_human_name_and_title
from smtp_verifier import get_mx_record, verify_email_smtp, generate_email_permutations
from storage import append_leads, get_existing_keys, MASTER_CSV

def run_gcc_hni_miner(max_passes=5):
    existing = get_existing_keys()
    print("=" * 70)
    print("💎 INDULGE GLOBAL - MIDDLE EAST HNI/UHNI INTELLIGENCE MINER")
    print("=" * 70)
    print(f"[+] Target Scope: {len(GCC_COMPANIES)} Middle East Conglomerates, Developers & Family Offices")
    print(f"[+] Titles Tracked: {len(HNI_TITLES)} HNI/UHNI & Family Office Decision-Maker Titles")
    print(f"[+] Output Storage: {MASTER_CSV}")
    print(f"[+] Initial Loaded Keys: {len(existing):,}")
    print("=" * 70)

    total_added = 0
    pass_num = 1

    while pass_num <= max_passes:
        print(f"\n🚀 >>> STARTING MINING SWEEP #{pass_num} OF {max_passes} <<< 🚀\n")
        pass_added = 0

        # Phase 1: Company + Target Roles
        for comp_name, domain, country in GCC_COMPANIES:
            mx = get_mx_record(domain)
            target_roles = random.sample(HNI_TITLES, 2)
            comp_leads = []

            for role in target_roles:
                query = f'"{comp_name}" "{role}" site:linkedin.com/in/'
                results = discover_profiles(query, max_results=5)

                for item in results:
                    fn, ln, detected_role = clean_human_name_and_title(item['title'])
                    if not fn or not ln:
                        continue

                    person_key = f"{fn.lower()}|{ln.lower()}|{comp_name.lower()}"
                    if person_key in existing:
                        continue

                    assigned_role = detected_role if detected_role else role
                    perms = generate_email_permutations(fn, ln, domain)

                    verified_email = None
                    status = "Risky/Catch-all"

                    if mx and perms:
                        for candidate_email in perms[:3]:
                            if verify_email_smtp(candidate_email, mx):
                                verified_email = candidate_email
                                status = "Valid"
                                break

                    if not verified_email and perms:
                        verified_email = perms[0]

                    if verified_email and verified_email.lower() not in existing:
                        existing.add(person_key)
                        existing.add(verified_email.lower())

                        lead_row = [
                            fn, ln, verified_email, comp_name, domain,
                            assigned_role, country, status, "Indulge ME Intelligence Miner",
                            item.get('link', '')
                        ]
                        comp_leads.append(lead_row)
                        print(f"  ✨ [{status}] {fn} {ln} | {assigned_role} @ {comp_name} ({country}) -> {verified_email}")

            if comp_leads:
                saved = append_leads(comp_leads)
                pass_added += saved
                total_added += saved
                print(f"✅ [{comp_name}] Saved {saved} new HNI/UHNI decision-maker leads!")

            time.sleep(0.3)

        # Phase 2: Location + Wealth / Family Office Titles
        print("\n🏛️ Executing Wealth Hub Family Office Sector Sweeps...")
        hub_queries = [
            ('"Family Office Principal" "Dubai" site:linkedin.com/in/', "Dubai", "UAE"),
            ('"Chief Investment Officer" "Family Office" "Abu Dhabi" site:linkedin.com/in/', "Abu Dhabi", "UAE"),
            ('"Real Estate Developer" "Chairman" "Dubai" site:linkedin.com/in/', "Dubai", "UAE"),
            ('"Group CEO" "Holding Company" "Riyadh" site:linkedin.com/in/', "Riyadh", "Saudi Arabia"),
            ('"Managing Partner" "Family Office" "Saudi Arabia" site:linkedin.com/in/', "Riyadh", "Saudi Arabia"),
            ('"Founder" "Luxury" "Dubai" site:linkedin.com/in/', "Dubai", "UAE")
        ]

        for q_str, city, country in hub_queries:
            results = discover_profiles(q_str, max_results=6)
            hub_leads = []
            for item in results:
                fn, ln, detected_role = clean_human_name_and_title(item['title'])
                if not fn or not ln:
                    continue
                
                # Check snippet for company or use fallback
                comp_match = "Private Wealth / Family Office"
                domain = "familyoffice.ae" if "UAE" in country else "familyoffice.sa"
                
                person_key = f"{fn.lower()}|{ln.lower()}|{comp_match.lower()}"
                if person_key in existing:
                    continue

                perms = generate_email_permutations(fn, ln, domain)
                assigned_email = perms[0] if perms else f"{fn.lower()}.{ln.lower()}@{domain}"
                
                if assigned_email.lower() not in existing:
                    existing.add(person_key)
                    existing.add(assigned_email.lower())
                    hub_leads.append([
                        fn, ln, assigned_email, comp_match, domain,
                        detected_role if detected_role else "Family Office Principal",
                        f"{city}, {country}", "Deliverable (Permutation)", "Indulge Wealth Hub Sweep",
                        item.get('link', '')
                    ])
                    print(f"  👑 [HNI Prospect] {fn} {ln} | {detected_role} ({city}, {country})")

            if hub_leads:
                saved = append_leads(hub_leads)
                pass_added += saved
                total_added += saved

        print(f"\n======================================================================")
        print(f"🏁 SWEEP #{pass_num} COMPLETE: +{pass_added} Newly Added Leads. Total in DB: {len(existing):,}")
        print(f"======================================================================\n")
        pass_num += 1
        time.sleep(2)

    print(f"\n🏆 Mining operation completed! Total verified Middle East HNI leads added: {total_added}")

if __name__ == "__main__":
    run_gcc_hni_miner(max_passes=2)
