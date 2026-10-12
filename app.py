r"""
Indulge Global - HNI Lead Intelligence Dashboard
=================================================
Flask backend serving the luxury lead mining dashboard.

Backend API:
  GET  /                      -> Dashboard SPA
  GET  /api/leads             -> All leads from HNI.xlsx (JSON)
  GET  /api/stats             -> Summary statistics
  POST /api/mine              -> Launch a mining run
  GET  /api/miners             -> List active miner processes
  POST /api/miners/<pid>/kill -> Kill a specific miner
  GET  /api/export/csv        -> Download leads as CSV

Data path: C:\Users\gozoi\Projects\indulge\data\HNI.xlsx
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os
import json
import signal
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, jsonify, request, Response

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SCRIPTS_DIR = BASE_DIR / "scripts"
HNI_XLSX = DATA_DIR / "HNI.xlsx"
HNI_CSV = DATA_DIR / "indulge_gcc_hni_master.csv"
PYTHON_EXE = sys.executable  # Use whichever Python launched this server

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Active miners registry  { pid: {info} }
# ---------------------------------------------------------------------------
active_miners = {}
miners_lock = threading.Lock()


import sys
sys.path.append(str(SCRIPTS_DIR))
try:
    import lead_store
except Exception:
    lead_store = None

def _read_hni_xlsx():
    """Read leads from durable store and fallback to HNI.xlsx."""
    if lead_store:
        try:
            leads = lead_store.get_all_leads()
            if leads:
                return leads
        except Exception:
            pass
    import pandas as pd
    if not HNI_XLSX.exists():
        return []
    try:
        df = pd.read_excel(str(HNI_XLSX))
        df = df.fillna("")
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"[WARNING] Could not read HNI.xlsx: {e}")
        return []


def _read_hni_csv():
    """Fallback: read CSV mirror."""
    import pandas as pd
    if not HNI_CSV.exists():
        return []
    try:
        df = pd.read_csv(str(HNI_CSV))
        df = df.fillna("")
        return df.to_dict(orient="records")
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/leads")
def api_leads():
    """Return all leads as JSON array."""
    leads = _read_hni_xlsx()
    if not leads:
        leads = _read_hni_csv()
    return jsonify({"leads": leads, "count": len(leads), "timestamp": datetime.now().isoformat()})


@app.route("/api/stats")
def api_stats():
    """Return summary statistics."""
    leads = _read_hni_xlsx()
    if not leads:
        leads = _read_hni_csv()

    total = len(leads)
    with_phone = sum(1 for l in leads if l.get("Phone Number", ""))
    with_email = sum(1 for l in leads if l.get("Email", ""))
    verified_email = sum(1 for l in leads if "Deliverable" in str(l.get("Deliverability Status", "")))
    risky_email = sum(1 for l in leads if "Risky" in str(l.get("Deliverability Status", "")))

    # Country/city breakdown
    cities = {}
    for l in leads:
        city = str(l.get("City/Country", "Unknown"))
        cities[city] = cities.get(city, 0) + 1

    # Source breakdown
    sources = {}
    for l in leads:
        src = str(l.get("Source", "Unknown"))
        # Shorten source names
        if "Apify" in src:
            src = "Apify Google Maps"
        elif "Tavily" in src:
            src = "Tavily SERP"
        elif "SMTP" in src:
            src = "SMTP Verified"
        sources[src] = sources.get(src, 0) + 1

    # Companies
    companies = {}
    for l in leads:
        comp = str(l.get("Company", "Unknown"))
        if comp:
            companies[comp] = companies.get(comp, 0) + 1

    with miners_lock:
        running_miners = len(active_miners)

    return jsonify({
        "total_leads": total,
        "with_phone": with_phone,
        "with_email": with_email,
        "verified_email": verified_email,
        "risky_email": risky_email,
        "cities": cities,
        "sources": sources,
        "top_companies": dict(sorted(companies.items(), key=lambda x: -x[1])[:15]),
        "running_miners": running_miners,
        "last_updated": datetime.now().isoformat(),
        "xlsx_size_kb": round(HNI_XLSX.stat().st_size / 1024, 1) if HNI_XLSX.exists() else 0,
    })


@app.route("/api/mine", methods=["POST"])
def api_mine():
    """Launch a mining run with optional custom parameters."""
    data = request.get_json(force=True) if request.data else {}
    miner_type = data.get("type", "full")  # full | apify | tavily | mobile
    location = data.get("location", "Dubai, UAE")
    query = data.get("query", "")
    target_count = data.get("target_count", 100)

    # Build a one-shot miner script dynamically
    script_name = None
    script_args = []

    if miner_type == "full":
        script_name = "mine_500_hni_master.py"
    elif miner_type == "apify":
        script_name = "apify_full_hni_miner.py"
    elif miner_type == "tavily":
        script_name = "mine_middle_east_hni.py"
    elif miner_type == "mobile":
        script_name = "mine_direct_hni_mobiles.py"
    elif miner_type == "custom":
        # Generate a custom one-shot script
        script_name = _generate_custom_miner(location, query, target_count)
    else:
        return jsonify({"error": f"Unknown miner type: {miner_type}"}), 400

    script_path = SCRIPTS_DIR / script_name if miner_type != "custom" else BASE_DIR / "scripts" / script_name

    if not script_path.exists():
        return jsonify({"error": f"Script not found: {script_path}"}), 404

    # Launch as subprocess
    proc = subprocess.Popen(
        [PYTHON_EXE, "-u", str(script_path)] + script_args,
        cwd=str(BASE_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )

    info = {
        "pid": proc.pid,
        "type": miner_type,
        "script": script_name,
        "location": location,
        "query": query,
        "target_count": target_count,
        "started_at": datetime.now().isoformat(),
        "status": "running",
        "log_lines": [],
    }

    with miners_lock:
        active_miners[proc.pid] = info

    # Background thread to capture output
    def _capture(proc, pid):
        try:
            for line in proc.stdout:
                line = line.rstrip()
                with miners_lock:
                    if pid in active_miners:
                        active_miners[pid]["log_lines"].append(line)
                        # Keep only last 200 lines
                        if len(active_miners[pid]["log_lines"]) > 200:
                            active_miners[pid]["log_lines"] = active_miners[pid]["log_lines"][-200:]
        except Exception:
            pass
        finally:
            proc.wait()
            with miners_lock:
                if pid in active_miners:
                    active_miners[pid]["status"] = "finished"
                    active_miners[pid]["finished_at"] = datetime.now().isoformat()

    t = threading.Thread(target=_capture, args=(proc, proc.pid), daemon=True)
    t.start()

    return jsonify({"message": f"Miner '{miner_type}' launched", "pid": proc.pid, "script": script_name})


@app.route("/api/miners")
def api_miners():
    """List active/recent miner processes."""
    with miners_lock:
        miners_list = []
        for pid, info in active_miners.items():
            miners_list.append({
                "pid": pid,
                "type": info["type"],
                "script": info["script"],
                "location": info.get("location", ""),
                "query": info.get("query", ""),
                "started_at": info["started_at"],
                "status": info["status"],
                "finished_at": info.get("finished_at", ""),
                "last_log": info["log_lines"][-5:] if info["log_lines"] else [],
            })
    return jsonify({"miners": miners_list})


@app.route("/api/miners/<int:pid>/kill", methods=["POST"])
def api_kill_miner(pid):
    """Kill a running miner."""
    with miners_lock:
        info = active_miners.get(pid)
        if not info:
            return jsonify({"error": "Miner not found"}), 404

    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
        else:
            os.kill(pid, signal.SIGTERM)
        with miners_lock:
            if pid in active_miners:
                active_miners[pid]["status"] = "killed"
                active_miners[pid]["finished_at"] = datetime.now().isoformat()
        return jsonify({"message": f"Miner PID {pid} killed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/miners/<int:pid>/logs")
def api_miner_logs(pid):
    """Get full log output for a miner."""
    with miners_lock:
        info = active_miners.get(pid)
        if not info:
            return jsonify({"error": "Miner not found"}), 404
        return jsonify({"pid": pid, "log_lines": info["log_lines"]})


@app.route("/api/export/csv")
def api_export_csv():
    """Download leads as CSV."""
    import pandas as pd
    leads = _read_hni_xlsx()
    if not leads:
        leads = _read_hni_csv()
    if not leads:
        return jsonify({"error": "No leads found"}), 404
    df = pd.DataFrame(leads)
    csv_data = df.to_csv(index=False)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=HNI_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"}
    )


def _generate_custom_miner(location, query, target_count):
    """Generate a one-shot custom miner script for user-specified parameters."""
    script_name = f"custom_miner_{int(time.time())}.py"
    script_content = f'''# Auto-generated custom miner
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os, json, time, requests, pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
HNI_XLSX = DATA_DIR / "HNI.xlsx"
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")

location = """{location}"""
query = """{query}"""
target_count = {target_count}

print(f"[Custom Miner] Location: {{location}}")
print(f"[Custom Miner] Query: {{query}}")
print(f"[Custom Miner] Target: {{target_count}} leads")

# Use Apify Google Places
search_queries = [query] if query else [
    f"Luxury Real Estate {{location}}",
    f"Private Wealth Management {{location}}",
    f"Family Office {{location}}",
    f"Holding Company {{location}}",
    f"Investment Firm {{location}}",
]

all_leads = []
for sq in search_queries:
    print(f"\\n[Apify] Mining: '{{sq}}'...")
    try:
        run_url = "https://api.apify.com/v2/acts/compass~crawler-google-places/runs"
        payload = {{"searchStringsArray": [sq], "maxCrawledPlacesPerSearch": 20, "language": "en", "maxImages": 0}}
        resp = requests.post(f"{{run_url}}?token={{APIFY_TOKEN}}", json=payload, timeout=30)
        run_data = resp.json()
        run_id = run_data.get("data", {{}}).get("id", "")
        if not run_id:
            print(f"  [!] No run ID")
            continue

        # Wait for completion
        for _ in range(60):
            time.sleep(5)
            status_resp = requests.get(f"https://api.apify.com/v2/actor-runs/{{run_id}}?token={{APIFY_TOKEN}}", timeout=15)
            status = status_resp.json().get("data", {{}}).get("status", "")
            if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
                break

        if status != "SUCCEEDED":
            print(f"  [!] Run {{status}}")
            continue

        dataset_id = status_resp.json().get("data", {{}}).get("defaultDatasetId", "")
        items_resp = requests.get(f"https://api.apify.com/v2/datasets/{{dataset_id}}/items?token={{APIFY_TOKEN}}", timeout=30)
        places = items_resp.json()
        print(f"  [+] Got {{len(places)}} results")

        for place in places:
            phone = place.get("phone", "")
            name = place.get("title", "Unknown")
            website = place.get("website", "")
            address = place.get("address", "")
            domain = ""
            if website:
                from urllib.parse import urlparse
                domain = urlparse(website).netloc.replace("www.", "")
            
            lead = {{
                "First Name": name.split()[0] if name.split() else name,
                "Last Name": " ".join(name.split()[1:]) if len(name.split()) > 1 else "",
                "Role": "Business Contact",
                "Company": name,
                "Domain": domain,
                "Phone Number": phone,
                "Email": f"info@{{domain}}" if domain else "",
                "City/Country": location,
                "Deliverability Status": "Pending",
                "Full Address": address,
                "Website": website,
                "Source": "Custom Miner - Apify",
                "Phone Type": "Office" if phone else "",
            }}
            all_leads.append(lead)

    except Exception as e:
        print(f"  [ERROR] {{e}}")

if all_leads:
    print(f"\\n[+] Writing {{len(all_leads)}} leads to HNI.xlsx...")
    new_df = pd.DataFrame(all_leads)
    if HNI_XLSX.exists():
        existing = pd.read_excel(str(HNI_XLSX))
        combined = pd.concat([existing, new_df], ignore_index=True)
        combined.drop_duplicates(subset=["Phone Number"], keep="first", inplace=True)
    else:
        combined = new_df
    combined.to_excel(str(HNI_XLSX), index=False, engine="openpyxl")
    print(f"[+] Done! Total: {{len(combined)}} leads in HNI.xlsx")
else:
    print("[!] No leads found")
'''
    script_path = SCRIPTS_DIR / script_name
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    return script_name


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("  INDULGE GLOBAL - HNI Lead Intelligence Dashboard")
    print("  http://localhost:5000")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
