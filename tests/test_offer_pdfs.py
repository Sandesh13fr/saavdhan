"""Exercise committed synthetic PDFs through local ingestion and deterministic analysis."""
import asyncio
import hashlib
import runpy
from pathlib import Path

import pytest
from pypdf import PdfReader

from backend import agent, ingest

DIRECTORY = Path(__file__).parent / "fixtures/offers"
LABEL = "TEST FIXTURE - invented data for software testing - not a real offer"
CASES = {
    "bangkok_data_entry_offer.pdf": ("STOP", {
        "R1_TOURIST_VISA", "R3_NO_RC_NUMBER", "R4_FEE_OVER_CAP", "R6_HIGH_RISK_CORRIDOR",
        "R7_INFORMAL_CHANNEL_ONLY", "R8_NO_RECEIPT", "H2_PASSPORT_HANDOVER", "H3_PRESSURE",
    }, set()),
    "dubai_electrician_offer.pdf": ("VERIFY_FIRST", {"R4_FEE_OVER_CAP"}, {
        "R1_TOURIST_VISA", "R6_HIGH_RISK_CORRIDOR", "R3_NO_RC_NUMBER",
    }),
    "cambodia_customer_support_scan.pdf": ("STOP", {"R1_TOURIST_VISA", "R6_HIGH_RISK_CORRIDOR"}, set()),
    "laos_it_offer_hindi.pdf": ("STOP", {"R1_TOURIST_VISA", "R4_FEE_OVER_CAP", "R6_HIGH_RISK_CORRIDOR"}, set()),
    "saudi_driver_offer_marathi.pdf": ("VERIFY_FIRST", set(), {"R1_TOURIST_VISA", "R4_FEE_OVER_CAP"}),
}


def fixture_path(name):
    path = DIRECTORY / name
    if not path.exists() and name.endswith(("_hindi.pdf", "_marathi.pdf")):
        generator = runpy.run_path(str(DIRECTORY / "make_offer_pdfs.py"))
        assert generator["devanagari_font"]() is None, f"Run the generator to create {name}"
        pytest.skip("Devanagari PDF omitted: no TTF in the specified font locations")
    assert path.is_file(), f"Missing committed fixture: {name}"
    return path


@pytest.mark.parametrize("name", CASES)
def test_pdf_structure_and_labelling(name):
    path = fixture_path(name)
    assert b"\0" in path.read_bytes()[:8000], "PDF must remain binary for Git line-ending detection"
    reader = PdfReader(path)
    assert len(reader.pages) == (2 if name == "dubai_electrician_offer.pdf" else 1)
    assert reader.metadata.title == LABEL
    assert reader.metadata.creation_date.year == reader.metadata.modification_date.year == 2000
    for page in reader.pages:
        text = page.extract_text() or ""
        if name.endswith("_scan.pdf"):
            assert not text.strip(), "Scan must have no text layer, including its footer"
            assert len(page.images) == 1
        else:
            assert LABEL in text
            assert "(Test)" in text


@pytest.fixture(scope="module")
def analyze_pdf():
    results = {}
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("SAAVDHAN_ENABLE_LLM", "false")
        patch.setenv("OPENAI_API_KEY", "")
        patch.setenv("LITELLM_API_KEY", "")
        patch.setenv("SAAVDHAN_OCR_ENABLED", "true")
        patch.setenv("SAAVDHAN_OCR_LANGS", "eng")
        patch.setattr(agent, "RA_LIST_DATE", "not loaded")

        def run(name):
            path = fixture_path(name)
            if name.endswith("_scan.pdf") and not ingest.tesseract_command():
                pytest.skip("Tesseract is missing; scanned offer requires local OCR")
            if name not in results:
                data = path.read_bytes()
                sources, errors = ingest.ingest_bytes(name, data)
                assert not errors
                assert len(sources) == len(PdfReader(path).pages) + 1
                for number, source in enumerate(sources[1:], 1):
                    assert source.page == number
                    assert source.sha256 == hashlib.sha256(data).hexdigest()
                    assert source.id == f"{sources[0].id}-P{number}"
                    assert LABEL in source.text, "Footer must be readable on every page, including the scan"
                    if name.endswith("_scan.pdf"):
                        assert source.kind == "ocr_document"
                result = asyncio.run(agent.analyze({"sources": [source.model_dump() for source in sources]}))
                assert result["extraction_method"] == "fallback"
                assert not result["errors"]
                by_id = {source.id: source for source in sources}
                for field_name, value in result["offer"].items():
                    if field_name == "source_ids":
                        continue
                    for field in value if isinstance(value, list) else [value]:
                        if field["value"] is not None:
                            assert field["quote"] in by_id[field["source_ref"]].text
                            assert by_id[field["source_ref"]].page is not None
                results[name] = result
            return results[name]

        yield run


@pytest.mark.parametrize("name", CASES)
def test_offer_verdict(name, analyze_pdf):
    verdict = analyze_pdf(name)["verdict"]
    assert verdict["level"] == CASES[name][0]
    assert verdict["ra_list_date"] == "not loaded"
    assert next(hit for hit in verdict["rule_hits"] if hit["rule_id"] == "R2_RA_NOT_LISTED")["status"] == "unknown"


@pytest.mark.parametrize("name", CASES)
def test_offer_rule_hits(name, analyze_pdf):
    hits = {hit["rule_id"] for hit in analyze_pdf(name)["verdict"]["rule_hits"] if hit["status"] == "hit"}
    _, required, forbidden = CASES[name]
    if name == "bangkok_data_entry_offer.pdf":
        # The correspondence-address conflict is isolated in the strict xfail below.
        required = required - {"R7_INFORMAL_CHANNEL_ONLY"}
    assert not forbidden & hits
    assert required <= hits, f"Missing rule hits: {required - hits}; actual hits: {hits}"
    if name == "saudi_driver_offer_marathi.pdf":
        assert not hits, "Only the unloaded recruiter list should require verification"


@pytest.mark.xfail(strict=True, reason=(
    "R7 treats the printed Pune correspondence address as office_address, so it clears "
    "the rule despite the offer's explicit WhatsApp-only contact restriction"
))
def test_bangkok_whatsapp_only_contact(analyze_pdf):
    hits = analyze_pdf("bangkok_data_entry_offer.pdf")["verdict"]["rule_hits"]
    assert next(hit for hit in hits if hit["rule_id"] == "R7_INFORMAL_CHANNEL_ONLY")["status"] == "hit"


def test_generator_is_deterministic(tmp_path):
    generator = runpy.run_path(str(DIRECTORY / "make_offer_pdfs.py"))
    generate = generator["generate"]
    first, second = tmp_path / "first", tmp_path / "second"
    generate(first)
    generate(second)
    names = {path.name for path in first.glob("*.pdf")}
    expected = set(CASES)
    if generator["devanagari_font"]() is None:
        expected -= set(generator["DEVANAGARI_FILES"])
    assert names == expected
    assert names == {path.name for path in second.glob("*.pdf")}
    for name in names:
        assert (first / name).read_bytes() == (second / name).read_bytes()
        assert (first / name).read_bytes() == fixture_path(name).read_bytes()
