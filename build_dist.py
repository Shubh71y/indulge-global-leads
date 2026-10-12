r"""
Indulge Global — Static Distribution Builder for Netlify / Vercel
===================================================================
Packages the dashboard HTML with all 893+ verified Pan-Middle East HNI leads
embedded directly as an offline/online dataset.
Includes client-side CSV generator, instant search, WhatsApp links, and filters.
"""
import sys
from pathlib import Path
import json

BASE_DIR = Path(r"C:\Users\gozoi\Projects\indulge")
sys.path.append(str(BASE_DIR / "scripts"))
import lead_store

DIST_DIR = BASE_DIR / "dist"
DIST_DIR.mkdir(parents=True, exist_ok=True)

leads = lead_store.get_all_leads()
print(f"[*] Packaging {len(leads)} leads into static deployment bundle...")

template_path = BASE_DIR / "templates" / "dashboard.html"
with open(template_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Replace loadLeads with dual-mode loader (fetch /api/leads if available, otherwise EMBEDDED_LEADS)
leads_json = json.dumps(leads, ensure_ascii=False)
embedded_snippet = f"""const EMBEDDED_LEADS = {leads_json};

async function loadLeads() {{
  try {{
    const res = await fetch('/api/leads');
    if (res.ok) {{
      const data = await res.json();
      if (data && data.leads && data.leads.length > 0) {{
        leadsData = data.leads;
        filteredData = leadsData;
        updateHeaderCounts();
        renderTable();
        return;
      }}
    }}
  }} catch(e) {{
    // Standalone static mode (Netlify / Vercel / GitHub Pages)
  }}
  leadsData = EMBEDDED_LEADS;
  filteredData = leadsData;
  updateHeaderCounts();
  renderTable();
}}"""

target_load = """async function loadLeads() {
  try {
    const res = await fetch('/api/leads');
    const data = await res.json();
    if (data && data.leads) {
      leadsData = data.leads;
      filteredData = leadsData;
      updateHeaderCounts();
      renderTable();
    }
  } catch(e) {
    console.error("Error fetching leads:", e);
  }
}"""

if target_load in html:
    html = html.replace(target_load, embedded_snippet)
else:
    print("[!] Target loadLeads function not found exactly as string, attempting regex substitution")
    import re
    html = re.sub(r'async function loadLeads\(\)\s*\{[\s\S]*?console\.error\("Error fetching leads:", e\);\s*\}\s*\}', embedded_snippet, html)

# 2. Client-side standalone CSV export (works without Python backend on Netlify)
standalone_csv = """function exportCSV() {
  if (!filteredData || filteredData.length === 0) {
    showToast("No leads available to export.");
    return;
  }
  const headers = ["First Name", "Last Name", "Role", "Company", "Domain", "Phone Number", "Email", "City/Country", "Deliverability Status", "Full Address", "Website", "Phone Type"];
  let csv = headers.join(",") + "\\n";
  filteredData.forEach(l => {
    const row = headers.map(h => {
      let val = String(l[h] || '').replace(/"/g, '""');
      return `"${val}"`;
    });
    csv += row.join(",") + "\\n";
  });
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `indulge_pan_middle_east_hnis_${filteredData.length}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  showToast(`Downloaded CSV dossier (${filteredData.length} records)!`);
}"""

target_export = """function exportCSV() {
  window.location.href = '/api/export/csv';
  showToast("Downloading full CSV export...");
}"""

if target_export in html:
    html = html.replace(target_export, standalone_csv)

# 3. Write out dist/index.html
out_file = DIST_DIR / "index.html"
with open(out_file, "w", encoding="utf-8") as f:
    f.write(html)

print(f"[+] Successfully generated standalone production bundle: {out_file} ({out_file.stat().st_size:,} bytes)")
