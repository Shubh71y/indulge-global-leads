r"""
=============================================================================
INDULGE GLOBAL - GCC HNI/UHNI INTELLIGENCE & LEAD FUNNEL PDF GENERATOR
=============================================================================
Builds an executive PDF document detailing:
1. Executive Summary & Indulge Global Positioning (WhatsApp-first Luxury Concierge)
2. Strategic Comparison: India vs. Middle East (GCC) Wealth Architecture
3. Ideal Client Profiles (ICP) & GCC Wealth Tiers
4. 5-Stage Autonomous Scraping & Verification Workflow
5. Direct Phone Number & WhatsApp Discovery Pipeline
6. Sales Navigator & Multi-Engine Dorking Search Strings
7. High-Converting Pitch Messaging & Conversion Angles
=============================================================================
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_PATH = r"C:\Users\gozoi\Projects\indulge\Indulge_Global_Middle_East_HNI_Strategy.pdf"

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
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "INDULGE GLOBAL  |  Middle East HNI/UHNI Funnel & Intelligence Architecture")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
        
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_text)
        self.drawString(54, 36, "CONFIDENTIAL  -  FOR INTERNAL USE ONLY  -  INDULGE.GLOBAL")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        self.restoreState()

def build_pdf():
    os.makedirs(os.path.dirname(PDF_PATH), exist_ok=True)
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    c_primary = colors.HexColor("#1A202C")     # Deep Charcoal
    c_gold = colors.HexColor("#B7791F")        # Executive Gold/Bronze
    c_dark_gold = colors.HexColor("#975A16")
    c_accent = colors.HexColor("#2B6CB0")      # Sophisticated Navy
    c_body = colors.HexColor("#2D3748")
    c_light_bg = colors.HexColor("#F7FAFC")
    c_border = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_gold,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_dark_gold,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_body,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_body,
        leftIndent=12,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'Callout_Text',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1A365D")
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#2C5282")
    )

    story = []

    # ================= COVER / HEADER =================
    story.append(Paragraph("INDULGE GLOBAL", ParagraphStyle('SuperTitle', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=c_gold, spaceAfter=4)))
    story.append(Paragraph("Middle East HNI/UHNI Acquisition Strategy & Intelligence Architecture", title_style))
    story.append(Paragraph("A WhatsApp-First Funnel, Multi-Engine Lead Scraper & Direct Contact Enrichment Engine", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_gold, spaceAfter=14))

    # Executive Overview Callout Box
    overview_text = (
        "<b>Executive Summary:</b> Indulge Global (indulge.global) operates a tech-enabled, WhatsApp-first luxury lifestyle "
        "concierge service commanding a ₹4 Lakh (~$4,800/yr) standalone membership. Scaling from India into the GCC (UAE, Saudi Arabia, "
        "Qatar, Kuwait, Bahrain, Oman) requires replacing India-centric startup signals with family-office governance, real estate dynasties, "
        "and sovereign conglomerate networks. Because UHNIs in the Middle East conduct business via private calls and WhatsApp, this document "
        "details the end-to-end data mining, phone/mobile discovery, SMTP verification, and conversion workflow."
    )
    callout_table = Table([[Paragraph(overview_text, callout_style)]], colWidths=[504])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EBF8FF")),
        ('BORDER', (0,0), (-1,-1), 1, colors.HexColor("#BEE3F8")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 12))

    # ================= SECTION 1: MARKET SHIFT =================
    story.append(Paragraph("1. Market Strategic Shift: India vs. Middle East (GCC)", h1_style))
    story.append(Paragraph(
        "Selling ultra-luxury concierge services to Middle East HNIs/UHNIs demands a fundamentally restructured qualification criteria:",
        body_style
    ))

    comp_data = [
        [Paragraph("<b>Dimension</b>", body_style), Paragraph("<b>India Market</b>", body_style), Paragraph("<b>Middle East (GCC) Market</b>", body_style)],
        [
            Paragraph("<b>Core Wealth Signals</b>", body_style),
            Paragraph("Startup Founders, Tech CXOs, Bollywood talent, traditional industrialists.", body_style),
            Paragraph("Multi-generational Family Offices, Real Estate Moguls, Holding Group Chairs, Sovereign-linked entities.", body_style)
        ],
        [
            Paragraph("<b>Geographic Priority</b>", body_style),
            Paragraph("Mumbai, Delhi NCR, Bengaluru.", body_style),
            Paragraph("<b>Tier 1:</b> Dubai & Abu Dhabi (UAE), Riyadh & Jeddah (KSA).<br/><b>Tier 2:</b> Doha (Qatar), Kuwait City, Manama (Bahrain), Muscat (Oman).", body_style)
        ],
        [
            Paragraph("<b>Primary Value Fit</b>", body_style),
            Paragraph("Time arbitrage on personal luxury travel, rare shopping, VIP Darshan bookings.", body_style),
            Paragraph("<b>Impossible Access:</b> Hermès Birkin waitlist bypass, F1 Paddock VIP, private jet charters, high-stakes medical air evacuations, unlisted villa buyouts.", body_style)
        ],
        [
            Paragraph("<b>Primary Channel</b>", body_style),
            Paragraph("Corporate Email, Executive Assistants, LinkedIn.", body_style),
            Paragraph("<b>WhatsApp & Private Mobile:</b> Direct, discrete, relationship-driven notes.", body_style)
        ]
    ]
    t_comp = Table(comp_data, colWidths=[110, 194, 200])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 14))

    # ================= SECTION 2: TARGET PERSONAS =================
    story.append(Paragraph("2. Ideal Client Profiles (ICP) & Wealth Tiers", h1_style))
    
    story.append(Paragraph("<b>Tier S — The Whales: Multi-Generational Family Offices & Sovereign Holdings</b>", h2_style))
    story.append(Paragraph("• <b>Profiles:</b> Family Office Principals, Chief Investment Officers (CIO), Family Office MDs (Al Futtaim, Al Habtoor, Al Olayan, Al Rajhi, Sedco, Zahid, Kanoo, Alshaya tiers).", bullet_style))
    story.append(Paragraph("• <b>Pain Point:</b> Conventional luxury desks and credit card concierges reject extreme or impossible requests.", bullet_style))
    story.append(Paragraph("• <b>Indulge Angle:</b> 24/7 dedicated lifestyle managers on WhatsApp; zero transactional markups; strict military-grade privacy.", bullet_style))

    story.append(Paragraph("<b>Tier A — Real Estate & Conglomerate Moguls</b>", h2_style))
    story.append(Paragraph("• <b>Profiles:</b> Founders, Chairmen, Group CEOs of property developers, contracting conglomerates, luxury hotel chains (Emaar, DAMAC, Sobha, Aldar, Binghatti, Omniyat, Dar Al Arkan, Roshn).", bullet_style))
    story.append(Paragraph("• <b>Pain Point:</b> Massive net worth but zero bandwidth to coordinate complex personal itineraries or source rare luxury allocations (Patek Philippe, Rolex, Hermès).", bullet_style))
    story.append(Paragraph("• <b>Indulge Angle:</b> 'From pin to plane' white-glove procurement under a single ₹4 Lakh annual membership.", bullet_style))

    story.append(Paragraph("<b>Tier B — Expat Unicorn Founders & Private Equity Partners</b>", h2_style))
    story.append(Paragraph("• <b>Profiles:</b> Relocated tech founders in DIFC/ADGM, General Partners at global PE/VC firms, and crypto/Web3 wealth.", bullet_style))
    story.append(Paragraph("• <b>Indulge Angle:</b> Exclusive networking access via Indulge's 'Connect' feature paired with sold-out global event access (Wimbledon, Art Basel, Monaco GP).", bullet_style))

    story.append(Spacer(1, 14))

    # ================= SECTION 3: WORKFLOW ARCHITECTURE =================
    story.append(Paragraph("3. End-to-End Autonomous Intelligence Workflow", h1_style))
    story.append(Paragraph(
        "The automated system operates across 5 synchronized stages, moving from unstructured web footprints to 100% verified multi-channel leads:",
        body_style
    ))

    workflow_stages = [
        [
            Paragraph("<b>Stage 1: Target Matrix</b>", body_style),
            Paragraph("Loads 55+ Tier-1 GCC conglomerates, holding firms, family offices, and 38 C-suite titles spanning Dubai, Abu Dhabi, Riyadh, Jeddah, Doha, Kuwait, and Bahrain.", body_style)
        ],
        [
            Paragraph("<b>Stage 2: Discovery Engine</b>", body_style),
            Paragraph("Multi-engine SERP dorking + rotating Tavily API keys + BrowserAct real-browser session automation. Pulls live LinkedIn profiles without risking personal account bans.", body_style)
        ],
        [
            Paragraph("<b>Stage 3: Identity Cleansing</b>", body_style),
            Paragraph("Regex parsers strip news, geographic noise, and degree acronyms, cleanly isolating First Name, Last Name, Operating Entity, and Corporate Role.", body_style)
        ],
        [
            Paragraph("<b>Stage 4: Verification Grid</b>", body_style),
            Paragraph("• <b>Corporate Email:</b> Generates 7 business permutations; runs live Port 25 SMTP handshake against Microsoft 365, Google Workspace, and Mimecast MX servers.<br/>"
                      "• <b>Direct Mobile / WhatsApp:</b> Extracts phone numbers via public registry dorking and API phone enrichers.", body_style)
        ],
        [
            Paragraph("<b>Stage 5: Storage & Outreach</b>", body_style),
            Paragraph("Thread-safe persistence to <code>indulge_gcc_hni_master.csv</code>. Clean leads feed into high-touch WhatsApp and private email concierge invitations.", body_style)
        ]
    ]
    t_wf = Table(workflow_stages, colWidths=[140, 364])
    t_wf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light_bg),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_wf)
    story.append(Spacer(1, 14))

    # ================= SECTION 4: DIRECT PHONE & WHATSAPP =================
    story.append(Paragraph("4. Direct Phone Number & WhatsApp Discovery Pipeline", h1_style))
    story.append(Paragraph(
        "Because Indulge Global operates on a WhatsApp-first interaction model, mobile phone intelligence is paramount. The system utilizes a 3-tier mobile discovery framework:",
        body_style
    ))

    story.append(Paragraph("<b>A. Public Commercial Registries & Regulatory Filings</b>", h2_style))
    story.append(Paragraph("• Mining Dubai DED (Department of Economy and Tourism), Saudi Ministry of Commerce (MOC) CR filings, and ADGM/DIFC commercial registers for listed executive contact numbers.", bullet_style))

    story.append(Paragraph("<b>B. Event Dossier & Conference vCard Dorking</b>", h2_style))
    story.append(Paragraph("• Automated SERP patterns targeting executive bios, speaker brochures, and press contact releases (FII Riyadh, Arabian Travel Market, Gitex Global):", bullet_style))
    p_dork = Paragraph('<code>&quot;[Executive Name]&quot; (&quot;+971&quot; OR &quot;+966&quot; OR &quot;+974&quot;) (&quot;mobile&quot; OR &quot;WhatsApp&quot; OR &quot;direct&quot;)</code>', code_style)
    story.append(p_dork)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>C. Third-Party Direct-Dial API Enrichment</b>", h2_style))
    story.append(Paragraph("• Integrates direct-dial API hooks (Apollo, Kaspr, Lusha) taking the verified corporate email/LinkedIn URL and returning direct mobile lines (+971 50..., +966 5...).", bullet_style))
    story.append(Paragraph("• <b>WhatsApp Ping Validation:</b> Validates mobile numbers against WhatsApp endpoints to confirm active account status prior to outreach.", bullet_style))

    story.append(Spacer(1, 14))

    # ================= SECTION 5: SEARCH STRINGS & REPO STRUCTURE =================
    story.append(Paragraph("5. LinkedIn Sales Navigator & Boolean Search Matrix", h1_style))
    story.append(Paragraph("Exact boolean strings optimized for GCC HNI discovery:", body_style))

    b_strings = [
        Paragraph("<b>1. UAE Family Office & Wealth Principals (Dubai / Abu Dhabi):</b><br/>"
                  "<code>(title:&quot;Family Office Principal&quot; OR title:&quot;Family Office Founder&quot; OR title:&quot;Family Office CEO&quot; OR title:&quot;Chief Investment Officer&quot; OR title:&quot;Head of Family Office&quot;) AND (location:&quot;Dubai&quot; OR location:&quot;Abu Dhabi&quot;)</code>", code_style),
        Paragraph("<b>2. Saudi Conglomerate & Holding Group Leadership (Riyadh / Jeddah):</b><br/>"
                  "<code>(title:&quot;Group Chairman&quot; OR title:&quot;Executive Chairman&quot; OR title:&quot;Holding Company Chairman&quot; OR title:&quot;Group Managing Director&quot; OR title:&quot;Industrialist&quot;) AND (location:&quot;Saudi Arabia&quot; OR location:&quot;Riyadh&quot; OR location:&quot;Jeddah&quot;)</code>", code_style),
        Paragraph("<b>3. GCC Real Estate Developers & Luxury Hospitality Owners:</b><br/>"
                  "<code>(title:&quot;Founder&quot; OR title:&quot;Chairman&quot; OR title:&quot;Managing Director&quot; OR title:&quot;Owner&quot;) AND (&quot;Real Estate&quot; OR &quot;Property Development&quot; OR &quot;Hospitality&quot;) AND (location:&quot;United Arab Emirates&quot; OR location:&quot;Saudi Arabia&quot;)</code>", code_style)
    ]
    for bs in b_strings:
        story.append(bs)
        story.append(Spacer(1, 5))

    story.append(Spacer(1, 10))

    # ================= SECTION 6: MESSAGING TEMPLATES =================
    story.append(Paragraph("6. High-Converting Pitch Messaging for Indulge Global", h1_style))
    
    pitch_a = (
        "<b>Angle A: The 'Impossible Procurement' Hook (WhatsApp / Email)</b><br/>"
        "<b>Subject:</b> Private allocations & Hermès / F1 access for {{Company/Family Office Name}}<br/><br/>"
        "Hi {{First_Name}},<br/><br/>"
        "Most luxury concierges fail when access isn't public. Booking commercial business class is easy—bypassing "
        "a 2-year Hermès Birkin waitlist, securing 48-hour Wimbledon Royal Box tickets, or chartering a private jet out "
        "of Zurich at midnight is where traditional desks break down.<br/><br/>"
        "Indulge Global operates a WhatsApp-first, closed-door concierge platform for 12,000+ UHNIs globally "
        "(standalone annual membership, zero service markups on lifestyle procurement).<br/><br/>"
        "We are extending private access to select family offices and principals in {{City}}. Would you be open to "
        "reviewing our private membership brief?"
    )

    pitch_b = (
        "<b>Angle B: The 'Emergency & Time-Arbitrage' Hook (For Family Office Principals)</b><br/>"
        "<b>Subject:</b> Turnkey lifestyle management for {{First_Name}}'s office<br/><br/>"
        "Hi {{First_Name}},<br/><br/>"
        "For principals managing large portfolios across {{Country}}, time and discretion are the scarcest assets. "
        "Standard executive assistants handle day-to-day coordination, but rare global demands require an institutional network.<br/><br/>"
        "Documented requests handled by Indulge Global within hours:<br/>"
        "• Emergency midnight air ambulance evacuations with full hospital admissions<br/>"
        "• Sold-out Michelin 3-star buyouts across Lake Como and Tokyo<br/>"
        "• Exclusive off-market real estate and private island charters<br/><br/>"
        "Operates 24/7 on WhatsApp with a dedicated lifestyle manager. Zero markup on transactions.<br/><br/>"
        "Open to a 5-minute introduction this week?"
    )

    t_pitches = Table([[Paragraph(pitch_a, body_style)], [Paragraph(pitch_b, body_style)]], colWidths=[504])
    t_pitches.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_pitches)

    story.append(Spacer(1, 14))

    # ================= SECTION 7: CODEBASE & EXECUTION =================
    story.append(Paragraph("7. Codebase Isolation & Operational Commands", h1_style))
    story.append(Paragraph(
        "The entire system is completely isolated inside <code>C:\\Users\\gozoi\\Projects\\indulge</code> with zero overlap "
        "with any other workspace.",
        body_style
    ))

    cmd_data = [
        [Paragraph("<b>File / Script</b>", body_style), Paragraph("<b>Function & Execution Command</b>", body_style)],
        [
            Paragraph("<code>scripts/config_middle_east_hni.py</code>", code_style),
            Paragraph("Master target matrix with 55+ GCC conglomerates, 38 wealth titles, and boolean search templates.", body_style)
        ],
        [
            Paragraph("<code>scripts/discovery_engine.py</code>", code_style),
            Paragraph("Rotating multi-key Tavily API engine with automated 429 backoff and Bing SERP scraper fallback.", body_style)
        ],
        [
            Paragraph("<code>scripts/smtp_verifier.py</code>", code_style),
            Paragraph("DNS MX resolver, 7-point corporate email permutation generator, and Port 25 SMTP handshake tester.", body_style)
        ],
        [
            Paragraph("<code>scripts/mine_middle_east_hni.py</code>", code_style),
            Paragraph("Autonomous 2-phase background miner. <i>Command:</i> <code>python scripts/mine_middle_east_hni.py</code>", body_style)
        ],
        [
            Paragraph("<code>scripts/stats.py</code>", code_style),
            Paragraph("Real-time pipeline diagnostics & deliverability inspector. <i>Command:</i> <code>python scripts/stats.py</code>", body_style)
        ],
        [
            Paragraph("<code>data/indulge_gcc_hni_master.csv</code>", code_style),
            Paragraph("Master deduplicated database of mined Middle East HNI/UHNI leads.", body_style)
        ]
    ]
    t_cmd = Table(cmd_data, colWidths=[180, 324])
    t_cmd.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_light_bg),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_cmd)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✅ PDF successfully generated at: {PDF_PATH}")

if __name__ == "__main__":
    build_pdf()
