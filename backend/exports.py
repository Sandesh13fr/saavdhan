from __future__ import annotations

import csv
import io
import json
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from .engine import CONVENTION, RULES_SOURCE
from .storage import upload_dir


def csv_bytes(rows, keys):
    output=io.StringIO(newline="")
    writer=csv.DictWriter(output,fieldnames=keys,extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        safe={key:json.dumps(row[key]) if isinstance(row.get(key),(list,dict)) else row.get(key,"") for key in keys}
        # Prevent a source filename/reference being interpreted as a spreadsheet formula.
        for key,value in safe.items():
            if isinstance(value,str) and value.startswith(("=","+","-","@")):
                safe[key]="'"+value
        writer.writerow(safe)
    return output.getvalue().encode("utf-8-sig")


def pdf_bytes(title, paragraphs, rows=None, col_widths=None):
    output=io.BytesIO()
    doc=SimpleDocTemplate(output,pagesize=(8.27*inch,11.69*inch),rightMargin=40,leftMargin=40,topMargin=40,bottomMargin=40)
    styles=getSampleStyleSheet()
    styles["BodyText"].fontSize=8.5
    styles["BodyText"].leading=11
    flow=[Paragraph(escape(title),styles["Title"]),Spacer(1,14)]
    for text in paragraphs:
        flow.extend([Paragraph(escape(text).replace("\n","<br/>"),styles["BodyText"]),Spacer(1,9)])
    if rows:
        wrapped=[[Paragraph(escape(str(cell)),styles["BodyText"]) for cell in row] for row in rows]
        table=Table(wrapped,repeatRows=1,colWidths=col_widths)
        table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e5ece4")),("GRID",(0,0),(-1,-1),.3,colors.grey),("VALIGN",(0,0),(-1,-1),"TOP"),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
        flow.append(table)
    doc.build(flow)
    return output.getvalue()


def packet_zip(view: dict, state: dict):
    demo=any(r["synthetic"] for r in state["input"]["rates"])
    label="SYNTHETIC DEMO - NOT FOR FILING" if demo else "REVIEWED PREPARATION DRAFT - VERIFY BEFORE FILING"
    totals=view["totals"]
    supplier,buyer=view["supplier"],view["buyer"]
    letter=(f"{label}\n\nDate: {view['as_of']}\nTo: {buyer['name']}\n{buyer['address']}\n\n"
            f"Subject: Request for settlement of delayed supplier payments\n\n"
            f"We, {supplier['name']}, request reconciliation and settlement of the attached invoice schedule. "
            f"As of {view['as_of']}, unpaid principal is INR {totals['principal']}; calculated delayed-payment interest is INR {totals['interest']}; "
            f"the preparation total is INR {totals['total']}. Bank receipts of INR {totals['bank_received']} and documented TDS credit of INR {totals['tds_recognized']} are accounted for separately.\n\n"
            "Sections 15 and 16 of the MSMED Act 2006 govern payment deadlines and monthly-rest compound interest at three times the notified RBI bank rate, subject to eligibility and the underlying facts. "
            "Please review the evidence index and contact us to resolve any disagreement about these records.\n\n"
            "Tax note for professional review: the legacy Income-tax Act 1961 Section 43B(h), and the applicable successor provision under the Income-tax Act 2025, address certain deductions for delayed MSE payments on an actual-payment basis. "
            "Applicability, tax year and current provision should be checked by your tax adviser. This letter makes no determination of your tax liability.\n\n"
            f"Calculation convention: {CONVENTION}\n\n"
            f"Prepared with Bakaya for {supplier['name']}; reviewed locally by {state['approval']['reviewer']}. "
            "Document preparation only; not legal advice. No portal submission or buyer communication has occurred.\n")
    odr={"document_status":label,"portal_schema_verified":False,"notice":"Generic claim field worksheet; current ODR mandatory fields and format have not been verified.",
         "supplier":supplier,"buyer":buyer,"as_of":view["as_of"],"totals":totals,"invoices":view["invoices"],"rules_source":RULES_SOURCE,"convention":CONVENTION}
    evidence=[{key:source.get(key) for key in ("id","file","kind","page","line","status","sha256","text","replacement_source_id")} for source in view["sources"]]
    output=io.BytesIO()
    with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("README.txt",label+"\n\nHuman approval permits this local download only. Nothing has been filed or sent.\n"+CONVENTION+"\nRate and invoice evidence references appear in each CSV line.\nPDF figures use rounded display amounts; sum interest_exact for exact totals.\n")
        archive.writestr("odr-field-sheet.json",json.dumps(odr,indent=2))
        archive.writestr("invoice-summary.csv",csv_bytes(view["invoices"],["id","number","amount","due_date","interest_start","outstanding","interest","total","source_refs","field_sources"]))
        archive.writestr("interest-schedule.csv",csv_bytes(view["schedule"],["invoice_id","start","end","days","principal","capitalized_interest","bank_rate","annual_rate","interest","interest_exact","rate_source","source_refs"]))
        archive.writestr("payment-reconciliation.csv",csv_bytes(view["matches"],["payment_id","invoice_id","amount","tds_amount","confidence","reason","source_refs"]))
        archive.writestr("evidence-index.csv",csv_bytes(evidence,["id","file","kind","page","line","status","sha256","text","replacement_source_id"]))
        archive.writestr("evidence-index.json",json.dumps(evidence,indent=2))
        archive.writestr("demand-letter.txt",letter)
        archive.writestr("demand-letter.pdf",pdf_bytes("Bakaya demand letter draft",[letter]))
        archive.writestr("interest-schedule.pdf",pdf_bytes("Bakaya interest schedule",[label,f"As of {view['as_of']}. Principal INR {totals['principal']}; interest INR {totals['interest']}; total INR {totals['total']}.",CONVENTION,"End dates below are exclusive. Each segment links to invoice/payment/rate evidence IDs in the evidence index. Row accruals round for display; the CSV includes exact unrounded values."],
            [["Invoice / period","Days","Principal INR","Capitalized INR","3x rate %","Accrual INR","Evidence IDs"]]+
            [[r["invoice_id"]+"\n"+r["start"]+" to "+r["end"],r["days"],r["principal"],r["capitalized_interest"],r["annual_rate"],r["interest"],", ".join(r["source_refs"])] for r in view["schedule"]],
            col_widths=[130,25,62,60,38,65,125]))
        archive.writestr("odr-field-sheet.pdf",pdf_bytes("Claim preparation worksheet",[label,odr["notice"],f"Supplier: {supplier['name']} | Udyam: {supplier['udyam_number']}",f"Buyer: {buyer['name']} | {buyer['address']}",f"Total: INR {totals['total']} | principal INR {totals['principal']} | interest INR {totals['interest']}",f"Rules: {RULES_SOURCE}"]))
        archive.writestr("audit.json",json.dumps(view["audit"],indent=2))
        archive.writestr("approval.json",json.dumps(state["approval"],indent=2))
        used=set()
        for source in view["sources"]:
            name=source.get("stored_name")
            if name and name not in used:
                path=upload_dir(view["id"])/Path(name).name
                if path.is_file():
                    archive.write(path,"evidence/"+Path(name).name)
                    used.add(name)
    return output.getvalue()
