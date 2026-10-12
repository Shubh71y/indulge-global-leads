# Indulge Global — VIP Concierge Outbound & Lead Discovery Platform

Ultra-luxury concierge outbound acquisition and intelligence engine targeting High-Net-Worth Individuals (HNIs) and Ultra-High-Net-Worth Individuals (UHNIs) across all 17 Middle East and Mediterranean sovereign nations.

---

## 🚀 Live Access Points
* **Live Edge URL:** [https://arbitration-michelle-zinc-tomorrow.trycloudflare.com](https://arbitration-michelle-zinc-tomorrow.trycloudflare.com)
* **Local Production Engine:** `http://localhost:5000` (Waitress WSGI Server)
* **Master Excel Dataset:** `data/HNI.xlsx` (Synchronized in real-time)

---

## 🏛️ Sovereign Coverage (17 Nations)
1. **Bahrain** (Manama, Financial Harbour, Seef)
2. **Cyprus** (Limassol Marina, Nicosia)
3. **Egypt** (New Cairo, Zamalek, Giza)
4. **Iran** (Tehran)
5. **Iraq** (Baghdad, Erbil)
6. **Israel** (Tel Aviv, Herzliya Pituach)
7. **Jordan** (Amman Abdoun, Sweifieh)
8. **Kuwait** (Kuwait City Sharq, KIPCO)
9. **Lebanon** (Beirut Achrafieh, Waterfront)
10. **Oman** (Muscat Al Qurum, Al Mouj)
11. **Palestine** (Ramallah, East Jerusalem)
12. **Qatar** (Doha West Bay, Lusail Marina, The Pearl)
13. **Saudi Arabia** (Riyadh KAFD, Olaya, Jeddah Corniche, Khobar)
14. **Syria** (Damascus)
15. **Turkey (Türkiye)** (Istanbul Levent, Maslak, Bodrum)
16. **United Arab Emirates (UAE)** (Dubai DIFC, Palm Jumeirah, Abu Dhabi ADGM)
17. **Yemen** (Sana'a, Aden)

---

## 🛠️ Architecture Stack
* **Frontend:** Bogdan Falin / QClay Finance Management Dashboard UI (Dribbble #23245345)
* **Backend:** Python Flask 3.1, Waitress WSGI Multi-Threaded Server (6 workers)
* **Discovery Workers:** Apify Google Places Actor (`compass~crawler-google-places`), Tavily AI OSINT Boolean Dorking
* **Edge Tunnel:** Cloudflare Zero-Trust QUIC/TLS 1.3 Tunnel (`pycloudflared`)
* **Persistence:** Concurrency-safe atomic append-only JSONL (`data/leads_store.jsonl`) + Excel sync (`data/HNI.xlsx`)
* **Outreach:** Universal WhatsApp direct deep-link scheme (`https://wa.me/`)

---

## 📖 Documentation
Detailed technical manuals and operational guides are available in [`docs/`](docs/):
* `docs/Indulge_Global_Technical_Architecture_Workflow.pdf` — Complete systems manual with data schemas, third-party platforms matrix, and WSGI threading.
* `docs/Indulge_Global_Client_Walkthrough_Guide.pdf` — Client-facing operational guide with UI tour and pitch scripts.
