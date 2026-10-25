import io

import pytest
from reportlab.pdfgen.canvas import Canvas

from backend.ingest import ingest_bytes


def test_searchable_pdf_preserves_page_text():
    output = io.BytesIO()
    canvas = Canvas(output)
    canvas.drawString(30, 700, "Offer: Data entry, Bangkok. Fee Rs 250000")
    canvas.save()
    sources, errors = ingest_bytes("offer.pdf", output.getvalue())
    assert sources[1].page == 1 and "250000" in sources[1].text
    assert sources[1].status == "unstructured_review"


def test_image_without_ocr_infers_nothing():
    sources, errors = ingest_bytes("offer.jpg", b"scan")
    assert sources[0].status == "ocr_unavailable" and "Nothing was inferred" in sources[0].text


def test_whatsapp_text_preserves_line_provenance():
    sources, errors = ingest_bytes("chat.txt", "Recruiter: नौकरी Bangkok\n\nफीस 2.5 लाख\n".encode("utf-8"))
    assert [s.line for s in sources[1:]] == [1, 3]
    assert "लाख" in sources[2].text and sources[0].sha256


def test_spreadsheets_are_rejected():
    for name in ("rows.csv", "rows.xlsx"):
        with pytest.raises(ValueError, match="Unsupported"):
            ingest_bytes(name, b"a,b")
