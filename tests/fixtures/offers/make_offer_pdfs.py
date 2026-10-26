"""Generate labelled, invented offer PDFs locally; no network or model calls."""
from __future__ import annotations

import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab import rl_config
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[3]
LABEL = "TEST FIXTURE - invented data for software testing - not a real offer"
DEVANAGARI_FILES = ("laos_it_offer_hindi.pdf", "saudi_driver_offer_marathi.pdf")


def devanagari_font():
    candidates = sorted((ROOT / "frontend/node_modules/@fontsource-variable/noto-sans-devanagari/files").glob("*.ttf"))
    candidates += [Path("C:/Windows/Fonts/Nirmala.ttf"), Path("C:/Windows/Fonts/Mangal.ttf")]
    return next((path for path in candidates if path.is_file()), None)


def pdf(path):
    # Binary Flate streams prevent Git from converting PDF bytes to Windows line endings.
    rl_config.useA85 = False
    # invariant fixes the PDF dates and document ID (ReportLab's 2000-01-01 epoch).
    document = canvas.Canvas(str(path), pagesize=A4, invariant=1, pageCompression=1)
    document.setTitle(LABEL)
    document.setAuthor("Invented software test fixtures")
    document.setSubject("Synthetic offer evidence; not valid for employment or travel")
    return document


def letter(path, heading, pages, font="Helvetica"):
    document = pdf(path)
    width, height = A4
    for number, lines in enumerate(pages, 1):
        document.setFillColorRGB(0.12, 0.2, 0.3)
        document.setFont("Helvetica-Bold", 15)
        document.drawString(42, height - 52, heading)
        document.setFont("Helvetica", 9)
        document.drawString(42, height - 72, f"SYNTHETIC OFFER | 12 October 2026 | Page {number} of {len(pages)}")
        document.line(42, height - 85, width - 42, height - 85)
        document.setFillColorRGB(0, 0, 0)
        document.setFont(font, 11)
        y = height - 115
        for line in lines:
            for part in simpleSplit(line, font, 11, width - 84):
                assert y > 70, "Offer text would overlap the mandatory footer"
                document.drawString(42, y, part)
                y -= 19
            y -= 8
        document.setFont("Helvetica", 8)
        document.drawCentredString(width / 2, 28, LABEL)
        document.showPage()
    document.save()


def scanned_offer(path):
    image = Image.new("RGB", (1800, 2400), (249, 249, 249))
    draw = ImageDraw.Draw(image)
    # Fixed grid and shades provide light scan noise without random state.
    for y in range(0, image.height, 17):
        for x in range(0, image.width, 19):
            grey = 235 + (x * 7 + y * 3) % 15
            draw.point((x, y), fill=(grey, grey, grey))
    font = ImageFont.load_default(size=43)
    lines = [
        "Fixture Customer Placements (Test)",
        "SYNTHETIC OFFER - 12 October 2026",
        "Reference: TEST-CAMBODIA-003",
        "Employer: Example Support Ltd (Test)",
        "Customer support executive",
        "Phnom Penh, Cambodia",
        "Visit visa arranged before departure.",
        "Deposit Rs 1,80,000 in cash.",
        "Telegram contact only: +91 90000 00003",
        "Please confirm today.",
        "Issued by Fable Recruiter (Test), HR Manager",
    ]
    draw.multiline_text((130, 180), "\n\n".join(lines), font=font, fill=(25, 25, 25), spacing=16)
    image = image.rotate(0.35, resample=Image.Resampling.BICUBIC, fillcolor="white")
    draw = ImageDraw.Draw(image)
    draw.text((100, 2290), LABEL, font=ImageFont.load_default(size=25), fill="black")
    output = io.BytesIO()
    image.save(output, format="PNG")
    document = pdf(path)
    document.drawImage(ImageReader(io.BytesIO(output.getvalue())), 0, 0, width=A4[0], height=A4[1])
    document.showPage()
    document.save()
    image.close()


