import io
import shutil
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont
from backend.ingest import ingest_bytes, ocr_available


def synthetic_scan():
    image = Image.new("RGB", (1600, 500), "white")
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    font = ImageFont.truetype(str(font_path) if font_path.exists() else "DejaVuSans.ttf", 48)
    ImageDraw.Draw(image).multiline_text((60, 60), "SYNTHETIC INVOICE\nInvoice TEST-123\nAmount INR 10000\nDate 2026-10-11", fill="black", font=font, spacing=20)
    return image


def test_disabled_ocr_preserves_blocker(monkeypatch):
    monkeypatch.setenv("BAKAYA_OCR_ENABLED", "false")
    assert not ocr_available()
    sources, records, errors = ingest_bytes("scan.png", b"invalid")
    assert sources[0].status == "ocr_unavailable" and not records and not errors


def test_actual_synthetic_image_and_pdf_ocr(monkeypatch):
    executable = shutil.which("tesseract") or "C:/Program Files/Tesseract-OCR/tesseract.exe"
    if not Path(executable).exists():
        pytest.skip("Tesseract is not installed; production Docker image supplies it")
    monkeypatch.setenv("BAKAYA_OCR_ENABLED", "true")
    monkeypatch.setenv("TESSERACT_CMD", executable)
    for suffix, format in [("png", "PNG"), ("pdf", "PDF")]:
        output = io.BytesIO()
        synthetic_scan().save(output, format=format)
        sources, records, errors = ingest_bytes("synthetic." + suffix, output.getvalue())
        source = sources[1] if suffix == "pdf" else sources[0]
        assert not records and not errors
        assert source.status == "unstructured_review" and source.kind == "ocr_document"
        assert "10000" in source.text and "TEST-123" in source.text
        assert source.sha256 and (source.page == 1 if suffix == "pdf" else True)


def test_invalid_ocr_image_fails_closed(monkeypatch):
    monkeypatch.setenv("BAKAYA_OCR_ENABLED", "true")
    monkeypatch.setenv("TESSERACT_CMD", shutil.which("python") or "C:/Program Files/Tesseract-OCR/tesseract.exe")
    sources, records, errors = ingest_bytes("scan.png", b"invalid")
    assert sources[0].status == "ocr_unavailable" and not records and errors


def test_configured_missing_executable_reports_unavailable(monkeypatch):
    monkeypatch.setenv("BAKAYA_OCR_ENABLED", "true")
    monkeypatch.setenv("TESSERACT_CMD", "not-installed")
    assert not ocr_available()
    sources, records, errors = ingest_bytes("scan.png", b"invalid")
    assert sources[0].status == "ocr_unavailable" and not records and not errors
