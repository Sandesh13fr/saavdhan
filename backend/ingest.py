"""Local ingestion of offer evidence (text, PDF, images). Text is data, never instructions."""
from __future__ import annotations

import hashlib
import io
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from PIL import Image

from .models import SourceRef

MAX_FILE_BYTES = 15 * 1024 * 1024
MAX_LINE_SOURCES = 500
ALLOWED = {".pdf", ".txt", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}


def tesseract_command():
    if os.getenv("SAAVDHAN_OCR_ENABLED", "false").lower() != "true":
        return None
    configured = os.getenv("TESSERACT_CMD")
    executable = shutil.which(configured or "tesseract")
    if not executable and Path("C:/Program Files/Tesseract-OCR/tesseract.exe").is_file():
        executable = None if configured else "C:/Program Files/Tesseract-OCR/tesseract.exe"
    return executable


def ocr_available():
    return bool(tesseract_command())


def ocr_image(data: bytes) -> str:
    """Local, opt-in OCR produces reviewable text only."""
    executable = tesseract_command()
    if not executable:
        return ""
    with Image.open(io.BytesIO(data)) as image:
        if getattr(image, "n_frames", 1) != 1:
            raise ValueError("Multi-frame images require a page-preserving PDF upload")
        if image.width * image.height > 20_000_000:
            raise ValueError("OCR image exceeds 20 million pixels")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "page.png"
            image.convert("RGB").save(path)
            result = subprocess.run([executable, str(path), "stdout", "-l", os.getenv("SAAVDHAN_OCR_LANGS", "eng"), "--psm", "6"],
                                    capture_output=True, timeout=60, check=True)
    return result.stdout.decode("utf-8").strip()



def ingest_bytes(filename: str, data: bytes):
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED:
        raise ValueError(f"Unsupported extension {suffix}; accepted: PDF, TXT, images")
    if len(data)>MAX_FILE_BYTES:
        raise ValueError("File exceeds15 MB limit")
    root = "SRC-"+uuid.uuid4().hex[:12]
    base = SourceRef(id=root,file=Path(filename).name,kind="uploaded_document",sha256=hashlib.sha256(data).hexdigest(),stored_name=root+suffix)
    sources, errors = [base], []

    def checked_text(text):
        if len(text) > 100000:
            note = "Only the first 100,000 characters were checked."
            if note not in errors:
                errors.append(note)
            base.status = "truncated"
        return text[:100000]

    if suffix in {".png",".jpg",".jpeg",".webp",".tif",".tiff"}:
        base.status="ocr_unavailable"
        base.text="OCR is not configured. Paste the offer text instead. Nothing was inferred from this image."
        try:
            text = ocr_image(data)
            if text:
                base.status = "unstructured_review"
                base.text = checked_text(text)
                base.kind = "ocr_document"
        except Exception as exc:  # best-effort OCR: record the cause, never invent text
            errors.append(f"OCR failed ({type(exc).__name__}) or exceeded its limit; paste the offer text instead.")
        return sources,errors
    if suffix == ".pdf":
        from pypdf import PdfReader
        reader=PdfReader(io.BytesIO(data))
        if len(reader.pages) > 50:
            raise ValueError("PDF exceeds 50 page limit")
        pages=[]
        for n,page in enumerate(reader.pages,1):
            text=page.extract_text() or ""
            if not text.strip() and os.getenv("SAAVDHAN_OCR_ENABLED", "false").lower() == "true":
                try:
                    import pypdfium2 as pdfium
                    with pdfium.PdfDocument(data) as document:
                        scan = document[n-1]
                        try:
                            if scan.get_width() * scan.get_height() * 9 > 20_000_000:
                                raise ValueError("OCR page exceeds pixel limit")
                            bitmap = scan.render(scale=3)
                            image = bitmap.to_pil()
                            output = io.BytesIO()
                            image.save(output, format="PNG")
                            text = ocr_image(output.getvalue())
                            image.close()
                            bitmap.close()
                        finally:
                            scan.close()
                except Exception as exc:  # best-effort OCR: record the cause, never invent text
                    errors.append(f"Page {n}: OCR failed ({type(exc).__name__}); manual evidence review required.")
            sid=f"{root}-P{n}"
            source=base.model_copy(update={"id":sid,"page":n,"text":checked_text(text),"stored_name":base.stored_name})
            source.status="truncated" if len(text)>100000 else "unstructured_review" if text.strip() else "ocr_unavailable"
            if text.strip() and not (page.extract_text() or "").strip():
                source.kind = "ocr_document"
            sources.append(source)
            pages.append(text)
        base.text=checked_text("\n".join(pages))
        if base.status != "truncated":
            base.status="parsed" if base.text.strip() else "ocr_unavailable"
        return sources,errors
    text=data.decode("utf-8-sig")
    base.text=checked_text(text)
    base.kind="message_export"
    for n,line in enumerate(base.text.splitlines(),1):
        if len(sources)>MAX_LINE_SOURCES:
            errors.append(f"Only the first {MAX_LINE_SOURCES} lines were checked.")
            base.status="truncated"
            break
        if line.strip():
            sources.append(base.model_copy(update={"id":f"{root}-L{n}","line":n,"text":line}))
    return sources,errors
