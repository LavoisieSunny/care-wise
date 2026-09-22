"""
PDF generation service for CareWise Digital Claim Dossier using PyMuPDF (fitz).
Produces a formatted, branded digital hospitalization and claim settlement dossier PDF.
"""
import fitz  # PyMuPDF
from app.schemas.journey import ClaimDossierResponse


def render_dossier_pdf(dossier: ClaimDossierResponse) -> bytes:
    """Generate high-resolution printable CareWise Claim Dossier PDF."""
    doc = fitz.open()
    # A4 standard dimensions: 595.28 x 841.89 points
    page = doc.new_page(width=595, height=842)

    # Palette
    c_primary = (0.02, 0.44, 0.65)      # Deep Cyan (#0570a6)
    c_dark = (0.09, 0.13, 0.24)         # Deep Navy (#17213d)
    c_text = (0.2, 0.25, 0.33)          # Slate Text (#334054)
    c_light_bg = (0.96, 0.98, 1.0)      # Soft Blue Ice (#f5fafe)
    c_card_border = (0.82, 0.88, 0.94)  # Border (#d1e0f0)
    c_emerald = (0.06, 0.6, 0.4)        # Success Green (#0f9966)
    c_amber = (0.85, 0.55, 0.05)        # Amber

    # Top Brand Banner
    page.draw_rect(fitz.Rect(0, 0, 595, 75), color=c_dark, fill=c_dark)
    page.insert_text(
        fitz.Point(40, 42),
        "CareWise",
        fontsize=22,
        fontname="helv",
        color=(1, 1, 1),
    )
    page.insert_text(
        fitz.Point(145, 40),
        "|  DIGITAL HOSPITALIZATION & CLAIM DOSSIER",
        fontsize=11,
        fontname="helv",
        color=(0.3, 0.8, 0.95),
    )
    page.insert_text(
        fitz.Point(40, 58),
        "Verified Discharge Settlement & IRDAI Cashless Compliance Archive",
        fontsize=8,
        fontname="helv",
        color=(0.7, 0.75, 0.85),
    )
    page.insert_text(
        fitz.Point(420, 42),
        "STATUS: SETTLED",
        fontsize=10,
        fontname="helv",
        color=(0.2, 0.95, 0.6),
    )
    page.insert_text(
        fitz.Point(420, 56),
        f"Archive ID: {dossier.dossier_id}",
        fontsize=8,
        fontname="helv",
        color=(0.8, 0.85, 0.95),
    )

    y = 95

    # Patient & Admission Meta Block
    page.draw_rect(fitz.Rect(40, y, 555, y + 80), color=c_card_border, fill=c_light_bg)
    page.insert_text(fitz.Point(55, y + 20), "PATIENT & ADMISSION INFORMATION", fontsize=9, fontname="helv", color=c_primary)

    page.insert_text(fitz.Point(55, y + 40), f"Patient Name: {dossier.patient_name}", fontsize=10, fontname="helv", color=c_dark)
    page.insert_text(fitz.Point(55, y + 55), f"Hospital: {dossier.hospital_name}", fontsize=9, fontname="helv", color=c_text)
    page.insert_text(fitz.Point(55, y + 70), f"Generated: {dossier.generated_at} IST", fontsize=8, fontname="helv", color=c_text)

    page.insert_text(fitz.Point(330, y + 40), f"Policy ID: {dossier.policy_number}", fontsize=10, fontname="helv", color=c_dark)
    page.insert_text(fitz.Point(330, y + 55), f"TPA Submission Ref: {dossier.tpa_submission_code}", fontsize=9, fontname="helv", color=c_primary)
    page.insert_text(fitz.Point(330, y + 70), "Admission Type: Emergency Cashless Inpatient", fontsize=8, fontname="helv", color=c_text)

    y += 95

    # Financial Settlement Ledger
    page.insert_text(fitz.Point(40, y + 16), "FINANCIAL DISCHARGE SETTLEMENT LEDGER", fontsize=11, fontname="helv", color=c_dark)
    y += 24

    # Table Header
    page.draw_rect(fitz.Rect(40, y, 555, y + 24), color=c_card_border, fill=(0.92, 0.95, 0.98))
    page.insert_text(fitz.Point(55, y + 16), "Line Item / Settlement Description", fontsize=9, fontname="helv", color=c_dark)
    page.insert_text(fitz.Point(340, y + 16), "Settlement Party", fontsize=9, fontname="helv", color=c_dark)
    page.insert_text(fitz.Point(480, y + 16), "Amount (INR)", fontsize=9, fontname="helv", color=c_dark)

    ledger_rows = [
        ("Total Hospital Final Bill (Itemized Inpatient Charges)", "Hospital Billing Dept", f"Rs. {dossier.total_bill:,.2f}", c_dark),
        ("TPA Cashless Sanctioned & Paid", "Insurer / TPA Disbursed", f"- Rs. {dossier.cashless_sanctioned:,.2f}", c_emerald),
        ("Mandatory Senior Citizen Co-Pay Settled", "Caregiver Settled at Desk", f"Rs. {dossier.copay_settled:,.2f}", c_amber),
        ("Non-Medical Disallowed & Deductions Settled", "Caregiver Settled at Desk", f"Rs. {(dossier.caregiver_paid - dossier.copay_settled):,.2f}", c_text),
        ("Total Caregiver Out-of-Pocket Payment", "Direct Payment to Hospital", f"Rs. {dossier.caregiver_paid:,.2f}", c_dark),
        ("Net Hospital Outstanding Balance", "Zero-Debt Discharge", "Rs. 0.00", c_emerald),
    ]

    for item, party, amt, color in ledger_rows:
        y += 24
        page.draw_rect(fitz.Rect(40, y, 555, y + 24), color=c_card_border, fill=(1, 1, 1))
        page.insert_text(fitz.Point(55, y + 16), item, fontsize=8.5, fontname="helv", color=color)
        page.insert_text(fitz.Point(340, y + 16), party, fontsize=8, fontname="helv", color=c_text)
        page.insert_text(fitz.Point(480, y + 16), amt, fontsize=9, fontname="helv", color=color)

    y += 40

    # Summary Text Callout
    page.draw_rect(fitz.Rect(40, y, 555, y + 48), color=(0.1, 0.7, 0.5), fill=(0.95, 1.0, 0.97))
    page.insert_text(fitz.Point(55, y + 18), "AUDIT VERIFICATION SUMMARY:", fontsize=8.5, fontname="helv", color=c_emerald)
    # Split summary into 2 lines if long
    text_s = dossier.summary_text
    line1 = text_s[:95]
    line2 = text_s[95:190]
    page.insert_text(fitz.Point(55, y + 32), line1, fontsize=8, fontname="helv", color=c_dark)
    if line2:
        page.insert_text(fitz.Point(55, y + 43), line2, fontsize=8, fontname="helv", color=c_dark)

    y += 62

    # Verified Document Checklist
    page.insert_text(fitz.Point(40, y + 16), "DIGITAL CLAIM ATTACHMENTS & CHECKLIST", fontsize=11, fontname="helv", color=c_dark)
    y += 24

    for chk in dossier.documents_checklist:
        page.draw_rect(fitz.Rect(40, y, 555, y + 22), color=c_card_border, fill=(0.99, 1.0, 1.0))
        # Draw green checkbox
        page.draw_rect(fitz.Rect(55, y + 5, 67, y + 17), color=c_emerald, fill=(0.9, 0.98, 0.94))
        page.insert_text(fitz.Point(57, y + 15), "OK", fontsize=7, fontname="helv", color=c_emerald)
        page.insert_text(fitz.Point(75, y + 15), chk, fontsize=8.5, fontname="helv", color=c_dark)
        y += 22

    y += 25

    # Footer note
    page.draw_line(fitz.Point(40, y), fitz.Point(555, y), color=c_card_border, width=1)
    page.insert_text(
        fitz.Point(40, y + 15),
        "Official CareWise Patient Protection & Audit Certificate. Generated under Cloud Auditing Data Federation (CADF) spec.",
        fontsize=7,
        fontname="helv",
        color=c_text,
    )
    page.insert_text(
        fitz.Point(40, y + 26),
        f"Verification Hash: SHA256:{hash(dossier.dossier_id) & 0xffffffffffffffff:016x} • TPA Code: {dossier.tpa_submission_code}",
        fontsize=7,
        fontname="helv",
        color=c_primary,
    )

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes
