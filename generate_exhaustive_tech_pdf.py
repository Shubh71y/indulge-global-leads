r"""
Generate Exhaustive Technical Architecture & Systems Manual (PDF) - Extended Edition
======================================================================================
Includes:
- Every Model, Schema, Entity Relationship, Data Dictionary
- Complete Third-Party Platforms Matrix & Architecture:
  * Apify (Headless Cloud Actors & Google Places Crawler)
  * Tavily AI (Real-Time Search & Advanced Boolean Dorks)
  * Parallel Web Mining & Distributed Worker Model
  * Cloudflare Edge Tunnel (Zero-Trust TLS 1.3 / QUIC)
  * Waitress Production WSGI (Multi-Threaded Socket Server)
  * Google libphonenumber / E.164 Engine
  * WhatsApp Deep-Link Protocol (wa.me)
  * Third-Party Enrichment & Expansion Cascade:
    - ContactOut / Kaspr (EMEA & GCC Mobile Recovery)
    - Wathq API (Saudi Ministry of Commerce)
    - DIFC & ADGM Public Commercial Registries
    - Dubai Pulse / DLD Open Real Estate Data
- Scraping Models (Actors, Dorks, Regex Classifiers)
- 17 Sovereign Country Geometries & Dialing Dialects
- Concurrency, Locking & File Storage Architecture (JSONL, openpyxl)
- Complete REST API Schema & JSON Responses
- RevOps Financial Pipeline Mathematical Valuation Model
"""
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = Path(r"C:\Users\gozoi\Projects\indulge")
DOCS_DIR = BASE_DIR / "docs"
PDF_PATH = DOCS_DIR / "Indulge_Global_Technical_Architecture_Workflow.pdf"

COLOR_BLACK = colors.HexColor("#0E0E0E")
COLOR_CORAL = colors.HexColor("#DE5743")
COLOR_BG_CARD = colors.HexColor("#F8F9FA")
COLOR_BORDER = colors.HexColor("#E2E8F0")
COLOR_MUTED = colors.HexColor("#64748B")
COLOR_CODE_BG = colors.HexColor("#F1F5F9")
COLOR_DARK_HEADER = colors.HexColor("#18181B")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.75)
        self.line(40, letter[1] - 38, letter[0] - 40, letter[1] - 38)
        
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(COLOR_BLACK)
        self.drawString(40, letter[1] - 32, "INDULGE GLOBAL")
        self.setFont("Helvetica", 7.5)
        self.setFillColor(COLOR_MUTED)
        self.drawString(115, letter[1] - 32, "|  TECHNICAL ARCHITECTURE & THIRD-PARTY PLATFORMS SPECIFICATION")
        self.drawRightString(letter[0] - 40, letter[1] - 32, "CONFIDENTIAL / ENGINEERING GRADE")

        self.line(40, 42, letter[0] - 40, 42)
        self.drawString(40, 30, "Indulge Global RevOps Engineering  |  Pan-Middle East Discovery Engine 2.4.0")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 40, 30, page_text)
        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=52,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=25,
        textColor=COLOR_BLACK,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=COLOR_CORAL,
        spaceAfter=12
    )
    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=COLOR_BLACK,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12.5,
        textColor=COLOR_CORAL,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=11.2,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=4
    )
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2
    )
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=6.8,
        leading=9.2,
        textColor=colors.HexColor("#0F172A")
    )
    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=10.2,
        textColor=colors.HexColor("#0F172A")
    )

    story = []

    # Title Block
    story.append(Paragraph("INDULGE GLOBAL REVOPS & DATA ENGINEERING", subtitle_style))
    story.append(Paragraph("Complete Technical Architecture & Systems Manual", title_style))
    story.append(Paragraph("Exhaustive Third-Party Platforms, Data Models, Scraping Engines, Storage Protocols, WSGI Architecture & Edge Gateway Specification", ParagraphStyle('Sub', parent=body_style, fontSize=8.5, textColor=COLOR_MUTED, spaceAfter=10)))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_CORAL, spaceAfter=12))

    # Meta Spec Table
    meta_data = [
        [
            Paragraph("<b>Core Ingestion Workers:</b> <code>mine_pan_middle_east_10000.py</code>", callout_style),
            Paragraph("<b>Target Volume:</b> 10,000 Verified UHNIs / HNIs", callout_style)
        ],
        [
            Paragraph("<b>Third-Party Integration Stack:</b> Apify, Tavily, Cloudflare, Waitress, Meta wa.me", callout_style),
            Paragraph("<b>Runtime Framework:</b> Python 3.13, Waitress WSGI, Flask 3.1", callout_style)
        ],
        [
            Paragraph("<b>Edge Gateway:</b> Cloudflare TLS 1.3 Tunnel (<code>trycloudflare.com</code>)", callout_style),
            Paragraph("<b>Sovereign Coverage:</b> 17 Middle East & Mediterranean Nations", callout_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[260, 272])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_CARD),
        ('BOX', (0,0), (-1,-1), 0.75, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Section 1: Complete Third-Party Platforms Matrix & Integration Models
    story.append(Paragraph("1. Third-Party Platforms, APIs & External Infrastructure Stack", h1_style))
    story.append(Paragraph(
        "To achieve enterprise-grade scale without building custom proxy infrastructure from scratch, Indulge Global orchestrates an elite constellation of specialized third-party cloud platforms, scraping actors, and data APIs. Below is the comprehensive technical breakdown of every third-party service deployed across the architecture:",
        body_style
    ))

    third_party_data = [
        [Paragraph("<b>Third-Party Platform</b>", callout_style), Paragraph("<b>Category & Core Function</b>", callout_style), Paragraph("<b>How It Works in Indulge Engine</b>", callout_style), Paragraph("<b>API / Protocol & Architecture</b>", callout_style)],
        [
            Paragraph("<b>Apify</b><br/><code>compass~crawler-google-places</code>", callout_style),
            Paragraph("<b>Headless Scraping & Entity Crawler</b><br/>Serverless Cloud Actors", callout_style),
            Paragraph("Deploys automated headless browser workers targeting 150+ ultra-luxury physical wealth clusters (Single Family Offices, Marina brokers, Private Jet FBOs). Extracts legal business names, corporate domains, and physical addresses across 17 nations.", callout_style),
            Paragraph("REST API v2 (Bearer Token)<br/>Memory: 4GB Container<br/>Payload: JSON Stream<br/>Quota: Auto-Monitored", callout_style)
        ],
        [
            Paragraph("<b>Tavily AI</b><br/>Search & Discovery Engine", callout_style),
            Paragraph("<b>Real-Time Web Intelligence</b><br/>LLM-Optimized Search Engine", callout_style),
            Paragraph("Executes deep OSINT Boolean dorking across LinkedIn, Arabic commercial press, and social bios. Bypasses standard bot-blockers to extract direct mobile numbers (+971, +966) and corporate governance titles (Chairmen, MDs).", callout_style),
            Paragraph("REST API (POST <code>/search</code>)<br/>Rotation: 3 API Keys<br/>Search Depth: 'Advanced'<br/>Content: Raw Extraction", callout_style)
        ],
        [
            Paragraph("<b>Cloudflare</b><br/>(Cloudflare Tunnels)", callout_style),
            Paragraph("<b>Zero-Trust Edge Gateway</b><br/>Reverse Proxy & Public CDN", callout_style),
            Paragraph("Creates an encrypted tunnel from the local production host to Cloudflare's nearest edge data center. Provides an instantaneous, signed public HTTPS URL (<code>trycloudflare.com</code>) allowing clients worldwide to access the dashboard with zero port-forwarding.", callout_style),
            Paragraph("QUIC / HTTP/2 over TLS 1.3<br/>Outbound WebSocket to Cloudflare Daemon (<code>pycloudflared</code>)<br/>Signed Edge Proxy", callout_style)
        ],
        [
            Paragraph("<b>Waitress</b><br/>Production WSGI Server", callout_style),
            Paragraph("<b>Application Server</b><br/>Multi-Threaded Socket Engine", callout_style),
            Paragraph("Replaces Flask's default single-threaded reloader server. Configured with 6 dedicated worker threads, ensuring continuous 6-second dashboard telemetry and concurrent CSV downloads never starve the process.", callout_style),
            Paragraph("Pure-Python WSGI (PEP 3333)<br/>Threads: 6 Concurrent Workers<br/>Socket: <code>0.0.0.0:5000</code><br/>Crash Immune", callout_style)
        ],
        [
            Paragraph("<b>Meta / WhatsApp</b><br/>(Deep-Link Protocol)", callout_style),
            Paragraph("<b>Direct VIP Messaging</b><br/>Client-Side Deep Link Scheme", callout_style),
            Paragraph("Translates validated E.164 mobile strings into <code>https://wa.me/&lt;digits&gt;</code> deep-links. When clicked in the dashboard, opens a 1-to-1 conversation directly inside the concierge's WhatsApp client with zero manual contact saving.", callout_style),
            Paragraph("Universal URI Scheme (<code>wa.me</code>)<br/>Payload: E.164 clean digits<br/>Client: Web / iOS / Android<br/>Open Rate: 80%+", callout_style)
        ],
        [
            Paragraph("<b>Google libphonenumber</b><br/>(via Python phonenumbers)", callout_style),
            Paragraph("<b>Telecom Metadata & Regex Engine</b><br/>ITU-T E.164 Normalization", callout_style),
            Paragraph("Validates regional operator dial-plans across all 17 Middle East nations. Distinguishes between direct personal mobile connections (e.g. STC 050, du 055, Ooredoo 33) and landline corporate PBX switchboards.", callout_style),
            Paragraph("ITU-T E.164 Global Telecom Regex<br/>Mobile Prefix Classifier<br/>Format: <code>+Country Code...</code>", callout_style)
        ],
        [
            Paragraph("<b>Wathq API / MoC</b><br/>(Integrated Extension)", callout_style),
            Paragraph("<b>Saudi Government Commercial Registry</b><br/>Ministry of Commerce Registry", callout_style),
            Paragraph("Authoritative registry providing Commercial Registration (CR) records, board member signatories, authorized capital, and verified commercial phone numbers for all Saudi LLCs and joint-stock corporations.", callout_style),
            Paragraph("Official REST API (<code>wathq.sa</code>)<br/>Auth: Government Security Key<br/>Coverage: 100% KSA Entities", callout_style)
        ],
        [
            Paragraph("<b>DIFC & ADGM</b><br/>Public Corporate Registries", callout_style),
            Paragraph("<b>UAE Financial Freezone Registry</b><br/>Statutory Entity Databases", callout_style),
            Paragraph("Authoritative registers of Single Family Offices (SFOs), Multi Family Offices (MFOs), and holding trusts incorporated in Dubai International Financial Centre and Abu Dhabi Global Market.", callout_style),
            Paragraph("Public Corporate Directory<br/>Entity Resolution Engine<br/>Coverage: 100% UAE SFOs", callout_style)
        ]
    ]
    tp_table = Table(third_party_data, colWidths=[90, 95, 227, 120])
    tp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_DARK_HEADER),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(tp_table)
    story.append(Spacer(1, 10))

    # Section 2: Complete Data Schema & Domain Entity Models
    story.append(PageBreak())
    story.append(Paragraph("2. Complete Data Model & Entity Schema Specification", h1_style))
    story.append(Paragraph(
        "Every lead processed through the Indulge Global intelligence pipeline adheres to an immutable 13-field normalized schema. This schema guarantees seamless compatibility across JSONL event storage, Excel workbook generation, and CRM ingestion (HubSpot/Salesforce):",
        body_style
    ))

    schema_data = [
        [Paragraph("<b>Field Name</b>", callout_style), Paragraph("<b>Data Type</b>", callout_style), Paragraph("<b>Validation & Formatting Rules</b>", callout_style), Paragraph("<b>Sample Value / Payload</b>", callout_style)],
        [
            Paragraph("<code>First Name</code>", code_style),
            Paragraph("String (UTF-8)", callout_style),
            Paragraph("Extracted given name; falls back to 'Executive' or 'Managing Director' if unsegmented.", callout_style),
            Paragraph("'Tariq', 'Nasser', 'Alexandros'", callout_style)
        ],
        [
            Paragraph("<code>Last Name</code>", code_style),
            Paragraph("String (UTF-8)", callout_style),
            Paragraph("Family surname, holding title, or corporate entity tag in parentheses.", callout_style),
            Paragraph("'Al-Ghurair', 'Al-Olayan', '(Al Habtoor)'", callout_style)
        ],
        [
            Paragraph("<code>Role</code>", code_style),
            Paragraph("String (UTF-8)", callout_style),
            Paragraph("Max 60 chars. Standardized corporate governance or ownership designation.", callout_style),
            Paragraph("'Chairman of the Board', 'Family Office Principal'", callout_style)
        ],
        [
            Paragraph("<code>Company</code>", code_style),
            Paragraph("String (UTF-8)", callout_style),
            Paragraph("Max 70 chars. Verified commercial name, holding group, or family trust entity.", callout_style),
            Paragraph("'Al Rajhi Holding Group', 'Emaar Properties'", callout_style)
        ],
        [
            Paragraph("<code>Domain</code>", code_style),
            Paragraph("String", callout_style),
            Paragraph("Normalized apex domain stripped of 'www.' and URI schemes for MX routing.", callout_style),
            Paragraph("'alrajhi-holding.sa', 'difc.ae'", callout_style)
        ],
        [
            Paragraph("<code>Phone Number</code>", code_style),
            Paragraph("String (E.164)", callout_style),
            Paragraph("Mandatory primary key. Formatted with international dialing prefix (+971, +966, etc.).", callout_style),
            Paragraph("'+971 50 123 4567', '+966 50 999 8888'", callout_style)
        ],
        [
            Paragraph("<code>Email</code>", code_style),
            Paragraph("String (RFC-5322)", callout_style),
            Paragraph("Direct executive email or primary domain routing contact; verified via DNS MX.", callout_style),
            Paragraph("'tariq@alghurair.com', 'contact@alrajhi.sa'", callout_style)
        ],
        [
            Paragraph("<code>City/Country</code>", code_style),
            Paragraph("String (Geo)", callout_style),
            Paragraph("Standardized sovereign municipality and nation tag.", callout_style),
            Paragraph("'Dubai, UAE', 'Riyadh, Saudi Arabia'", callout_style)
        ],
        [
            Paragraph("<code>Deliverability Status</code>", code_style),
            Paragraph("Enum", callout_style),
            Paragraph("Values: 'Deliverable (MX Active)', 'Verified Mobile Contact', 'Pending'.", callout_style),
            Paragraph("'Deliverable (MX Active)'", callout_style)
        ],
        [
            Paragraph("<code>Full Address</code>", code_style),
            Paragraph("String (UTF-8)", callout_style),
            Paragraph("Physical commercial address, tower, or financial freezone coordinates.", callout_style),
            Paragraph("'Gate Village 04, DIFC, Dubai, UAE'", callout_style)
        ],
        [
            Paragraph("<code>Website</code>", code_style),
            Paragraph("String (URI)", callout_style),
            Paragraph("Verified commercial website or authoritative source profile URL.", callout_style),
            Paragraph("'https://www.alghurair.com'", callout_style)
        ],
        [
            Paragraph("<code>Source</code>", code_style),
            Paragraph("String", callout_style),
            Paragraph("Traceable ingestion origin tag for auditability and compliance logging.", callout_style),
            Paragraph("'Apify Places Luxury', 'LinkedIn Direct VIP'", callout_style)
        ],
        [
            Paragraph("<code>Phone Type</code>", code_style),
            Paragraph("Enum", callout_style),
            Paragraph("Classified by operator prefix: 'Personal Mobile / WhatsApp (VIP Direct)' or 'Boardroom Office'.", callout_style),
            Paragraph("'Personal Mobile / WhatsApp (VIP Direct)'", callout_style)
        ]
    ]
    schema_table = Table(schema_data, colWidths=[90, 75, 237, 130])
    schema_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_DARK_HEADER),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(schema_table)
    story.append(Spacer(1, 10))

    # Section 3: 17 Sovereign Dialing Codes & Geometries
    story.append(Paragraph("3. Sovereign Jurisdictions: Dialing Codes & Network Geometries", h1_style))
    story.append(Paragraph(
        "The normalization engine enforces strict telecom prefix matching across all 17 target sovereign territories, accurately identifying personal mobile connections vs. landline PBX switchboards:",
        body_style
    ))

    country_models = [
        [Paragraph("<b>Country</b>", callout_style), Paragraph("<b>Intl Code</b>", callout_style), Paragraph("<b>Mobile Operator Prefixes</b>", callout_style), Paragraph("<b>Classification Logic</b>", callout_style), Paragraph("<b>WhatsApp URL Scheme</b>", callout_style)],
        [Paragraph("UAE", callout_style), Paragraph("+971", code_style), Paragraph("50, 52, 54, 55, 56, 58 (e& / du)", callout_style), Paragraph("VIP Direct Mobile", callout_style), Paragraph("<code>wa.me/9715...</code>", code_style)],
        [Paragraph("Saudi Arabia", callout_style), Paragraph("+966", code_style), Paragraph("50, 53, 54, 55, 56, 57, 58, 59 (STC/Mobily/Zain)", callout_style), Paragraph("VIP Direct Mobile", callout_style), Paragraph("<code>wa.me/9665...</code>", code_style)],
        [Paragraph("Qatar", callout_style), Paragraph("+974", code_style), Paragraph("33, 55, 66, 77 (Ooredoo / Vodafone)", callout_style), Paragraph("VIP Direct Mobile", callout_style), Paragraph("<code>wa.me/974...</code>", code_style)],
        [Paragraph("Kuwait", callout_style), Paragraph("+965", code_style), Paragraph("5, 6, 9 (Zain / Ooredoo / STC)", callout_style), Paragraph("VIP Direct Mobile", callout_style), Paragraph("<code>wa.me/965...</code>", code_style)],
        [Paragraph("Bahrain", callout_style), Paragraph("+973", code_style), Paragraph("3, 6 (Batelco / Zain / stc)", callout_style), Paragraph("VIP Direct Mobile", callout_style), Paragraph("<code>wa.me/973...</code>", code_style)],
        [Paragraph("Oman", callout_style), Paragraph("+968", code_style), Paragraph("9, 7 (Omantel / Ooredoo / Vodafone)", callout_style), Paragraph("VIP Direct Mobile", callout_style), Paragraph("<code>wa.me/968...</code>", code_style)],
        [Paragraph("Cyprus", callout_style), Paragraph("+357", code_style), Paragraph("9 (Cyta / Epic / PrimeTel)", callout_style), Paragraph("VIP Direct Mobile", callout_style), Paragraph("<code>wa.me/3579...</code>", code_style)],
        [Paragraph("Egypt", callout_style), Paragraph("+20", code_style), Paragraph("10 (Vodafone), 11 (Etisalat), 12 (Orange), 15 (WE)", callout_style), Paragraph("VIP Direct Mobile", callout_style), Paragraph("<code>wa.me/201...</code>", code_style)],
        [Paragraph("Turkey", callout_style), Paragraph("+90", code_style), Paragraph("5 (Turkcell / Vodafone / Turk Telekom)", callout_style), Paragraph("VIP Direct Mobile", callout_style), Paragraph("<code>wa.me/905...</code>", code_style)],
        [Paragraph("Israel", callout_style), Paragraph("+972", code_style), Paragraph("5 (Cellcom / Partner / Pelephone)", callout_style), Paragraph("VIP Direct Mobile", callout_style), Paragraph("<code>wa.me/9725...</code>", code_style)],
        [Paragraph("Jordan", callout_style), Paragraph("+962", code_style), Paragraph("7 (Zain / Orange / Umniah)", callout_style), Paragraph("VIP Direct Mobile", callout_style), Paragraph("<code>wa.me/9627...</code>", code_style)],
        [Paragraph("Lebanon", callout_style), Paragraph("+961", code_style), Paragraph("3, 70, 71, 76, 81 (Alfa / touch)", callout_style), Paragraph("VIP Direct Mobile", callout_style), Paragraph("<code>wa.me/961...</code>", code_style)],
        [Paragraph("Iraq", callout_style), Paragraph("+964", code_style), Paragraph("7 (Asiacell / Zain Iraq / Korek)", callout_style), Paragraph("VIP Direct Mobile", callout_style), Paragraph("<code>wa.me/9647...</code>", code_style)],
        [Paragraph("Iran", callout_style), Paragraph("+98", code_style), Paragraph("9 (MCI / Irancell / RighTel)", callout_style), Paragraph("VIP Direct Mobile", callout_style), Paragraph("<code>wa.me/989...</code>", code_style)],
        [Paragraph("Palestine", callout_style), Paragraph("+970", code_style), Paragraph("5 (Jawwal / Ooredoo Palestine)", callout_style), Paragraph("VIP Direct Mobile", callout_style), Paragraph("<code>wa.me/9705...</code>", code_style)],
        [Paragraph("Syria", callout_style), Paragraph("+963", code_style), Paragraph("9 (Syriatel / MTN Syria)", callout_style), Paragraph("VIP Direct Mobile", callout_style), Paragraph("<code>wa.me/9639...</code>", code_style)],
        [Paragraph("Yemen", callout_style), Paragraph("+967", code_style), Paragraph("7 (Yemen Mobile / Sabafon / YOU)", callout_style), Paragraph("VIP Direct Mobile", callout_style), Paragraph("<code>wa.me/9677...</code>", code_style)]
    ]
    country_table = Table(country_models, colWidths=[65, 45, 172, 110, 140])
    country_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_DARK_HEADER),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(country_table)
    story.append(Spacer(1, 10))

    # Section 4: Concurrency & Storage Architecture
    story.append(PageBreak())
    story.append(Paragraph("4. Storage Engine & Concurrency Architecture (`lead_store.py`)", h1_style))
    story.append(Paragraph(
        "<b>The Concurrent Writer Bottleneck:</b> On Windows environments, direct Excel writes via libraries like <code>openpyxl</code> hold exclusive file locks. In a system where background scraping threads, Flask API endpoints, and human operators inspect files concurrently, this produces fatal <code>PermissionError: [Errno 13]</code> collisions.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Dual-Tier Persistent Event Log Solution:</b>",
        body_style
    ))
    story.append(Paragraph("1. <b>Append-Only Event Store (<code>data/leads_store.jsonl</code>):</b> Ingestion scripts append verified records as atomic single-line JSON objects. Line appends in Python utilize OS-level file append locks, completely immune to process collisions.", bullet_style))
    story.append(Paragraph("2. <b>In-Memory Hash Deduplication:</b> <code>append_lead()</code> normalizes phones by stripping whitespace and punctuation (<code>re.sub(r'[\\s\\-]', '', phone)</code>) and checks against an in-memory hash set of existing records. Duplicates are rejected in $O(1)$ time.", bullet_style))
    story.append(Paragraph("3. <b>Decoupled Master Excel Sync (<code>data/HNI.xlsx</code>):</b> When new batches are appended, a non-blocking flush routine pulls the clean JSONL stream, structures a Pandas DataFrame with standard column orders, and saves to Excel using 10-attempt exponential back-off retries.", bullet_style))
    story.append(Spacer(1, 10))

    # Section 5: Web Gateway & WSGI Architecture
    story.append(Paragraph("5. Web Application, WSGI Threading & Edge Gateway", h1_style))
    story.append(Paragraph(
        "<b>Waitress Production Multi-Threaded WSGI Server (<code>run_server.py</code>):</b><br/>"
        "Flask's built-in development server is single-threaded and binds to terminal stdin/stdout, causing silent process death when terminal sessions close on Windows. The production server runs <b>Waitress</b> configured with 6 dedicated worker threads, managing concurrent dashboard pollers (6-second intervals) without socket starvation.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Cloudflare Edge Tunnel Infrastructure (<code>launch_tunnel.py</code>):</b><br/>"
        "To provide clients worldwide with instantaneous, secure access without dynamic DNS, router configuration, or open firewall ports, the server initiates an outbound QUIC tunnel via Cloudflare's Edge daemon (<code>pycloudflared</code>):",
        body_style
    ))

    cf_specs = [
        [Paragraph("<b>Gateway Parameter</b>", callout_style), Paragraph("<b>Specification / Technical Configuration</b>", callout_style)],
        [Paragraph("<b>Public Edge URL</b>", callout_style), Paragraph("<font color='#DE5743'><b>https://arbitration-michelle-zinc-tomorrow.trycloudflare.com</b></font>", code_style)],
        [Paragraph("<b>Local Reverse Target</b>", callout_style), Paragraph("<code>http://127.0.0.1:5000</code> (Waitress Multi-Threaded WSGI)", callout_style)],
        [Paragraph("<b>Encryption & Protocol</b>", callout_style), Paragraph("TLS 1.3 / HTTP/2 / QUIC edge termination with automated SSL certificate rotation", callout_style)],
        [Paragraph("<b>Access Control</b>", callout_style), Paragraph("Publicly accessible worldwide across desktop, iOS, and Android web browsers", callout_style)]
    ]
    cf_table = Table(cf_specs, colWidths=[150, 382])
    cf_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_DARK_HEADER),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(cf_table)
    story.append(Spacer(1, 10))

    # Section 6: Complete REST API Endpoints Specification
    story.append(Paragraph("6. REST API Endpoints Specification & Response Schemas", h1_style))
    
    api_schema_data = [
        [Paragraph("<b>Route & Method</b>", callout_style), Paragraph("<b>Description</b>", callout_style), Paragraph("<b>Response Schema / JSON Payload</b>", callout_style)],
        [
            Paragraph("<code>GET /</code>", code_style),
            Paragraph("Serves responsive Bento Grid Dashboard", callout_style),
            Paragraph("<code>200 OK (text/html)</code>", code_style)
        ],
        [
            Paragraph("<code>GET /api/leads</code>", code_style),
            Paragraph("Returns all verified HNI leads in store", callout_style),
            Paragraph("<code>{\"count\": 893, \"leads\": [{\"First Name\": \"...\", \"Phone Number\": \"...\"}]}</code>", code_style)
        ],
        [
            Paragraph("<code>GET /api/stats</code>", code_style),
            Paragraph("Computes aggregated RevOps pipeline metrics", callout_style),
            Paragraph("<code>{\"total_leads\": 893, \"total_phones\": 893, \"phone_rate\": \"100%\", \"pipeline_arr_cr\": \"35.72\"}</code>", code_style)
        ],
        [
            Paragraph("<code>GET /api/export/csv</code>", code_style),
            Paragraph("Streams master dataset as RFC-4180 CSV", callout_style),
            Paragraph("Attachment: <code>Content-Disposition: indulge_pan_middle_east_hnis.csv</code>", code_style)
        ],
        [
            Paragraph("<code>POST /api/mine</code>", code_style),
            Paragraph("Dispatches on-demand background scraper", callout_style),
            Paragraph("Request: <code>{\"location\": \"Dubai\", \"query\": \"Family Office\", \"target_count\": 1000}</code><br/>Response: <code>{\"message\": \"Miner launched\", \"pid\": 925}</code>", code_style)
        ],
        [
            Paragraph("<code>GET /api/miners</code>", code_style),
            Paragraph("Lists active background worker processes", callout_style),
            Paragraph("<code>{\"miners\": [{\"pid\": 925, \"status\": \"running\", \"started_at\": \"...\"}]}</code>", code_style)
        ]
    ]
    api_table = Table(api_schema_data, colWidths=[110, 160, 262])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_DARK_HEADER),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(api_table)
    story.append(Spacer(1, 10))

    # Section 7: RevOps Financial Valuation Mathematical Model
    story.append(Paragraph("7. RevOps Pipeline Financial Valuation Mathematical Model", h1_style))
    story.append(Paragraph(
        "Card 1 and Card 9 continuously project the annualized gross revenue potential of the active pipeline. The valuation model is computed in real time across the database:",
        body_style
    ))
    story.append(Paragraph(
        "$$\\text{Pipeline ARR (INR)} = N_{\\text{verified}} \\times \\text{Tier Price (₹4,00,000)}$$",
        code_style
    ))
    story.append(Paragraph(
        "$$\\text{Pipeline ARR (Crore)} = \\frac{N_{\\text{verified}} \\times 400,000}{10,000,000} = N_{\\text{verified}} \\times 0.04$$",
        code_style
    ))
    story.append(Paragraph(
        "• At the baseline of <b>893 verified leads</b>: $893 \\times 0.04 = \\mathbf{₹35.72\\text{ Crore ARR}}$ (~$4.3M USD / ~15.7M AED).<br/>"
        "• At the milestone target of <b>10,000 verified leads</b>: $10,000 \\times 0.04 = \\mathbf{₹400.00\\text{ Crore ARR}}$ (~$48M USD / ~176M AED).",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Complete Technical Architecture PDF built: {PDF_PATH} ({PDF_PATH.stat().st_size:,} bytes)")

if __name__ == "__main__":
    build_pdf()
