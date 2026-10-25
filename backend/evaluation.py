"""Reproducible synthetic benchmark, separate daily interest reference oracle."""
from __future__ import annotations

import calendar
import json
from datetime import date, timedelta, datetime, timezone
from decimal import Decimal, localcontext
from pathlib import Path

from .engine import analyze, money
from .fixtures import evaluation_cases


def reference_interest(amount, start, as_of, credits, rates):
    """Independent day-by-day oracle; no production schedule/math helper calls."""
    with localcontext() as ctx:
        ctx.prec=40
        principal=Decimal(amount)
        capitalized=Decimal(0)
        accrued=Decimal(0)
        principal-=sum((Decimal(v) for d,v in credits if d<start),Decimal(0))
        cursor=start
        while cursor<=as_of:
            principal-=sum((Decimal(v) for d,v in credits if d==cursor),Decimal(0))
            month_distance=(cursor.year-start.year)*12+cursor.month-start.month
            rest_day=min(start.day,calendar.monthrange(cursor.year,cursor.month)[1])
            if month_distance>0 and cursor.day==rest_day:
                capitalized+=accrued
                accrued=Decimal(0)
            rate=next(r for r in rates if r.start<=cursor<r.end)
            accrued+=(principal+capitalized)*rate.bank_rate*Decimal(3)/Decimal(100)/Decimal(365)
            cursor+=timedelta(days=1)
        return capitalized+accrued


def evaluate():
    fixtures=evaluation_cases()
    report={"dataset":"20 fictional scenarios; explicit TDS proof; not real customer validation","cases":20,
            "method":"Matching and due-date labels are explicit fixture truth. Interest checked against independent daily Decimal oracle; closed-form hand calculations in unit tests. Every fixture shares the disclosed Actual/365 monthly-anniversary convention.",
            "baseline_definition":"Deliberately flawed first-open-invoice matcher ignores documented TDS and guesses duplicate payments; cannot be approved.",
            "metrics":{},"results":[],"integrations":"Local audit only; no hosted neatlogs or Entire trace IDs claimed."}
    scores={mode:{"correct_cases":0,"interest_max_error":Decimal(0),"false_short_payments":0,"ambiguities_flagged":0,"due_dates_correct":0,"verdicts_correct":0} for mode in ("baseline","fixed")}
    review={"rate_confirmed":True,"buyer_confirmed":True}
    for fixture in fixtures:
        case=fixture["input"]
        expected=fixture["expected_matches"]
        expected_principal={inv.id:inv.amount for inv in case.invoices}
        expected_interest={}
        for inv in case.invoices:
            expected_principal[inv.id]-=sum((Decimal(cash)+Decimal(tax) for _,iid,cash,tax in expected if iid==inv.id),Decimal(0))
            credits=[(next(p.date for p in case.payments if p.id==pid),Decimal(cash)+Decimal(tax)) for pid,iid,cash,tax in expected if iid==inv.id]
            start=date.fromisoformat(fixture["expected_due"][inv.id])+timedelta(days=1)
            expected_interest[inv.id]=reference_interest(inv.amount,start,case.as_of,credits,case.rates)
        row={"id":fixture["id"],"difficulty":fixture["kind"],"expected_matches":expected,"expected_due":fixture["expected_due"],
             "expected_principal":{k:money(v) for k,v in expected_principal.items()},"expected_interest":{k:money(v) for k,v in expected_interest.items()},"expected_block":fixture["expected_block"]}
        for mode in ("baseline","fixed"):
            result=analyze(case,review,mode)
            actual=[(m["payment_id"],m["invoice_id"],m["amount"],m["tds_amount"]) for m in result["matches"]]
            correct=sorted(actual)==sorted(expected)
            scores[mode]["correct_cases"]+=int(correct)
            ambiguity=any(b["code"]=="ambiguous_payment" for b in result["blockers"])
            scores[mode]["ambiguities_flagged"]+=int(fixture["kind"]=="ambiguous" and ambiguity)
            due_correct=all(i["due_date"]==fixture["expected_due"][i["id"]] for i in result["invoices"])
            scores[mode]["due_dates_correct"]+=int(due_correct)
            block=fixture["expected_block"]
            verdict_correct=not block or any(b["code"]==block for b in result["blockers"])
            scores[mode]["verdicts_correct"]+=int(verdict_correct)
            errors=[abs(Decimal(i["interest"])-expected_interest[i["id"]]) for i in result["invoices"]]
            error=max(errors,default=Decimal(0))
            scores[mode]["interest_max_error"]=max(scores[mode]["interest_max_error"],error)
            if fixture["kind"]=="tds" and any(Decimal(i["outstanding"])>expected_principal[i["id"]] for i in result["invoices"]):
                scores[mode]["false_short_payments"]+=1
            row[mode]={"matching_correct":correct,"due_dates_correct":due_correct,"max_interest_error":money(error),"ambiguity_flagged":ambiguity,"totals":result["totals"]}
        report["results"].append(row)
    for mode,score in scores.items():
        report["metrics"][mode]={"matching_accuracy":score["correct_cases"]/len(fixtures)*100,"matching_correct":score["correct_cases"],"matching_cases":len(fixtures),
            "max_interest_error":money(score["interest_max_error"]),"false_short_payments":score["false_short_payments"],"ambiguities_flagged":score["ambiguities_flagged"],"planted_ambiguities":2,
            "due_dates_correct":score["due_dates_correct"],"eligibility_and_ambiguity_verdicts_correct":score["verdicts_correct"]}
    report["baseline"]=report["metrics"]["baseline"]
    report["fixed"]=report["metrics"]["fixed"]
    return report


def main():
    target=Path(__file__).parent/"evaluation_data"
    target.mkdir(exist_ok=True)
    (target/"results.json").write_text(json.dumps(evaluate(),indent=2),encoding="utf-8")
    fixtures=[]
    for item in evaluation_cases():
        fixtures.append({**item,"input":item["input"].model_dump(mode="json")})
    (target/"synthetic-cases.json").write_text(json.dumps(fixtures,indent=2),encoding="utf-8")
    print(json.dumps(evaluate()["metrics"],indent=2))


if __name__=="__main__":
    main()
