#!/usr/bin/env python3
"""Generate Arsen's resume PDF tailored for State Street (ATO AI Process & Automation Engineer, AVP)."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

INK = (15, 22, 38)
INK_SOFT = (60, 70, 90)
MUTED = (130, 140, 158)
RULE = (215, 220, 230)
ACCENT = (30, 64, 124)  # institutional navy

PAGE_W = 612
PAGE_H = 792
MARGIN_X = 48
MARGIN_TOP = 42
MARGIN_BOTTOM = 42
CONTENT_W = PAGE_W - 2 * MARGIN_X

FONT_DIR = "/System/Library/Fonts/Supplemental"
FONT = "Body"


def _register_fonts(pdf: FPDF) -> None:
    pdf.add_font(FONT, "", f"{FONT_DIR}/Arial.ttf")
    pdf.add_font(FONT, "B", f"{FONT_DIR}/Arial Bold.ttf")
    pdf.add_font(FONT, "I", f"{FONT_DIR}/Arial Italic.ttf")
    pdf.add_font(FONT, "BI", f"{FONT_DIR}/Arial Bold Italic.ttf")


def section(pdf: FPDF, title: str) -> None:
    pdf.ln(7)
    pdf.set_font(FONT, "B", 10)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 12, title.upper(), new_x="LMARGIN", new_y="NEXT")
    y = pdf.get_y() + 1
    pdf.set_draw_color(*RULE)
    pdf.set_line_width(0.5)
    pdf.line(MARGIN_X, y, PAGE_W - MARGIN_X, y)
    pdf.ln(5)


def role_header(pdf: FPDF, company: str, location: str, dates: str, title: str) -> None:
    pdf.set_font(FONT, "B", 10.5)
    pdf.set_text_color(*INK)
    pdf.cell(CONTENT_W * 0.65, 14, company)
    pdf.set_font(FONT, "", 9.5)
    pdf.set_text_color(*INK_SOFT)
    pdf.cell(CONTENT_W * 0.35, 14, dates, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(FONT, "I", 9.5)
    pdf.cell(CONTENT_W * 0.65, 12, f"{title}  ·  {location}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def project_header(pdf: FPDF, name: str, year: str, links: list[tuple[str, str]]) -> None:
    pdf.set_font(FONT, "B", 10.5)
    pdf.set_text_color(*INK)
    pdf.cell(CONTENT_W * 0.65, 14, name)
    pdf.set_font(FONT, "", 9.5)
    pdf.set_text_color(*INK_SOFT)
    pdf.cell(CONTENT_W * 0.35, 14, year, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(FONT, "", 9)
    for i, (text, url) in enumerate(links):
        if i > 0:
            pdf.set_text_color(*MUTED)
            pdf.cell(pdf.get_string_width("   ·   "), 12, "   ·   ")
        pdf.set_text_color(*ACCENT)
        pdf.cell(pdf.get_string_width(text), 12, text, link=url)
    pdf.ln(13)


def bullets(pdf: FPDF, items: list[str], size: float = 9.5, line_h: float = 12.5) -> None:
    pdf.set_font(FONT, "", size)
    for item in items:
        pdf.set_text_color(*INK)
        pdf.set_x(MARGIN_X + 10)
        pdf.cell(8, line_h, "•")
        pdf.set_x(MARGIN_X + 20)
        pdf.set_text_color(*INK_SOFT)
        pdf.multi_cell(CONTENT_W - 20, line_h, item, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def skills_row(pdf: FPDF, label: str, items: str) -> None:
    pdf.set_font(FONT, "B", 9.5)
    pdf.set_text_color(*INK)
    pdf.cell(0, 13, label, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(FONT, "", 9.5)
    pdf.set_text_color(*INK_SOFT)
    pdf.set_x(MARGIN_X)
    pdf.multi_cell(CONTENT_W, 13, items, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def build() -> Path:
    pdf = FPDF("portrait", "pt", "letter")
    pdf.set_margins(MARGIN_X, MARGIN_TOP, MARGIN_X)
    pdf.set_auto_page_break(True, margin=MARGIN_BOTTOM)
    _register_fonts(pdf)
    pdf.add_page()

    pdf.set_font(FONT, "B", 24)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 30, "Arsen Khanguieldyan", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font(FONT, "", 10)
    pdf.set_text_color(*INK_SOFT)
    contact = ("arsen.khanguieldyan@gmail.com", "+1 (617) 655-4650", "Boston, MA, USA")
    sep = "   ·   "
    sep_w = pdf.get_string_width(sep)
    parts_w = [pdf.get_string_width(p) for p in contact]
    total_w = sum(parts_w) + sep_w * (len(contact) - 1)
    x = (PAGE_W - total_w) / 2
    pdf.set_x(x)
    for i, part in enumerate(contact):
        if i > 0:
            pdf.cell(sep_w, 14, sep)
        link = f"mailto:{part}" if i == 0 else ""
        pdf.set_text_color(*ACCENT if i == 0 else INK_SOFT)
        pdf.cell(parts_w[i], 14, part, link=link)
        pdf.set_text_color(*INK_SOFT)
    pdf.ln(20)
    pdf.set_draw_color(*RULE)
    pdf.set_line_width(0.6)
    pdf.line(MARGIN_X, pdf.get_y(), PAGE_W - MARGIN_X, pdf.get_y())
    pdf.ln(6)

    # Summary — State Street flavored (governance + automation + Microsoft / Azure stack)
    pdf.set_font(FONT, "", 10)
    pdf.set_text_color(*INK_SOFT)
    pdf.multi_cell(0, 13.5,
                   "Process-automation engineer with 7 years building and operating production systems "
                   "in highly regulated environments (defense, automotive, enterprise). Microsoft Azure "
                   "DevOps Engineer Expert (AZ-400). Hands-on with AI-enabled workflow automation, "
                   "data integration, requirements engineering, and SDLC / V&V discipline. Recent "
                   "focus: AI agents that triage governance workflows (ATO, NTAP, compliance review).",
                   new_x="LMARGIN", new_y="NEXT")

    # Selected Projects — lead with ATO Copilot
    section(pdf, "Selected Projects")
    project_header(pdf,
                   "ATO Copilot — AI Triage for ATO/NTAP Governance Workflows",
                   "2026",
                   [
                       ("github.com/[your-handle]/ato-copilot", "https://github.com/"),
                   ])
    bullets(pdf, [
        "End-to-end AI workflow tool: free-text NTAP request goes in, structured ATO package comes "
        "out — Approved Technology List check, NIST 800-53 control mapping, reference-architecture "
        "review, risk classification, cycle-time estimate, recommended decision (ATO-APPROVED / "
        "CONDITIONS / DENIED / ARB-ROUTING).",
        "Agentic AI loop on Claude Sonnet 4.6 with RAG over a synthetic governance corpus (ATL "
        "entries, NIST control families, reference architecture patterns, prior ATO precedents). "
        "Three custom tools: retrieve, classify_risk, estimate_cycle_time.",
        "Production-target architecture explicitly mapped onto State Street's stack: Microsoft "
        "Copilot Studio + Azure OpenAI, ServiceNow workflow + Power Automate connector, "
        "Azure AI Search / SharePoint, Flexera ITAM data, Splunk + Azure Monitor telemetry.",
        "FastAPI service with visitor-notify (Resend HTTPS API), modern dark UI with semantic "
        "rendering of every output field, Railway deploy ready.",
    ])

    # Also list sister projects briefly
    project_header(pdf,
                   "Site Copilot & Case Pilot — Sister AI-Workflow Demos",
                   "2026",
                   [
                       ("github.com/smartpneucontact-sketch/Sufflk",
                        "https://github.com/smartpneucontact-sketch/Sufflk"),
                       ("github.com/smartpneucontact-sketch/Scaffold",
                        "https://github.com/smartpneucontact-sketch/Scaffold"),
                   ])
    bullets(pdf, [
        "Same agent pattern applied to different regulated domains: construction RFI / Daily Report "
        "triage (Site Copilot) and surgical case intake with implant configuration + compliance "
        "checks (Case Pilot). Reinforces that the workflow-automation pattern transfers cleanly — "
        "swap the corpus, swap the prompt, ship a new agent in days.",
    ])

    # Experience
    section(pdf, "Professional Experience")

    role_header(pdf, "Hyperion", "Yerevan, Armenia", "Nov 2022 – Jun 2025", "Head of Engineering")
    bullets(pdf, [
        "Shipped a fully autonomous AI defense drone — acquired by strategic buyer; owned the full "
        "engineering lifecycle across AI software, computer vision, firmware, electronics, "
        "mechanical, and composites.",
        "Operated under strict regulated-industry process discipline — requirements engineering, "
        "design reviews, traceability matrix, risk register, formal V&V, ITIL-shaped change "
        "management — directly applicable to State Street's SDLC + ATO / ARB governance work.",
        "Led a multidisciplinary team and managed cross-functional dependencies with vendors, "
        "regulators, and customer stakeholders.",
        "Built edge-deployed computer vision for GPS-denied navigation at 96% accuracy; validated "
        "across 3,000 flight-test hours.",
    ])

    role_header(pdf, "Deloitte", "Luxembourg", "Apr 2021 – Jun 2022", "Data Analyst")
    bullets(pdf, [
        "Led migration of multi-source enterprise data into a unified Azure-hosted repository with "
        "static + dynamic metadata governance; exposed via REST API to a single-page web app. "
        "Standard governance / data-architecture engagement for a regulated client.",
        "Evaluated nine AutoML platforms (IaaS / PaaS / SaaS) against predefined test protocols; "
        "produced selection rationale, risk-control mapping, and executive presentations.",
    ])

    role_header(pdf,
                "Forschungsgesellschaft Umformtechnik mbH",
                "Stuttgart, Germany",
                "May 2019 – Mar 2021",
                "Data Engineer")
    bullets(pdf, [
        "Shipped a tool-wear classifier (CNN, 82% accuracy) into TRUMPF Group's next-generation "
        "punching machines; co-authored \"Data-Driven Tool Wear Classification with a CNN in "
        "Punching Machines\" (Feb 2020). Production deployment with the full QA / approval cycle.",
        "Built a sensor-fusion IoT pipeline (force, distance, sound, lubrication) and an ML "
        "failure-prediction algorithm on Audi AG data — connecting operational telemetry into "
        "an actionable signals layer, the data-architecture pattern State Street's JD asks for.",
    ])

    role_header(pdf, "Audi AG", "Neckarsulm, Germany", "Apr 2018 – Dec 2018", "Software Developer")
    bullets(pdf, [
        "Built and deployed an Oracle APEX low-code web application that digitalized die-cast "
        "tooling improvements; rolled out internationally across Audi sites. Process-automation / "
        "paper-to-digital pattern.",
    ])

    # Skills — Microsoft / governance first ordering for State Street
    section(pdf, "Technical Skills")
    skills_row(pdf, "Process Automation & AI",
               "Microsoft Copilot-style AI workflow design, Agentic RAG, LLM tool-use, RPA-shaped "
               "thinking, requirements engineering, SDLC + V&V, ITIL processes")
    skills_row(pdf, "Microsoft / Azure",
               "Azure DevOps Engineer Expert (AZ-400), Azure Administrator (AZ-204), Azure "
               "Fundamentals (AZ-900), Azure Data Factory, Power Platform-shaped architecture "
               "(Power Apps, Power Automate, Copilot Studio applied via prototype), Active Directory")
    skills_row(pdf, "Governance & Risk",
               "Reference architecture review, security control frameworks (NIST 800-53 mapping in "
               "prototype), audit-readiness artifacts, regulated-industry process discipline "
               "(defense, automotive)")
    skills_row(pdf, "Data & Integration",
               "ETL / ELT design, REST APIs, sensor-fusion pipelines, vector stores, hybrid search "
               "(BM25 + dense), Azure AI Search-shaped retrieval, SQL")
    skills_row(pdf, "Engineering",
               "Python (expert), FastAPI, C/C++, Docker, Kubernetes, Terraform, GitHub Actions, "
               "AWS, Altium / PCB design, SolidWorks, Simulink")

    # Certifications
    section(pdf, "Certifications")
    pdf.set_font(FONT, "", 9.5)
    pdf.set_text_color(*INK_SOFT)
    pdf.multi_cell(0, 13,
                   "Microsoft Azure DevOps Engineer Expert (AZ-400)  ·  Microsoft Azure Administrator (AZ-204)  ·  "
                   "Microsoft Azure Fundamentals (AZ-900)  ·  AWS Cloud Practitioner  ·  TensorFlow Developer  ·  "
                   "Deep Learning in Computer Vision",
                   new_x="LMARGIN", new_y="NEXT")

    # Education
    section(pdf, "Education")
    pdf.set_font(FONT, "B", 10)
    pdf.set_text_color(*INK)
    pdf.cell(CONTENT_W * 0.7, 13, "Ecole Centrale d'Electronique  —  Paris, France")
    pdf.set_font(FONT, "", 9.5)
    pdf.set_text_color(*INK_SOFT)
    pdf.cell(CONTENT_W * 0.3, 13, "", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(FONT, "", 9.5)
    pdf.cell(CONTENT_W * 0.7, 12, "M.S. Computer Science & Engineering")
    pdf.cell(CONTENT_W * 0.3, 12, "Jun 2019", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(CONTENT_W * 0.7, 12, "B.S. Mathematics & Electronics")
    pdf.cell(CONTENT_W * 0.3, 12, "Jun 2017", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font(FONT, "B", 10)
    pdf.set_text_color(*INK)
    pdf.cell(CONTENT_W * 0.7, 13, "MIT Professional Education")
    pdf.set_font(FONT, "", 9.5)
    pdf.set_text_color(*INK_SOFT)
    pdf.cell(CONTENT_W * 0.3, 13, "Dec 2025 – Sep 2026", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(FONT, "I", 9.5)
    pdf.cell(0, 12, "Digital Transformation in the AI Age  (in progress)", new_x="LMARGIN", new_y="NEXT")

    # Languages
    section(pdf, "Languages")
    pdf.set_font(FONT, "", 9.5)
    pdf.set_text_color(*INK_SOFT)
    pdf.cell(0, 13,
             "English (proficient)  ·  French (fluent)  ·  German (fluent)  ·  Armenian (native)",
             new_x="LMARGIN", new_y="NEXT")

    out = Path("Arsen_Khanguieldyan_Resume_state_street.pdf").resolve()
    pdf.output(str(out))
    return out


if __name__ == "__main__":
    print(f"Wrote: {build()}")
