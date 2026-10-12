r"""
Generate High-End Executive PDF: Complete Technical Architecture & Workflow
=============================================================================
Design: Comprehensive Engineering Blueprint & Systems Architecture Manual
Coverage: Three-Tier Architecture, Data Pipeline, Regex & Normalization,
          Atomic JSONL Store, Waitress WSGI, Cloudflare Edge Tunneling, API Endpoints
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

# Palette
COLOR_BLACK = colors.HexColor("#0E0E0E")
COLOR_CORAL = colors.HexColor("#DE5743")
COLOR_BG_CARD = colors.HexColor("#F8F9FA")
COLOR_BORDER = colors.HexColor("#E2E8F0")
COLOR_MUTED = colors.HexColor("#64748B")
COLOR_CODE_BG = colors.HexColor("#F1F5F9")

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
        # Top rule
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.75)
        self.line(40, letter[1] - 38, letter[0] - 40, letter[1] - 38)
        
        # Header text
        self.setFont("Helvetica", 7.5)
        self.setFillColor(COLOR_MUTED)
        self.drawString(40, letter[1] - 32, "INDULGE GLOBAL  |  SYSTEMS ENGINEERING & REVOPS SPECIFICATION")
        self.drawRightString(letter[0] - 40, letter[1] - 32, "TECHNICAL ARCHITECTURE MANUAL")

        # Bottom rule
        self.line(40, 42, letter[0] - 40, 42)
        
        # Footer text
        self.drawString(40, 30, "Confidential: Technical Blueprint & Workflow Specification  |  Pan-Middle East Engine")
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
        fontSize=23,
        leading=27,
        textColor=COLOR_BLACK,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=COLOR_CORAL,
        spaceAfter=14
    )
    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=COLOR_BLACK,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=COLOR_BLACK,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=5
    )
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#0F172A")
    )
    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#0F172A")
    )

    story = []

    # Title Block
    story.append(Paragraph("INDULGE GLOBAL ENGINEERING", subtitle_style))
    story.append(Paragraph("Complete Technical Architecture & Systems Workflow", title_style))
    story.append(Paragraph("Pan-Middle East HNI Discovery Pipeline, Concurrency Store & Gateway Specification", ParagraphStyle('Sub', parent=body_style, fontSize=9.5, textColor=COLOR_MUTED, spaceAfter=14)))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_CORAL, spaceAfter=14))

    # Meta Spec Table
    meta_data = [
        [
            Paragraph("<b>Repository:</b> <code>C:\\Users\\gozoi\\Projects\\indulge</code>", callout_style),
            Paragraph("<b>Target Lead Goal:</b> 10,000 Verified UHNIs / HNIs", callout_style)
        ],
        [
            Paragraph("<b>Runtime Stack:</b> Python 3.13, Waitress WSGI, Flask 3.1", callout_style),
            Paragraph("<b>Active Mining Script:</b> <code>scripts/mine_pan_middle_east_10000.py</code>", callout_style)
        ],
        [
            Paragraph("<b>Public Cloud Tunnel:</b> Cloudflare Signed Edge Proxy", callout_style),
            Paragraph("<b>Storage Protocols:</b> Atomic JSONL Append + Master Excel Sync", callout_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[260, 272])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_CARD),
        ('BOX', (0,0), (-1,-1), 0.75, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # Section 1: Three-Tier Architecture
    story.append(Paragraph("1. Three-Tier Reactive Systems Architecture", h1_style))
    story.append(Paragraph(
        "The Indulge Global intelligence infrastructure decouples ingestion, state management, and client presentation into three independent, fault-tolerant tiers:",
        body_style
    ))

    arch_layers = [
        [Paragraph("<b>Architectural Layer</b>", callout_style), Paragraph("<b>Component / Tech</b>", callout_style), Paragraph("<b>Engineering Responsibility & Guarantees</b>", callout_style)],
        [
            Paragraph("<b>1. Ingestion Tier<br/>(The Radar Engines)</b>", callout_style),
            Paragraph("<code>mine_pan_middle_east_10000.py</code><br/>Apify Places Actor<br/>Tavily Multi-Key Engine", callout_style),
            Paragraph("Executes asynchronous sweeps across 150+ luxury wealth clusters and 80+ OSINT dorks. Intercepts raw titles, entity addresses, and unformatted phone strings across 17 nations.", callout_style)
        ],
        [
            Paragraph("<b>2. Persistence Tier<br/>(Atomic Data Store)</b>", callout_style),
            Paragraph("<code>scripts/lead_store.py</code><br/><code>leads_store.jsonl</code><br/><code>data/HNI.xlsx</code>", callout_style),
            Paragraph("Eliminates Windows file-locking race conditions through an append-only JSONL log. Enforces E.164 phone hash deduplication and flushes safely to Excel/CSV with exponential retries.", callout_style)
        ],
        [
            Paragraph("<b>3. Presentation Tier<br/>(Gateway & Edge)</b>", callout_style),
            Paragraph("Waitress WSGI (6 Threads)<br/>Flask Web API (<code>app.py</code>)<br/>Cloudflare Edge Tunnel", callout_style),
            Paragraph("Serves real-time REST endpoints (<code>/api/leads</code>, <code>/api/stats</code>) and streams CSV exports over a secure global HTTPS URL without local port forwarding.", callout_style)
        ]
    ]
    arch_table = Table(arch_layers, colWidths=[110, 140, 282])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0E0E0E")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 14))

    # Section 2: Data Extraction & Normalization
    story.append(Paragraph("2. Extraction & Normalization Engineering", h1_style))
    story.append(Paragraph(
        "<b>A. Phone Extraction & Classification Engine:</b><br/>"
        "Phone strings extracted from public corporate listings and bio texts are validated against a strict international regex covering all 17 Middle East and Mediterranean calling codes:",
        body_style
    ))
    code_block_1 = Paragraph(
        "PHONE_RE = re.compile(r'(\\+(?:971|966|974|965|973|968|357|20|98|964|972|962|961|970|963|90|967)"
        "[\\s\\-]?\\d{1,3}[\\s\\-]?[\\d\\s\\-]{6,10})')<br/><br/>"
        "# Classifies if number belongs to personal mobile operator prefixes:<br/>"
        "MOBILE_RE = re.compile(r'(\\+971[\\s\\-]?(?:50|52|54|55|56|58)|\\+966[\\s\\-]?(?:50|53|54|55|58)|"
        "\\+974[\\s\\-]?(?:33|55|66|77)|\\+965[\\s\\-]?(?:5|6|9)|\\+357[\\s\\-]?(?:9)|\\+20[\\s\\-]?(?:10|11|12))')",
        code_style
    )
    code_t1 = Table([[code_block_1]], colWidths=[532])
    code_t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_CODE_BG),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(code_t1)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>B. Multi-Key Tavily Quota Guard & Load Balancing:</b><br/>"
        "Mining 10,000 records requires handling thousands of search requests. The engine rotates across 3 active developer keys: <code>api-pool-token-1</code>, <code>api-pool-token-2</code>, and <code>api-pool-token-3</code> using round-robin distribution with automated 429 back-off handling.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # Section 3: Concurrency & Storage Architecture
    story.append(PageBreak())
    story.append(Paragraph("3. Concurrency & Persistence Engine (`scripts/lead_store.py`)", h1_style))
    story.append(Paragraph(
        "<b>Why Traditional Excel Direct Writes Fail:</b> On Windows, attempting to write to an Excel workbook (<code>HNI.xlsx</code>) while a user has it open or while another thread is reading throws <code>PermissionError: [Errno 13] Permission denied</code>. This previously caused data truncation.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Append-Only JSONL Architecture:</b><br/>"
        "The system decouples state ingestion from export generation using an append-only JSONL event log (<code>data/leads_store.jsonl</code>):",
        body_style
    ))

    flow_steps = [
        Paragraph("1. <b>Atomic Ingestion:</b> When a lead is mined, <code>lead_store.append_lead()</code> cleans the phone string of whitespace and dashes and checks if the normalized phone exists in the persistent hash set.", bullet_style),
        Paragraph("2. <b>Instant Append:</b> If unique, the lead dictionary is appended as a single JSON line to <code>leads_store.jsonl</code>. Line appends in Python on Windows are atomic at the OS level.", bullet_style),
        Paragraph("3. <b>Safe Workbook Flush:</b> Following batch append, <code>sync_to_excel_and_csv()</code> loads all unique records, constructs a pandas DataFrame with standardized column schema, and writes out <code>HNI.xlsx</code> with up to 10 automated retry attempts.", bullet_style)
    ]
    for s in flow_steps:
        story.append(s)
    story.append(Spacer(1, 12))

    # Section 4: Edge Tunnel & Web Server
    story.append(Paragraph("4. Edge Gateway & Multi-Threaded WSGI Architecture", h1_style))
    story.append(Paragraph(
        "<b>Waitress Production Server (<code>run_server.py</code>):</b><br/>"
        "The web layer is served by <b>Waitress</b>, a production-grade pure-Python WSGI server configured with 6 dedicated worker threads. This guarantees that background 6-second dashboard pollers do not block long-running queries or CSV exports.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Cloudflare Edge Tunnel (<code>launch_tunnel.py</code>):</b><br/>"
        "To allow instant external client access without port forwarding or firewalls, <code>pycloudflared</code> establishes an outbound secure tunnel to Cloudflare edge nodes, producing the active public URL:",
        body_style
    ))
    
    url_box = Paragraph(
        "<b>Public Client URL:</b> <font color='#DE5743'><b>https://arbitration-michelle-zinc-tomorrow.trycloudflare.com</b></font><br/>"
        "<b>Protocol:</b> TLS 1.3 Encrypted Reverse Proxy  |  <b>Target Port:</b> 127.0.0.1:5000",
        callout_style
    )
    url_table = Table([[url_box]], colWidths=[532])
    url_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_CARD),
        ('BOX', (0,0), (-1,-1), 1, COLOR_CORAL),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(url_table)
    story.append(Spacer(1, 14))

    # Section 5: API Endpoints
    story.append(Paragraph("5. REST API Endpoints Specification", h1_style))
    api_specs = [
        [Paragraph("<b>HTTP Method & Route</b>", callout_style), Paragraph("<b>Function & Return Type</b>", callout_style), Paragraph("<b>Payload / Sample Output</b>", callout_style)],
        [
            Paragraph("<code>GET /</code>", code_style),
            Paragraph("Serves Bento Grid Dashboard (HTML/CSS/JS)", callout_style),
            Paragraph("Renders Falin/QClay luxury dashboard with dynamic metrics", callout_style)
        ],
        [
            Paragraph("<code>GET /api/leads</code>", code_style),
            Paragraph("Returns all verified HNI leads (JSON)", callout_style),
            Paragraph("<code>{\"count\": 893, \"leads\": [{...}, ...]}</code>", code_style)
        ],
        [
            Paragraph("<code>GET /api/stats</code>", code_style),
            Paragraph("Computes aggregated RevOps pipeline metrics", callout_style),
            Paragraph("<code>{\"total_leads\": 893, \"phone_rate\": \"100%\", \"arr_cr\": \"35.72\"}</code>", code_style)
        ],
        [
            Paragraph("<code>GET /api/export/csv</code>", code_style),
            Paragraph("Streams master dataset as RFC-4180 CSV", callout_style),
            Paragraph("Download: <code>indulge_pan_middle_east_hnis.csv</code>", callout_style)
        ],
        [
            Paragraph("<code>POST /api/mine</code>", code_style),
            Paragraph("Triggers custom background mining sweep", callout_style),
            Paragraph("Input: <code>{\"location\": \"Dubai\", \"query\": \"Family Office\"}</code>", code_style)
        ],
        [
            Paragraph("<code>GET /api/miners</code>", code_style),
            Paragraph("Lists active miner PIDs and process logs", callout_style),
            Paragraph("<code>{\"miners\": [{\"pid\": 925, \"status\": \"running\"}]}</code>", code_style)
        ]
    ]
    api_table = Table(api_specs, colWidths=[120, 170, 242])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0E0E0E")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_BG_CARD]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(api_table)
    story.append(Spacer(1, 14))

    # Section 6: Standard Operating Procedures
    story.append(Paragraph("6. Operational Playbook & Process Management (SOP)", h1_style))
    story.append(Paragraph(
        "• <b>Inspect Live Lead Count:</b><br/>"
        "<code>python -c \"import lead_store; print('Verified Leads:', len(lead_store.get_all_leads()))\"</code><br/>"
        "• <b>Force Immediate Excel Sync:</b><br/>"
        "<code>python -c \"import sys; sys.path.append('scripts'); import lead_store; lead_store.sync_to_excel_and_csv()\"</code><br/>"
        "• <b>Stack Restart Sequence:</b><br/>"
        "1. Launch Server: <code>python -u run_server.py</code><br/>"
        "2. Launch Tunnel: <code>python -u launch_tunnel.py</code><br/>"
        "3. Launch Miner: <code>python -u scripts/mine_pan_middle_east_10000.py</code>",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Technical Specification PDF built: {PDF_PATH} ({PDF_PATH.stat().st_size:,} bytes)")

if __name__ == "__main__":
    build_pdf()