def generate(directory=Path(__file__).resolve().parent):
    directory.mkdir(parents=True, exist_ok=True)
    letter(directory / "bangkok_data_entry_offer.pdf", "Fixture Overseas Placements (Test)", [[
        "Correspondence address: 17 Fixture Lane, Sample Quarter, Pune, Maharashtra 000000 (invented).",
        "Reference: TEST-BANGKOK-001",
        "Employer: Example Data Ltd (Test)",
        "Position: Data entry operator. Destination: Bangkok, Thailand.",
        "Salary: THB 35,000 per month.",
        "Processing and visa charges: Rs 2,50,000 payable by UPI before departure.",
        "Tourist visa arranged. Work permit after arrival.",
        "Transit via Bangkok to a partner office near Mae Sot.",
        "Passport to be submitted to the agent for processing.",
        "Joining within 7 days; limited seats.",
        "WhatsApp-only contact: +91 90000 00001",
        "Signed: Fable Coordinator (Test), HR Manager (typed test signature)",
    ]])
    letter(directory / "dubai_electrician_offer.pdf", "Example Facilities Ltd (Test)", [[
        "Reference: TEST-DUBAI-002",
        "Employer location: 28 Fixture Lane, Example Quarter, Dubai, United Arab Emirates (invented).",
        "Issued through Fixture Gulf Placements (Test).",
        "RC number: B-1234/TEST/PER/1000+/5/4321/2026",
        "Office address: 42 Fixture Road, Example Quarter, Mumbai, Maharashtra 000000 (invented).",
        "Email: fixture.gulf@example.org; contact: +91 90000 00002",
        "Position: Electrician. Destination: Dubai, United Arab Emirates.",
        "Employment visa. Salary: AED 2,200 per month plus accommodation.",
        "Service charge: Rs 45,000 + GST with a written receipt.",
        "Terms continue on page 2.",
    ], [
        "Reference: TEST-DUBAI-002 - employment terms",
        "Employment contract signed by employer, recruiting agent and worker before departure.",
        "Pravasi Bharatiya Bima Yojana (PBBY) insurance included in the offer terms.",
        "Passport stays with the worker. Do not hand over the original passport to the agent.",
        "Employer signatory: Fable Employer (Test) - typed test signature.",
        "Agent signatory: Fable Agent (Test) - typed test signature.",
        "Worker signatory: Fable Worker (Test) - typed test signature.",
        "Issued by Fable Supervisor (Test), HR Manager.",
    ]])
    scanned_offer(directory / "cambodia_customer_support_scan.pdf")
    font = devanagari_font()
    if font is None:
        for name in DEVANAGARI_FILES:
            print(f"SKIPPED {name}: no Devanagari TTF in the specified locations")
        return
    pdfmetrics.registerFont(TTFont("FixtureDevanagari", str(font)))
    letter(directory / DEVANAGARI_FILES[0], "Fixture Laos Placements (Test)", [[
        "संदर्भ: TEST-LAOS-004",
        "एजेंसी: Fixture Laos Placements (Test)",
        "नियोक्ता: Example Support Ltd (Test)",
        "आईटी सपोर्ट की नौकरी, लाओस।",
        "टूरिस्ट वीज़ा।",
        "फीस अढ़ाई लाख रुपये UPI से।",
        "रसीद नहीं। आज ही कन्फर्म करें।",
        "WhatsApp: +91 90000 00004",
    ]], "FixtureDevanagari")
    letter(directory / DEVANAGARI_FILES[1], "Fixture Driver Placements (Test)", [[
        "संदर्भ: TEST-SAUDI-005",
        "एजंट: Fixture Driver Placements (Test)",
        "RC number: B-5678/TEST/PER/1000+/5/8765/2026",
        "पत्ता: 63 Fixture Lane, Sample Quarter, Nashik, Maharashtra 000000 (invented).",
        "नियोक्ता: Example Transport Ltd (Test)",
        "चालक, रियाध, सौदी अरेबिया। रोजगार व्हिसा।",
        "पगार SAR 1,800 दरमहा।",
        "सेवा शुल्क ₹25,000 + GST, पावती दिली जाईल।",
        "नियोक्ता, एजंट आणि कामगार यांनी सही केलेला करार।",
        "PBBY विमा। पासपोर्ट कामगाराकडे राहील।",
        "fixture.driver@example.org; +91 90000 00005",
    ]], "FixtureDevanagari")


if __name__ == "__main__":
    generate()
