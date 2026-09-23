import fitz
from app.schemas.report import ClaimReadinessReportResponse


def render_claim_readiness_pdf(report: ClaimReadinessReportResponse) -> bytes:
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    c_primary = (0.02, 0.44, 0.65)
    c_dark = (0.09, 0.13, 0.24)
    c_text = (0.2, 0.25, 0.33)
    c_light_bg = (0.96, 0.98, 1.0)
    c_border = (0.82, 0.88, 0.94)
    c_emerald = (0.06, 0.6, 0.4)
    c_red = (0.75, 0.15, 0.15)

    # Banner
    page.draw_rect(fitz.Rect(0, 0, 595, 75), color=c_dark, fill=c_dark)
    page.insert_text(fitz.Point(40, 42), "CareWise", fontsize=22, fontname="helv", color=(1, 1, 1))
    page.insert_text(fitz.Point(145, 40), "|  AI CLAIM READINESS REPORT", fontsize=11, fontname="helv", color=(0.3, 0.8, 0.95))
    page.insert_text(fitz.Point(40, 58), f"Policy: {report.policy_name}", fontsize=8, fontname="helv", color=(0.7, 0.75, 0.85))
    page.insert_text(fitz.Point(420, 42), f"Report ID: {report.report_id}", fontsize=8, fontname="helv", color=(0.8, 0.85, 0.95))
    page.insert_text(fitz.Point(420, 56), f"Generated: {report.generated_at}", fontsize=8, fontname="helv", color=(0.8, 0.85, 0.95))

    y = 95

    # AI Summary box
    page.draw_rect(fitz.Rect(40, y, 555, y + 90), color=c_border, fill=c_light_bg)
    page.insert_text(fitz.Point(55, y + 18), "AI PLAIN-ENGLISH SUMMARY", fontsize=9, fontname="helv", color=c_primary)
    words = report.ai_summary.split()
    lines, line = [], ""
    for w in words:
        if len(line) + len(w) < 95:
            line += w + " "
        else:
            lines.append(line)
            line = w + " "
    lines.append(line)
    for i, l in enumerate(lines[:5]):
        page.insert_text(fitz.Point(55, y + 36 + i * 13), l.strip(), fontsize=8.5, fontname="helv", color=c_dark)

    y += 105

    # Recommendation callout
    page.draw_rect(fitz.Rect(40, y, 555, y + 34), color=c_emerald, fill=(0.95, 1.0, 0.97))
    page.insert_text(fitz.Point(55, y + 21), f"RECOMMENDED: {report.recommended_hospital}  |  Potential Savings vs riskiest option: Rs.{report.savings_vs_riskiest:,.0f}", fontsize=9, fontname="helv", color=c_emerald)

    y += 55

    # Hospital comparison table
    page.insert_text(fitz.Point(40, y), "HOSPITAL COST COMPARISON", fontsize=11, fontname="helv", color=c_dark)
    y += 20
    page.draw_rect(fitz.Rect(40, y, 555, y + 22), color=c_border, fill=(0.92, 0.95, 0.98))
    headers = ["Hospital", "Network", "Total Bill", "Out-of-Pocket", "Risk"]
    xpos = [50, 220, 330, 420, 500]
    for h, x in zip(headers, xpos):
        page.insert_text(fitz.Point(x, y + 15), h, fontsize=8, fontname="helv", color=c_dark)
    y += 22

    for comp in report.comparisons[:6]:
        risk_color = c_emerald if comp.risk_tier == "RECOMMENDED" else (c_red if comp.risk_tier == "FINANCIAL_RISK" else c_text)
        page.draw_rect(fitz.Rect(40, y, 555, y + 22), color=c_border, fill=(1, 1, 1))
        page.insert_text(fitz.Point(50, y + 15), comp.hospital_name[:26], fontsize=8, fontname="helv", color=c_dark)
        page.insert_text(fitz.Point(220, y + 15), comp.network_status.replace("_", " ").title()[:16], fontsize=7.5, fontname="helv", color=c_text)
        page.insert_text(fitz.Point(330, y + 15), f"Rs.{comp.total_bill:,.0f}", fontsize=8, fontname="helv", color=c_dark)
        page.insert_text(fitz.Point(420, y + 15), f"Rs.{comp.estimated_out_of_pocket:,.0f}", fontsize=8, fontname="helv", color=c_dark)
        page.insert_text(fitz.Point(500, y + 15), comp.risk_tier.replace("_", " ").title()[:14], fontsize=7.5, fontname="helv", color=risk_color)
        y += 22

    y += 30
    page.draw_line(fitz.Point(40, y), fitz.Point(555, y), color=c_border, width=1)
    page.insert_text(fitz.Point(40, y + 15),
        "AI-generated using CareWise's grounded policy extraction. Verify all figures with your insurer/TPA before admission.",
        fontsize=7, fontname="helv", color=c_text)

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes
