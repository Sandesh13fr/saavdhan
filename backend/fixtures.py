"""Explicitly fictional records; no private bank/customer data."""
from datetime import date
from decimal import Decimal

from .models import CaseInput, Invoice, Payment, SourceRef, Supplier, Buyer, RatePeriod, Allocation


def ref(sid, file, text, kind="document"):
    return SourceRef(id=sid, file=file, kind=kind, line=1, text=text)


def sourced(model, sid, **kwargs):
    return model(source_refs=[sid], field_sources={key: [sid] for key in kwargs}, **kwargs)


def demo_case() -> CaseInput:
    sources = [ref("UDYAM", "synthetic-udyam.txt", "FICTIONAL: Sahyadri Precision Works, small, manufacturing, UDYAM-DEMO-0001; registered2023-01-01"),
               ref("BUYER", "synthetic-buyer.txt", "FICTIONAL: Deccan Industrial Systems Pvt Ltd, Pune, Maharashtra"),
               ref("RATES", "synthetic-rates.csv", "DEMO RATES ONLY:2024-01-01 to2026-07-01 bank rate6.50%;2026-07-01 to2027-01-01 bank rate5.75%", "rate_table"),
               ref("BANK", "synthetic-bank.csv", "PAY-001 2026-07-15 INR98000 INV-001; PAY-002 2026-08-01 INR80000 INV-002; PAY-003 2026-08-15 INR150000 no invoice reference; control total INR328000", "bank_statement"),
               ref("TDS-001", "synthetic-tds-certificate.txt", "FICTIONAL TDS certificate: INV-001 gross100000, TDS2000 under194C, net98000, credited2026-07-15", "tds_certificate"),
               ref("REMIT-003", "synthetic-remittance-note.txt", "Buyer remittance confirmation: PAY-003 of INR150000 on2026-08-15 is allocated to INV-004. Owner must confirm this linkage.", "remittance_note")]
    invoices = []
    for n, amount in enumerate([100000,240000,150000,150000,160000],1):
        sid, iid = f"DOC-{n:03}", f"INV-{n:03}"
        sources.append(ref(sid, f"synthetic-invoice-{n:03}.txt", f"{iid}; invoice2026-05-01 amount INR{amount}; PO2026-04-20 terms30days; delivery accepted2026-05-03", "invoice"))
        invoices.append(sourced(Invoice,sid,id=iid,number=iid,date=date(2026,5,1),amount=Decimal(amount),contract_date=date(2026,4,20),delivery_date=date(2026,5,3),written_term_days=30))
    payments = [sourced(Payment,"BANK",id="PAY-001",date=date(2026,7,15),amount=Decimal(98000),reference="INV-001",invoice_ids=["INV-001"],tds_amount=Decimal(2000),tds_evidence_source="TDS-001",tds_section="194C"),
                sourced(Payment,"BANK",id="PAY-002",date=date(2026,8,1),amount=Decimal(80000),reference="INV-002",invoice_ids=["INV-002"]),
                sourced(Payment,"BANK",id="PAY-003",date=date(2026,8,15),amount=Decimal(150000),reference="NEFT-BUYER-NO-INVOICE")]
    return CaseInput(name="Sahyadri · Deccan Industrial",as_of=date(2026,10,10),supplier=sourced(Supplier,"UDYAM",name="Sahyadri Precision Works",category="small",activity="manufacturing",udyam_number="UDYAM-DEMO-0001",udyam_date=date(2023,1,1),address="Pune, Maharashtra · fictional"),buyer=sourced(Buyer,"BUYER",name="Deccan Industrial Systems Pvt Ltd",address="Pune, Maharashtra · fictional"),invoices=invoices,payments=payments,sources=sources,bank_total=Decimal(328000),rates=[sourced(RatePeriod,"RATES",start=date(2024,1,1),end=date(2026,7,1),bank_rate=Decimal("6.50"),source="synthetic-rates.csv (fictional, not RBI)",synthetic=True),sourced(RatePeriod,"RATES",start=date(2026,7,1),end=date(2027,1,1),bank_rate=Decimal("5.75"),source="synthetic-rates.csv (fictional, not RBI)",synthetic=True)])


