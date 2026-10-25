import io
from decimal import Decimal

from openpyxl import Workbook
from reportlab.pdfgen.canvas import Canvas

from backend.ingest import ingest_bytes


def test_csv_typed_records_have_line_provenance():
    content=b"record_type,id,number,date,amount,delivery_date,contract_date,written_term_days\ninvoice,I1,I1,2026-01-01,100000,2026-01-02,2025-12-01,30\n"
    sources,records,errors=ingest_bytes("ledger.csv",content)
    assert not errors
    invoice=records["invoices"][0]
    assert invoice.amount==Decimal(100000)
    assert invoice.field_sources["amount"]==[sources[1].id]
    assert sources[1].line==2


def test_xlsx_payment_extracts_without_date_guessing():
    book=Workbook()
    sheet=book.active
    sheet.append(["record_type","id","date","amount","reference"])
    sheet.append(["payment","P1","2026-01-31",5000,"I1"])
    output=io.BytesIO()
    book.save(output)
    sources,records,errors=ingest_bytes("bank.xlsx",output.getvalue())
    assert not errors and records["payments"][0].amount==5000
    assert sources[1].line==2


def test_ambiguous_date_is_parse_error_not_guess():
    sources,records,errors=ingest_bytes("bank.csv",b"record_type,id,date,amount\npayment,P1,01/02/2026,1000\n")
    assert errors and sources[1].status=="parse_error"
    assert not records


def test_searchable_pdf_preserves_page_text_pending_review():
    output=io.BytesIO()
    canvas=Canvas(output)
    canvas.drawString(30,700,"Invoice I1 amount INR100000 delivered2026-01-02")
    canvas.save()
    sources,records,errors=ingest_bytes("invoice.pdf",output.getvalue())
    assert sources[1].page==1 and "100000" in sources[1].text
    assert sources[1].status=="unstructured_review"
    assert not records


def test_image_flags_missing_ocr_never_invents_date():
    sources,records,errors=ingest_bytes("challan.jpg",b"scan")
    assert sources[0].status=="ocr_unavailable" and not records


def test_whatsapp_text_preserves_line_provenance_without_acceptance_guess():
    sources,records,errors=ingest_bytes("whatsapp.txt",b"01/02/2026 Buyer: Payment soon\nOwner: Thank you\n")
    assert len(records["messages"])==2
    assert records["messages"][0].field_sources["text"]==[sources[1].id]
    assert "invoices" not in records
