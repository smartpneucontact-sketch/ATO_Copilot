#!/usr/bin/env python3
"""Generate the ATO Copilot product brief PDF."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

INK = (15, 22, 38)
INK_SOFT = (60, 70, 90)
MUTED = (130, 140, 158)
NAVY = (30, 64, 124)
NAVY_SOFT = (228, 235, 246)
BORDER = (215, 220, 230)
CODE_BG = (244, 246, 250)
CODE_INK = (40, 50, 75)
ROW_ALT = (250, 251, 253)

PAGE_W = 612
MARGIN = 56
CONTENT_W = PAGE_W - 2 * MARGIN

FONT_DIR = "/System/Library/Fonts/Supplemental"
FONT = "Body"
MONO = "Mono"


class Brief(FPDF):
    def footer(self):
        self.set_y(-32)
        self.set_font(FONT, size=8)
        self.set_text_color(*MUTED)
        self.set_draw_color(*BORDER)
        self.set_line_width(0.4)
        self.line(MARGIN, self.get_y(), PAGE_W - MARGIN, self.get_y())
        self.set_y(-26)
        self.cell(0, 10, "ATO Copilot  ·  portfolio brief", align="L")
        self.set_y(-26)
        self.cell(0, 10, f"page {self.page_no()} of {{nb}}", align="R")


def _register_fonts(pdf: FPDF) -> None:
    pdf.add_font(FONT, "", f"{FONT_DIR}/Arial.ttf")
    pdf.add_font(FONT, "B", f"{FONT_DIR}/Arial Bold.ttf")
    pdf.add_font(FONT, "I", f"{FONT_DIR}/Arial Italic.ttf")
    pdf.add_font(FONT, "BI", f"{FONT_DIR}/Arial Bold Italic.ttf")
    pdf.add_font(MONO, "", f"{FONT_DIR}/Courier New.ttf")


def rule(pdf: FPDF, width: float = 72, height: float = 2.5) -> None:
    pdf.set_fill_color(*NAVY)
    pdf.rect(pdf.get_x(), pdf.get_y(), width, height, "F")
    pdf.ln(height + 14)


def h1(pdf: FPDF, text: str) -> None:
    pdf.set_font(FONT, "B", 30)
    pdf.set_text_color(*INK)
    pdf.cell(0, 36, text, new_x="LMARGIN", new_y="NEXT")


def h2(pdf: FPDF, text: str) -> None:
    pdf.ln(4)
    pdf.set_font(FONT, "B", 9)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 12, text.upper(), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def body(pdf: FPDF, text: str, size: int = 10.5) -> None:
    pdf.set_font(FONT, "", size)
    pdf.set_text_color(*INK_SOFT)
    pdf.multi_cell(0, 15, text, new_x="LMARGIN", new_y="NEXT")


def bullets(pdf: FPDF, items: list[str]) -> None:
    pdf.set_font(FONT, "", 10.5)
    pdf.set_text_color(*INK_SOFT)
    for item in items:
        x0 = pdf.get_x()
        pdf.set_x(x0 + 4)
        pdf.cell(10, 15, "•")
        pdf.set_x(x0 + 16)
        pdf.multi_cell(CONTENT_W - 16, 15, item, new_x="LMARGIN", new_y="NEXT")


def hero_link_card(pdf: FPDF, primary_url: str, primary_display: str,
                   sub_lines: list[tuple[str, str, str | None]]) -> None:
    y0 = pdf.get_y()
    height = 36 + 28 + 18 * len(sub_lines) + 14
    pdf.set_fill_color(*NAVY_SOFT)
    pdf.set_draw_color(*NAVY)
    pdf.set_line_width(1.0)
    pdf.rect(MARGIN, y0, CONTENT_W, height, "DF")
    pdf.set_fill_color(*NAVY)
    pdf.rect(MARGIN, y0, 4, height, "F")

    pdf.set_xy(MARGIN + 18, y0 + 12)
    pdf.set_font(FONT, "B", 9)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 12, "OPEN THE LIVE DEMO", new_x="LMARGIN", new_y="NEXT")

    pdf.set_x(MARGIN + 18)
    pdf.set_font(FONT, "B", 17)
    pdf.set_text_color(*INK)
    pdf.cell(CONTENT_W - 36, 26, primary_display, new_x="LMARGIN", new_y="NEXT", link=primary_url)
    pdf.set_draw_color(*NAVY)
    pdf.set_line_width(0.8)
    text_w = pdf.get_string_width(primary_display)
    pdf.line(MARGIN + 18, y0 + 46, MARGIN + 18 + text_w, y0 + 46)

    pdf.ln(4)
    for label, value, url in sub_lines:
        pdf.set_x(MARGIN + 18)
        pdf.set_font(FONT, "B", 10)
        pdf.set_text_color(*INK)
        pdf.cell(80, 16, label)
        pdf.set_font(FONT, "", 10)
        if url:
            pdf.set_text_color(*NAVY)
            pdf.cell(0, 16, value, new_x="LMARGIN", new_y="NEXT", link=url)
        else:
            pdf.set_text_color(*INK_SOFT)
            pdf.cell(0, 16, value, new_x="LMARGIN", new_y="NEXT")
    pdf.set_y(y0 + height + 12)


def stack_table(pdf: FPDF, rows: list[tuple[str, str]]) -> None:
    col_w = CONTENT_W / 2
    row_h = 22
    pdf.set_fill_color(*INK)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(FONT, "B", 9)
    pdf.cell(col_w, row_h, "  THIS DEMO", border=0, fill=True)
    pdf.cell(col_w, row_h, "  STATE STREET PRODUCTION", new_x="LMARGIN", new_y="NEXT", border=0, fill=True)
    pdf.set_font(FONT, "", 10)
    for i, (left, right) in enumerate(rows):
        bg = ROW_ALT if i % 2 == 0 else (255, 255, 255)
        pdf.set_fill_color(*bg)
        pdf.set_text_color(*INK)
        pdf.set_draw_color(*BORDER)
        pdf.cell(col_w, row_h, "  " + left, border="B", fill=True)
        pdf.set_text_color(*INK_SOFT)
        pdf.cell(col_w, row_h, "  " + right, new_x="LMARGIN", new_y="NEXT", border="B", fill=True)
    pdf.ln(6)


def trace_block(pdf: FPDF, title: str, lines: list[str]) -> None:
    y0 = pdf.get_y()
    line_h = 13
    pad_y = 12
    height = pad_y * 2 + line_h * len(lines) + 16
    pdf.set_fill_color(*CODE_BG)
    pdf.set_draw_color(*BORDER)
    pdf.set_line_width(0.4)
    pdf.rect(MARGIN, y0, CONTENT_W, height, "DF")
    pdf.set_xy(MARGIN + 14, y0 + 10)
    pdf.set_font(FONT, "B", 8)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 11, title.upper(), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(MONO, "", 8.8)
    pdf.set_text_color(*CODE_INK)
    for line in lines:
        pdf.set_x(MARGIN + 14)
        pdf.cell(0, line_h, line, new_x="LMARGIN", new_y="NEXT")
    pdf.set_y(y0 + height + 10)


def build() -> Path:
    pdf = Brief("portrait", "pt", "letter")
    pdf.set_margins(MARGIN, MARGIN, MARGIN)
    pdf.set_auto_page_break(True, margin=66)
    pdf.alias_nb_pages()
    _register_fonts(pdf)
    pdf.add_page()

    h1(pdf, "ATO Copilot")
    pdf.set_font(FONT, "", 13)
    pdf.set_text_color(*INK_SOFT)
    pdf.cell(0, 18, "AI triage for ATO / NTAP governance workflows.",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    rule(pdf)

    pdf.set_font(FONT, "B", 10)
    pdf.set_text_color(*INK)
    pdf.cell(0, 14, "Arsen Khanguieldyan", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(FONT, "", 10)
    pdf.set_text_color(*INK_SOFT)
    pdf.cell(0, 14, "arsen.khanguieldyan@gmail.com", new_x="LMARGIN", new_y="NEXT",
             link="mailto:arsen.khanguieldyan@gmail.com")
    pdf.cell(0, 14, "Portfolio piece for State Street", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    hero_link_card(
        pdf,
        primary_url="https://ato-copilot.up.railway.app",
        primary_display="ato-copilot.up.railway.app",
        sub_lines=[
            ("Source code", "github.com/[your-handle]/ato-copilot", "https://github.com/"),
            ("Model", "Anthropic Claude Sonnet 4.6  ·  ~$0.07 per request", None),
        ],
    )

    h2(pdf, "Summary")
    body(pdf,
         "ATO Copilot is a working portfolio demo aligned to the State Street ATO AI Process and "
         "Automation Engineer (AVP) role. A delivery team's free-text NTAP / ATO request goes in. "
         "A structured ATO package comes out — Approved Technology List check, NIST 800-53 control "
         "mapping, reference-architecture review, risk classification, cycle-time estimate, "
         "recommended decision (ATO-APPROVED / CONDITIONS / DENIED / ARB-ROUTING). Every claim "
         "cited back to a retrieved governance document. The agent loop and corpus contract map "
         "cleanly onto a Microsoft Copilot Studio + ServiceNow + Flexera production deployment.")

    h2(pdf, "The problem this solves")
    body(pdf,
         "Enterprise ATO/NTAP processing today is a queue. Submissions sit waiting for a human "
         "reviewer to manually check the ATL, identify applicable controls, walk the reference "
         "architecture, classify risk, and route. Cycle times of 5–20 days are typical; cycle-time "
         "improvement is one of the State Street JD's named KPIs. The work is high-volume, "
         "citation-bound, and procedurally regular — the textbook shape of an AI-augmented "
         "governance workflow.")

    h2(pdf, "What it ships")
    bullets(pdf, [
        "Single AI agent (ATORequestAgent) that runs a tool-use loop on Claude Sonnet 4.6: "
        "retrieve governance corpus, classify risk, estimate cycle time, then draft the structured "
        "ATO package.",
        "Synthetic but realistic governance corpus: 3 ATL entries (PostgreSQL/RDS, Kafka/MSK, "
        "Azure OpenAI), 2 NIST 800-53 control family summaries, reference architecture patterns "
        "with explicit anti-patterns, 2 prior ATO precedents (one Low + one High-risk).",
        "FastAPI service with visitor-notify (Resend HTTPS), modern dark UI with semantic rendering "
        "of every output field (ATL status, control mapping, risk badge, decision badge, cycle "
        "time, open items, rationale), deployed to Railway.",
        "Production-shape exactly: agent loop + tool-use ports to Copilot Studio with no code "
        "redesign; corpus contract maps to Azure AI Search over the existing SharePoint governance "
        "library; FastAPI surface ports to a ServiceNow / Power Automate workflow.",
    ])

    pdf.add_page()

    h2(pdf, "How it maps to State Street's stack")
    body(pdf,
         "Every component in this demo has a 1:1 production target. The agent loop and the corpus "
         "contract are the durable parts; the surfaces around them adapt to State Street's existing "
         "Microsoft / ServiceNow / Flexera footprint.")
    pdf.ln(4)
    stack_table(pdf, [
        ("Anthropic SDK + Claude Sonnet 4.6", "Microsoft Copilot Studio + Azure OpenAI (gpt-4o)"),
        ("BM25 over markdown corpus", "Azure AI Search / SharePoint Search on governance KB"),
        ("FastAPI + Pydantic backend", "ServiceNow workflow + Azure Function via Power Automate"),
        ("Single-page HTML UI", "ServiceNow service portal / Power Apps canvas"),
        ("JSONL traces", "Splunk + Azure Monitor"),
        ("Synthetic ATL corpus", "Flexera ITAM data + SharePoint ATL document library"),
        ("YAML eval suite + GitHub Actions", "Same — governance for the governance tool itself"),
        ("Visitor-notify webhook", "Power Automate flow → Outlook / Teams alert"),
    ])

    h2(pdf, "Sample agent reasoning (real run)")
    body(pdf,
         "Example: a delivery team asks to upgrade PostgreSQL 14 → 16 on RDS for an internal "
         "reporting dashboard. Tool sequence is fully traced.")
    trace_block(pdf, "run_demo  ·  3 steps  ·  internal db upgrade request", [
        "step 0  retrieve(query=\"PostgreSQL RDS managed approved technology list\",",
        "                  source_type=\"atl\")",
        "        -> atl:postgresql_rds                            (score 14.2)",
        "",
        "step 0  retrieve(query=\"internal database approval prior ATO precedent\",",
        "                  source_type=\"prior_ato\")",
        "        -> prior_ato:ato_0231                            (score 9.1)",
        "",
        "step 0  classify_risk(handles_client_funds=false,",
        "                       handles_pii_or_pci=false,",
        "                       is_public_facing=false,",
        "                       is_new_to_atl=false,",
        "                       critical_business_function=false)",
        "        -> risk_band=\"low\", score=0",
        "",
        "step 1  estimate_cycle_time(risk_band=\"low\", is_new_to_atl=false,",
        "                              needs_arb_review=false)",
        "        -> estimated_days_to_decision=2",
        "",
        "step 2  final answer (cited): ATO-APPROVED, low risk, 2-day cycle,",
        "        no ARB review, inherits ATL-2024-DB-0017.",
    ])

    h2(pdf, "Why this fits the role")
    body(pdf,
         "The JD asks for someone who modernizes, automates, and governs ATO/ATL lifecycle "
         "processes using workflow automation and AI-enabled capabilities. ATO Copilot is exactly "
         "that artifact: a real workflow-automation tool that compresses cycle time while preserving "
         "control rigor (citations, audit trail, ARB-routing flag). The agent pattern transfers "
         "trivially — same loop for vendor-risk intake, exception requests, control evidence "
         "collection, or recertification triage. Weeks not quarters.")

    h2(pdf, "Honest gaps")
    bullets(pdf, [
        "Synthetic corpus, not real ATL / control catalogs. Real deployment needs the Flexera ITAM "
        "feed + SharePoint governance library and a refresh cadence.",
        "No ServiceNow / Power Platform integration yet — this is the FastAPI prototype demonstrating "
        "the pattern. The production wire is a custom connector behind an Azure Function.",
        "No human-in-the-loop UI for InfoSec / ARB reviewer to accept / edit / route the draft "
        "package — that's the next layer of UX work.",
        "Eval suite is shaped but not populated with a labeled golden set; production would need "
        "100+ historical ATO decisions to score precision / recall on the recommendation field.",
    ])

    h2(pdf, "In one line")
    pdf.set_font(FONT, "I", 11.5)
    pdf.set_text_color(*INK)
    pdf.multi_cell(0, 16,
                   "Speed with safety — AI-triaged ATO/NTAP packages with full citation trail, "
                   "shippable to a real governance workflow on the Microsoft + ServiceNow + Flexera "
                   "stack State Street already runs.",
                   new_x="LMARGIN", new_y="NEXT")

    out = Path("ATO_Copilot_Brief.pdf").resolve()
    pdf.output(str(out))
    return out


if __name__ == "__main__":
    print(f"Wrote: {build()}")
