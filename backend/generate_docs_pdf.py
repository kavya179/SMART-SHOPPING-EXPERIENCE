import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# Define Palette
PRIMARY = colors.HexColor("#0F172A")    # Dark Obsidian
SECONDARY = colors.HexColor("#1E293B")  # Slate Navy
ACCENT = colors.HexColor("#059669")     # Emerald Accent
ACCENT_LIGHT = colors.HexColor("#ECFDF5")
TEXT_DARK = colors.HexColor("#1E293B")
TEXT_MUTED = colors.HexColor("#64748B")
BG_LIGHT = colors.HexColor("#F8FAFC")
BORDER_COLOR = colors.HexColor("#E2E8F0")

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
        if self._pageNumber == 1:
            # Suppress headers and footers on cover page
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(TEXT_MUTED)

        # Header
        self.drawString(54, 792 - 36, "Joyory SmartMatch — Development Documentation")
        self.drawRightString(612 - 54, 792 - 36, "Smart Shopping Experience Track")
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(54, 792 - 42, 612 - 54, 792 - 42)

        # Footer
        self.line(54, 46, 612 - 54, 46)
        self.drawString(54, 34, "Joyory SmartMatch MVP | Confidential Hackathon Deliverable")
        self.drawRightString(612 - 54, 34, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def build_pdf(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=PRIMARY,
        spaceAfter=8
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=ACCENT,
        spaceAfter=20
    )
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=20,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_DARK,
        spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4
    )
    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=PRIMARY,
        backColor=BG_LIGHT,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )
    callout_style = ParagraphStyle(
        'CalloutText',
        parent=body_style,
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=SECONDARY
    )

    story = []

    # ── COVER PAGE ────────────────────────────────────────────────────────
    story.append(Spacer(1, 30))
    story.append(Paragraph("Joyory SmartMatch", title_style))
    story.append(Paragraph("Smart Shopping Experience for Beauty & Personal Care", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2.5, color=ACCENT, spaceAfter=20))

    meta_table_data = [
        [Paragraph("<b>Document Type:</b>", body_style), Paragraph("Technical Architecture & Development Documentation", body_style)],
        [Paragraph("<b>Hackathon Track:</b>", body_style), Paragraph("Smart Shopping Experience", body_style)],
        [Paragraph("<b>Date:</b>", body_style), Paragraph("September 20, 2026", body_style)],
        [Paragraph("<b>Authors / Team:</b>", body_style), Paragraph("[Student / Developer Team Name] (Editable Placeholder)", body_style)],
        [Paragraph("<b>Repository:</b>", body_style), Paragraph("https://github.com/kavya179/SMART-SHOPPING-EXPERIENCE.git", body_style)],
        [Paragraph("<b>Core Stack:</b>", body_style), Paragraph("React 18 · Django 5 · Django REST Framework · SQLite", body_style)],
        [Paragraph("<b>Prototype Verification:</b>", body_style), Paragraph("26 / 26 Backend Unit Tests Passing (100% OK)", body_style)]
    ]
    meta_table = Table(meta_table_data, colWidths=[130, 374])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 20))

    # Executive Summary Box on Cover
    summary_box_data = [
        [Paragraph("<b>Executive Summary & Abstract</b>", h2_style)],
        [Paragraph(
            "<b>Joyory SmartMatch</b> is a full-stack smart shopping platform built to demystify beauty and personal-care cosmetics. "
            "It couples a 5-step guided recommendation quiz with a deterministic weighted scoring engine, side-by-side INCI formulation comparison, "
            "an automated zero-cost product FAQ assistant, and a luxury dark obsidian shopping interface. "
            "All recommendations and queries are grounded strictly in verified SQLite catalog specifications without external paid AI dependencies.",
            body_style
        )]
    ]
    summary_box = Table(summary_box_data, colWidths=[504])
    summary_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), ACCENT_LIGHT),
        ('BOX', (0,0), (-1,-1), 1.5, ACCENT),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(summary_box)
    story.append(PageBreak())

    # ── SECTION 1 & 2: PROBLEM & SOLUTION ─────────────────────────────────
    story.append(Paragraph("1. Problem Statement & Market Opportunity", h1_style))
    story.append(Paragraph(
        "Online beauty and personal care shoppers face significant friction due to formulation complexity and marketing opacity. "
        "Key challenges identified across the cosmetic retail space include:",
        body_style
    ))
    story.append(Paragraph("• <b>Formulation Jargon:</b> Complex INCI chemical names overwhelm consumers without chemistry expertise.", bullet_style))
    story.append(Paragraph("• <b>Trial-and-Error Purchasing:</b> Purchasing incompatible products causes skin irritation, wasted money, and high return rates.", bullet_style))
    story.append(Paragraph("• <b>Search Limitations:</b> Standard e-commerce catalogs only support brand or keyword filtering without assessing skin-barrier suitability.", bullet_style))
    story.append(Paragraph("• <b>Omitted Safety Guidance:</b> Usage routines (AM vs PM) and essential patch-test instructions are routinely obscured in fine print.", bullet_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("2. Proposed Solution & Concept", h1_style))
    story.append(Paragraph(
        "Joyory SmartMatch bridges the gap between cosmetic chemistry and consumer decision-making by delivering four core pillars:",
        body_style
    ))
    story.append(Paragraph("1. <b>Guided 5-Step Quiz Finder:</b> Interactive workflow assessing category, skin profile, target concern, budget, and active preferences.", bullet_style))
    story.append(Paragraph("2. <b>Deterministic Scoring Engine:</b> Pure Python rule-based recommender calculating percentage compatibility with explicit reason breakdowns.", bullet_style))
    story.append(Paragraph("3. <b>Side-by-Side Comparison Matrix:</b> Multi-product dock evaluating active concentrations, full INCI formulas, and safety cautions.", bullet_style))
    story.append(Paragraph("4. <b>Catalog FAQ Assistant:</b> Automated assistant answering routine and ingredient queries with explicit non-medical guardrails.", bullet_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("3. Target User Personas", h1_style))
    persona_data = [
        [Paragraph("<b>Persona</b>", body_style), Paragraph("<b>Key Characteristics & Pain Points</b>", body_style), Paragraph("<b>Joyory SmartMatch Solution</b>", body_style)],
        [Paragraph("<b>Skincare Novice</b>", body_style), Paragraph("Overwhelmed by active ingredients; fears breakouts.", body_style), Paragraph("Guided quiz, beginner active matches, routine directions.", body_style)],
        [Paragraph("<b>Ingredient Hunter</b>", body_style), Paragraph("Seeks specific actives (Vitamin C, Ceramides, SPF).", body_style), Paragraph("Full INCI transparency and side-by-side comparison matrix.", body_style)],
        [Paragraph("<b>Budget Shopper</b>", body_style), Paragraph("Strict price cap; seeks value-for-money formulations.", body_style), Paragraph("Budget filters, promo codes, and budget-alternative suggestions.", body_style)]
    ]
    persona_table = Table(persona_data, colWidths=[100, 204, 200])
    persona_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
    ]))
    story.append(persona_table)

    story.append(PageBreak())

    # ── SECTION 4 & 5: MARKET REVIEW & FEATURE BREAKDOWN ──────────────────
    story.append(Paragraph("4. Existing Market Review & Proposed Differentiation", h1_style))
    story.append(Paragraph(
        "<i>Date of Review: September 20, 2026</i>. An analysis of modern beauty e-commerce platforms highlights the key differentiators introduced by Joyory SmartMatch:",
        body_style
    ))

    diff_data = [
        [Paragraph("<b>Feature Dimension</b>", body_style), Paragraph("<b>Traditional Beauty E-Commerce</b>", body_style), Paragraph("<b>Joyory SmartMatch Prototype</b>", body_style)],
        [Paragraph("<b>Product Discovery</b>", body_style), Paragraph("Keyword & brand search only.", body_style), Paragraph("5-step category-adaptive compatibility quiz.", body_style)],
        [Paragraph("<b>Recommendation Logic</b>", body_style), Paragraph("Black-box or sponsored placements.", body_style), Paragraph("Transparent weighted scoring with explicit reasons.", body_style)],
        [Paragraph("<b>Formula Comparison</b>", body_style), Paragraph("Rarely available or price-only.", body_style), Paragraph("Side-by-side INCI, routine, and caution matrix.", body_style)],
        [Paragraph("<b>Budget Flexibility</b>", body_style), Paragraph("Binary filter (hides non-matches).", body_style), Paragraph("Suggests closest alternatives with budget explanations.", body_style)],
        [Paragraph("<b>Catalog Assistance</b>", body_style), Paragraph("Generic bot or delayed human tickets.", body_style), Paragraph("Instant rule-based FAQ with non-medical guardrails.", body_style)]
    ]
    diff_table = Table(diff_data, colWidths=[110, 194, 200])
    diff_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
    ]))
    story.append(diff_table)

    story.append(Spacer(1, 10))
    story.append(Paragraph("5. Feature Status Breakdown", h1_style))

    feat_data = [
        [Paragraph("<b>Feature Module</b>", body_style), Paragraph("<b>Status</b>", body_style), Paragraph("<b>Implementation Mechanism</b>", body_style)],
        [Paragraph("Product Catalog & Search", body_style), Paragraph("<font color='#059669'><b>Implemented</b></font>", body_style), Paragraph("Django REST API, real-time keyword search & category filter pills.", body_style)],
        [Paragraph("Product Detail Page (PDP)", body_style), Paragraph("<font color='#059669'><b>Implemented</b></font>", body_style), Paragraph("Full INCI lists, active chips, morning/night routine, cautions.", body_style)],
        [Paragraph("SmartMatch 5-Step Quiz", body_style), Paragraph("<font color='#059669'><b>Implemented</b></font>", body_style), Paragraph("Category-adaptive step wizard with budget threshold sliders.", body_style)],
        [Paragraph("Recommendation Engine", body_style), Paragraph("<font color='#059669'><b>Implemented</b></font>", body_style), Paragraph("Deterministic weighted Python scoring with budget fallback logic.", body_style)],
        [Paragraph("Formula Comparison Studio", body_style), Paragraph("<font color='#059669'><b>Implemented</b></font>", body_style), Paragraph("Floating dock + /compare page for up to 3 selected items.", body_style)],
        [Paragraph("Wishlist & Cart Management", body_style), Paragraph("<font color='#059669'><b>Implemented</b></font>", body_style), Paragraph("React Context (ShopContext) mirrored to browser localStorage.", body_style)],
        [Paragraph("Demo Checkout", body_style), Paragraph("<font color='#D97706'><b>Simulated</b></font>", body_style), Paragraph("Modal summary, form validation, mock order ID (JOY-XXXXXX).", body_style)],
        [Paragraph("Product FAQ Assistant", body_style), Paragraph("<font color='#059669'><b>Implemented</b></font>", body_style), Paragraph("Token-based rule engine with non-medical disclaimer banner.", body_style)],
        [Paragraph("Cloud User Auth", body_style), Paragraph("<font color='#64748B'><b>Planned</b></font>", body_style), Paragraph("Multi-device cloud user profiles with JWT authentication.", body_style)]
    ]
    feat_table = Table(feat_data, colWidths=[130, 84, 290])
    feat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('PADDING', (0,0), (-1,-1), 4.5),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
    ]))
    story.append(feat_table)

    story.append(PageBreak())

    # ── SECTION 6 & 7: ARCHITECTURE & DATABASE ────────────────────────────
    story.append(Paragraph("6. System Architecture", h1_style))
    story.append(Paragraph(
        "The system adheres to a clean decoupled client-server architecture consisting of three core tiers:",
        body_style
    ))
    story.append(Paragraph("• <b>Presentation Tier (React 18 SPA):</b> Client-side routing, glassmorphic UI components, and state management via <code>ShopContext</code>.", bullet_style))
    story.append(Paragraph("• <b>Application & Logic Tier (Django 5 & DRF):</b> RESTful API routing, input validation, <code>RuleBasedRecommender</code> service, and <code>ProductFaqAssistant</code> service.", bullet_style))
    story.append(Paragraph("• <b>Data Tier (SQLite via Django ORM):</b> Relational storage of product records, ingredient profiles, categories, and routine directions.", bullet_style))

    arch_diagram_text = (
        "+-------------------------------------------------------------------------+\n"
        "|                         REACT 18 FRONTEND (SPA)                         |\n"
        "|  HomePage | Catalog | ProductDetail | SmartMatchQuiz | Compare | Cart   |\n"
        "|  Global State: ShopContext (Wishlist, Cart, Compare in localStorage)    |\n"
        "+------------------------------------+------------------------------------+\n"
        "                                     | HTTP / JSON REST API (Port 8000)\n"
        "                                     v\n"
        "+-------------------------------------------------------------------------+\n"
        "|                    DJANGO REST FRAMEWORK BACKEND                        |\n"
        "|  - Endpoints: /api/products/, /api/recommendations/, /api/faq/          |\n"
        "|  - Services: RuleBasedRecommender, ProductFaqAssistant                  |\n"
        "+------------------------------------+------------------------------------+\n"
        "                                     | Django ORM Queries\n"
        "                                     v\n"
        "+-------------------------------------------------------------------------+\n"
        "|                             SQLITE DATABASE                             |\n"
        "|  Table: products_product (12 Verified Multi-Category Items)             |\n"
        "+-------------------------------------------------------------------------+"
    )
    story.append(Paragraph(f"<pre>{arch_diagram_text}</pre>", code_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("7. Database Schema: Product Model", h1_style))
    story.append(Paragraph(
        "The relational schema is centered around the <code>Product</code> model (<code>backend/products/models.py</code>):",
        body_style
    ))

    db_data = [
        [Paragraph("<b>Field Name</b>", body_style), Paragraph("<b>Data Type</b>", body_style), Paragraph("<b>Constraints / Default</b>", body_style), Paragraph("<b>Description</b>", body_style)],
        [Paragraph("<code>id</code>", body_style), Paragraph("AutoField", body_style), Paragraph("Primary Key", body_style), Paragraph("Unique product ID.", body_style)],
        [Paragraph("<code>name</code>", body_style), Paragraph("CharField(255)", body_style), Paragraph("Required", body_style), Paragraph("Full product title.", body_style)],
        [Paragraph("<code>category</code>", body_style), Paragraph("CharField(50)", body_style), Paragraph("6 Choice Enum", body_style), Paragraph("Skincare, Haircare, etc.", body_style)],
        [Paragraph("<code>price</code>", body_style), Paragraph("DecimalField", body_style), Paragraph("max_digits=10, dec=2", body_style), Paragraph("Base price in INR.", body_style)],
        [Paragraph("<code>discount_percent</code>", body_style), Paragraph("PositiveInt", body_style), Paragraph("default=0", body_style), Paragraph("Percentage discount.", body_style)],
        [Paragraph("<code>skin_type</code>", body_style), Paragraph("CharField(50)", body_style), Paragraph("default='all'", body_style), Paragraph("Target skin compatibility.", body_style)],
        [Paragraph("<code>concern_tags</code>", body_style), Paragraph("CharField(255)", body_style), Paragraph("Comma-separated", body_style), Paragraph("Target skin/hair goals.", body_style)],
        [Paragraph("<code>key_ingredients</code>", body_style), Paragraph("CharField(255)", body_style), Paragraph("Required", body_style), Paragraph("Primary active ingredients.", body_style)],
        [Paragraph("<code>full_ingredients</code>", body_style), Paragraph("TextField", body_style), Paragraph("Required", body_style), Paragraph("Full INCI ingredient list.", body_style)],
        [Paragraph("<code>usage_instructions</code>", body_style), Paragraph("TextField", body_style), Paragraph("Required", body_style), Paragraph("AM/PM routine directions.", body_style)],
        [Paragraph("<code>caution_info</code>", body_style), Paragraph("TextField", body_style), Paragraph("Required", body_style), Paragraph("Patch test & safety notes.", body_style)]
    ]
    db_table = Table(db_data, colWidths=[90, 80, 114, 220])
    db_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('PADDING', (0,0), (-1,-1), 4),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
    ]))
    story.append(db_table)

    story.append(PageBreak())

    # ── SECTION 8 & 9: API SPECIFICATION & RECOMMENDATION ENGINE ──────────
    story.append(Paragraph("8. REST API Specification", h1_style))
    story.append(Paragraph("The backend exposes standard REST endpoints adhering to HTTP status conventions:", body_style))

    api_data = [
        [Paragraph("<b>Endpoint</b>", body_style), Paragraph("<b>Method</b>", body_style), Paragraph("<b>Key Parameters</b>", body_style), Paragraph("<b>Status & Response Scope</b>", body_style)],
        [Paragraph("<code>/api/products/</code>", body_style), Paragraph("GET", body_style), Paragraph("<code>category, search, min_price, max_price, ordering</code>", body_style), Paragraph("<code>200 OK</code>: Paginated list of product records.", body_style)],
        [Paragraph("<code>/api/products/&lt;id&gt;/</code>", body_style), Paragraph("GET", body_style), Paragraph("<code>id (int)</code>", body_style), Paragraph("<code>200 OK</code>: Single product details; <code>404</code> if missing.", body_style)],
        [Paragraph("<code>/api/products/categories/</code>", body_style), Paragraph("GET", body_style), Paragraph("None", body_style), Paragraph("<code>200 OK</code>: Categories with count of items.", body_style)],
        [Paragraph("<code>/api/recommendations/</code>", body_style), Paragraph("POST", body_style), Paragraph("<code>category, skin_type, concern, budget_max, preferred_ingredients</code>", body_style), Paragraph("<code>200 OK</code>: Ranked matches with match % and explanations.", body_style)],
        [Paragraph("<code>/api/faq/</code>", body_style), Paragraph("POST", body_style), Paragraph("<code>question (str), product_id (opt)</code>", body_style), Paragraph("<code>200 OK</code>: Catalog answers with non-medical disclaimer.", body_style)],
        [Paragraph("<code>/api/health/</code>", body_style), Paragraph("GET", body_style), Paragraph("None", body_style), Paragraph("<code>200 OK</code>: Health check status.", body_style)]
    ]
    api_table = Table(api_data, colWidths=[120, 50, 164, 170])
    api_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('PADDING', (0,0), (-1,-1), 4.5),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
    ]))
    story.append(api_table)

    story.append(Spacer(1, 10))
    story.append(Paragraph("9. Recommendation Engine & Matching Rules", h1_style))
    story.append(Paragraph(
        "The recommendation algorithm (<code>backend/products/services/recommender.py</code>) executes a deterministic weighted scoring formula:",
        body_style
    ))

    formula_box = [
        [Paragraph("<b>Mathematical Scoring Formula:</b>", h2_style)],
        [Paragraph(
            "<b>Total Score = Category Match (Hard Constraint) + Skin Type Match (30 pts) + Concern Match (35 pts) + Ingredient Boost (20 pts) + Budget Compliance (15 pts)</b><br/><br/>"
            "• <b>Category Filter:</b> If product category != user category, product is excluded (Score = 0).<br/>"
            "• <b>Skin Compatibility (30 pts):</b> 30 pts for exact skin match; 20 pts for universal ('all') formulas; 5 pts otherwise.<br/>"
            "• <b>Concern Alignment (35 pts):</b> 35 pts if concern in product tags; 20 pts if matched in description.<br/>"
            "• <b>Ingredient Preference (20 pts):</b> 10 pts per matching preferred active ingredient (up to 20 pts).<br/>"
            "• <b>Budget Compliance (15 pts):</b> 15 pts if price &le; budget; linearly scaled down if exceeding budget.<br/>"
            "• <b>Budget Alternative Fallback:</b> If zero products satisfy budget, closest formulation matches are returned with transparent budget notes.",
            body_style
        )]
    ]
    formula_table = Table(formula_box, colWidths=[504])
    formula_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(formula_table)

    story.append(PageBreak())

    # ── SECTION 10 & 11: TESTING & ROADMAP ────────────────────────────────
    story.append(Paragraph("10. Testing & Quality Assurance", h1_style))
    story.append(Paragraph(
        "The project has undergone rigorous automated backend unit testing and end-to-end browser user journey validation. "
        "All <b>26 automated unit tests</b> pass with a 100% pass rate:",
        body_style
    ))

    test_summary_data = [
        [Paragraph("<b>Test Suite Module</b>", body_style), Paragraph("<b>Test Cases Count</b>", body_style), Paragraph("<b>Coverage Scope</b>", body_style), Paragraph("<b>Result</b>", body_style)],
        [Paragraph("<code>ProductModelTests</code>", body_style), Paragraph("3 Tests", body_style), Paragraph("Model fields, discount calculations, concern list parsing.", body_style), Paragraph("<font color='#059669'><b>3 / 3 PASS</b></font>", body_style)],
        [Paragraph("<code>ProductApiTests</code>", body_style), Paragraph("6 Tests", body_style), Paragraph("Catalog listing, filters, keyword search, price range, categories.", body_style), Paragraph("<font color='#059669'><b>6 / 6 PASS</b></font>", body_style)],
        [Paragraph("<code>RecommendationTests</code>", body_style), Paragraph("6 Tests", body_style), Paragraph("Skincare matches, adaptive haircare, ingredient boost, budget fallbacks.", body_style), Paragraph("<font color='#059669'><b>6 / 6 PASS</b></font>", body_style)],
        [Paragraph("<code>FaqAssistantTests</code>", body_style), Paragraph("7 Tests", body_style), Paragraph("Ingredient lookup, usage directions, cautions, shipping, fallbacks.", body_style), Paragraph("<font color='#059669'><b>7 / 7 PASS</b></font>", body_style)],
        [Paragraph("<code>ApiAppHealthTests</code>", body_style), Paragraph("4 Tests", body_style), Paragraph("Root health checks and CORS response validation.", body_style), Paragraph("<font color='#059669'><b>4 / 4 PASS</b></font>", body_style)]
    ]
    test_table = Table(test_summary_data, colWidths=[120, 70, 234, 80])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('PADDING', (0,0), (-1,-1), 4.5),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
    ]))
    story.append(test_table)

    story.append(Spacer(1, 10))
    story.append(Paragraph("11. Limitations & Future Roadmap", h1_style))
    story.append(Paragraph("<b>Current Prototype Limitations:</b>", h2_style))
    story.append(Paragraph("• <i>Simulated Transactions:</i> Checkout is simulated without real credit card processing.", bullet_style))
    story.append(Paragraph("• <i>Local Cache Persistence:</i> Wishlist and cart persist in browser localStorage rather than cloud accounts.", bullet_style))
    story.append(Paragraph("• <i>Sample Database:</i> Seeded with 12 multi-category products for demonstration purposes.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Production Roadmap:</b>", h2_style))
    story.append(Paragraph("• <b>Phase 1:</b> Mobile Barcode & INCI Label OCR Scanner using camera input.", bullet_style))
    story.append(Paragraph("• <b>Phase 2:</b> AM/PM Daily Routine Tracker with Sunscreen reminders.", bullet_style))
    story.append(Paragraph("• <b>Phase 3:</b> Cloud User Profiles & Certified Dermatologist Q&A integration.", bullet_style))
    story.append(Paragraph("• <b>Phase 4:</b> Live Payment Gateway (Razorpay/Stripe) and ERP inventory integration.", bullet_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("12. Conclusion & References", h1_style))
    story.append(Paragraph(
        "Joyory SmartMatch demonstrates that complex cosmetic shopping can be made delightful, transparent, and safe through "
        "rule-based matching algorithms and modern full-stack web engineering.",
        body_style
    ))
    story.append(Paragraph("<b>References:</b>", h2_style))
    story.append(Paragraph("1. Hackathon Task Brief: Smart Shopping Experience for Beauty & Personal Care (Joyory).", bullet_style))
    story.append(Paragraph("2. Django 5.x & Django REST Framework Official Documentation (https://docs.djangoproject.com/).", bullet_style))
    story.append(Paragraph("3. React 18 & Bootstrap 5 Documentation (https://react.dev/, https://getbootstrap.com/).", bullet_style))
    story.append(Paragraph("4. International Nomenclature of Cosmetic Ingredients (INCI) Standards.", bullet_style))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated at: {output_path}")

if __name__ == '__main__':
    target = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs', 'Joyory_SmartMatch_Development_Documentation.pdf'))
    build_pdf(target)
