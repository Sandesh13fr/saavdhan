"""Family report packet. Contents are local downloads; nothing is sent anywhere."""
from __future__ import annotations

import csv
import io
import json
import zipfile
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

WHERE_TO_REPORT = """WHERE TO REPORT - VERIFY EACH CONTACT ON THE OFFICIAL SITE BEFORE USE
- Ministry of External Affairs helpline: helpline@mea.gov.in
- MADAD consular grievance portal: https://madad.gov.in
- Indian embassy or consulate in the destination country (see https://www.mea.gov.in)
- National cyber crime helpline: 1930, and https://cybercrime.gov.in
- Local police station
- Protector of Emigrants / eMigrate: https://emigrate.gov.in
"""


def csv_bytes(rows, keys):
    output=io.StringIO(newline="")
    writer=csv.DictWriter(output,fieldnames=keys,extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        cells={key:json.dumps(row[key],ensure_ascii=False) if isinstance(row.get(key),(list,dict)) else row.get(key,"") for key in keys}
        # Prevent quoted offer text being interpreted as a spreadsheet formula.
        for key,value in cells.items():
            if isinstance(value,str) and value.startswith(("=","+","-","@","\t","\r")):
                cells[key]="'"+value
        writer.writerow(cells)
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


def fact_rows(offer: dict):
    for name, value in offer.items():
        if name == "source_ids":
            continue
        for item in value if isinstance(value, list) else [value]:
            if item.get("value") is not None:
                yield {"field": name, "value": item["value"], "quote": item["quote"], "source_ref": item["source_ref"]}


def itinerary_text(safety: dict) -> str:
    plan = safety["plan"]
    lines = [
        "ITINERARY AND CHECK-INS",
        f"Traveller alias: {plan['traveller_alias']}",
        "Contacts:",
        *[f"- {c['alias']} via {c['channel']}" for c in plan["contacts"]],
        "Itinerary:",
        *([f"- {item}" for item in plan["itinerary"]] or ["- (none entered)"]),
        f"Check-in interval: every {plan['checkin_interval_hours']} hours",
        f"Last check-in: {plan.get('last_checkin') or 'none'}",
        f"Status: {safety.get('status', 'not computed')}",
        "Check-ins:",
        *([f"- {c['at']}: {c['note']}" for c in safety.get("checkins", [])] or ["- (none)"]),
        "Alerts (SIMULATED - nothing was sent to anyone):",
        *([f"- {a['at']} to {a['to_alias']} via {a['channel']} for check-in due {a['due']} (simulated)"
           for a in safety.get("alerts", [])] or ["- (none)"]),
    ]
    return "\n".join(lines) + "\n"


def packet_zip(view: dict) -> bytes:
    label = "SYNTHETIC DEMO" if view.get("demo") else "Saavdhan report packet"
    analysis = view.get("analysis") or {}
    offer, verdict = analysis.get("offer", {}), analysis.get("verdict", {})
    facts = list(fact_rows(offer))
    hits = verdict.get("rule_hits", [])
    safety = view.get("safety")
    paragraphs = [
        f"Result: {verdict.get('level', 'not analysed')}. Recruiter list date: {verdict.get('ra_list_date', 'not loaded')}.",
        "Rule checks compare stated facts with India's emigration guidance. They are not a legal finding about any person or agency.",
    ]
    if safety:
        paragraphs.append(
            f"Safety net: last check-in {safety['plan'].get('last_checkin') or 'none'}. "
            f"Status {safety.get('status', 'not computed')}. "
            f"Simulated alerts recorded: {len(safety.get('alerts', []))}."
        )
    paragraphs.append(WHERE_TO_REPORT)
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("offer-copy.txt", "\n\n".join(s["text"] for s in view["sources"] if not s.get("line")))
        archive.writestr("extracted-facts.csv", csv_bytes(facts, ["field", "value", "quote", "source_ref"]))
        archive.writestr("rule-checks.csv", csv_bytes(hits, ["rule_id", "severity", "status", "rule_source_url", "heuristic"]))
        archive.writestr("where-to-report.txt", WHERE_TO_REPORT)
        if safety:
            archive.writestr("itinerary-and-checkins.txt", itinerary_text(safety))
        archive.writestr("summary.pdf", pdf_bytes(f"{label}: offer check", paragraphs,
            [["Rule", "Severity", "Status"]] + [[h["rule_id"], h["severity"], h["status"]] for h in hits]))
    return output.getvalue()