def evaluation_cases():
    """20 labeled scenarios. Ground truth matching/dates is separate from matcher.

    Interest numerical truth uses independent day-by-day Decimal accrual in
    evaluation.py, and is corroborated by hand-closed-form unit tests.
    """
    cases = []
    kinds = ["clean"]*3 + ["tds"]*4 + ["lump"]*3 + ["partial"]*3 + ["ambiguous"]*2 + ["objection"]*2 + ["post_registration","trader","rate_change"]
    for n, kind in enumerate(kinds,1):
        case = demo_case()
        case.name = f"EVAL-{n:02} {kind}"
        case.as_of = date(2026,9,10)
        invoice = case.invoices[0].model_copy(deep=True)
        invoice.amount = Decimal(100000)
        invoice.date, invoice.delivery_date, invoice.contract_date = date(2026,6,1),date(2026,6,1),date(2026,5,1)
        invoice.written_term_days = 0
        case.invoices = [invoice]
        case.payments = [sourced(Payment,"BANK",id="P1",date=date(2026,8,1),amount=Decimal(100000),invoice_ids=[invoice.id],reference=invoice.id)]
        expected = [("P1",invoice.id,"100000.00","0.00")]
        expected_due = {invoice.id:"2026-06-01"}
        expected_block = None
        if kind == "tds":
            p=case.payments[0]
            p.amount,p.tds_amount,p.tds_evidence_source,p.tds_section=Decimal(98000),Decimal(2000),"TDS-001","194C"
            expected=[("P1",invoice.id,"98000.00","2000.00")]
        if kind in {"lump","ambiguous"}:
            other = invoice.model_copy(deep=True)
            other.id,other.number="INV-002","INV-002"
            case.invoices.append(other)
            expected_due[other.id]="2026-06-01"
            case.payments[0].invoice_ids=[]
            case.payments[0].reference="Buyer transfer"
            if kind == "lump":
                case.payments[0].amount=Decimal(200000)
                case.payments[0].allocations=[sourced(Allocation,"BANK",invoice_id=i.id,amount=Decimal(100000)) for i in case.invoices]
                expected=[("P1",i.id,"100000.00","0.00") for i in case.invoices]
            else:
                expected=[]
                expected_block="ambiguous_payment"
        if kind == "partial":
            case.payments=[sourced(Payment,"BANK",id="P1",date=date(2026,7,1),amount=Decimal(30000),invoice_ids=[invoice.id]),sourced(Payment,"BANK",id="P2",date=date(2026,8,1),amount=Decimal(20000),invoice_ids=[invoice.id])]
            expected=[("P1",invoice.id,"30000.00","0.00"),("P2",invoice.id,"20000.00","0.00")]
        if kind == "objection":
            invoice.objection_date,invoice.objection_resolved_date=date(2026,6,10),date(2026,6,20)
            invoice.field_sources.update(objection_date=["DOC-001"],objection_resolved_date=["DOC-001"])
            expected_due[invoice.id]="2026-06-20"
        if kind == "post_registration":
            case.supplier.udyam_date=date(2026,7,1)
            expected_block="registration_review"
        if kind == "trader":
            case.supplier.activity="trading"
            expected_block="ineligible"
        if kind != "rate_change":
            case.rates=[sourced(RatePeriod,"RATES",start=date(2024,1,1),end=date(2027,1,1),bank_rate=Decimal("6.5"),source="Synthetic6.5%",synthetic=True)]
        case.bank_total=sum((p.amount for p in case.payments),Decimal(0))
        # Evidence snapshots reflect each fictional case rather than the demo.
        for source in case.sources:
            linked=[i for i in case.invoices if source.id in i.source_refs]
            if linked:
                source.text="FICTIONAL invoice/PO/delivery facts: "+"; ".join(i.model_dump_json() for i in linked)
            if source.id=="BANK":
                source.text="FICTIONAL bank entries: "+"; ".join(p.model_dump_json() for p in case.payments)+f"; control total {case.bank_total}"
            if source.id=="TDS-001":
                source.text="FICTIONAL certificate INV-001: TDS2000 under194C; net98000; credited2026-08-01"
            if source.id=="UDYAM":
                source.text="FICTIONAL supplier facts: "+case.supplier.model_dump_json()
            if source.id=="RATES":
                source.text="FICTIONAL rates: "+"; ".join(r.model_dump_json() for r in case.rates)
        cases.append({"id":f"EVAL-{n:02}","kind":kind,"input":case,"expected_matches":expected,"expected_due":expected_due,"expected_block":expected_block})
    return cases
