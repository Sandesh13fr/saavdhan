"""Synthetic offer evaluation harness. Standard library plus the project's backend package.

Run from the repo root:  .venv\\Scripts\\python eval\\run_eval.py [--llm] [--limit N]

Default mode is the deterministic fallback extractor and never touches the network.
--llm uses backend.providers.extract_offer only when provider_available() is true, and
falls back per offer on ValueError (counted). Results are synthetic; not real-world accuracy.
Exit code is non-zero only on a crash.
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import math
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.extract_fallback import extract  # noqa: E402
from backend.ingest import ingest_bytes  # noqa: E402
from backend.models import FieldValue  # noqa: E402
from backend.rules import RULES, run_rules  # noqa: E402
from backend.verdict import decide  # noqa: E402

OFFERS_DIR = ROOT / "eval" / "offers"
RESULTS_DIR = ROOT / "eval" / "results"
REPORT_PATH = ROOT / "eval" / "REPORT.md"
RULE_IDS = [r["id"] for r in RULES]
VERDICTS = ["STOP", "VERIFY_FIRST", "NO_RED_FLAGS_FOUND"]
NUMERIC_FIELDS = {"fees_demanded_inr", "salary_amount"}
SYNTHETIC_NOTICE = ("Synthetic evaluation set of 40 offers written for this project. Not real-world accuracy. "
                    "The fallback extractor was tuned on this same set after the first run (27/40), so these scores are "
                    "optimistic; a held-out set is needed for an honest estimate.")
LIKELY_CAUSES_HEADING = "## Likely causes"


def load_offers(directory: Path = OFFERS_DIR, limit: int | None = None) -> list[dict]:
    files = sorted(Path(directory).glob("[0-9][0-9][0-9].json"))
    fixtures = [json.loads(p.read_text(encoding="utf-8")) for p in files]
    return fixtures[:limit] if limit else fixtures


def git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                             text=True, check=True)
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _has(fv: FieldValue | None) -> bool:
    return bool(fv and (fv.value or "").strip())


def analyse_offer(fixture: dict, llm_ok: bool, llm_stats: dict) -> dict:
    expected = fixture["expected"]
    sources, _errors = ingest_bytes(f"{fixture['id']}.txt", fixture["text"].encode("utf-8"))
    t0 = time.perf_counter()
    offer, method = None, "fallback"
    if llm_ok:
        from backend.providers import extract_offer  # lazy: imported only with --llm
        try:
            offer = asyncio.run(extract_offer(sources))
        except ValueError:
            llm_stats["failures"] += 1
        if offer is not None:
            method = "llm"
    if offer is None:
        offer = extract(sources)
    ra = None
    if _has(offer.agent_name) or _has(offer.agent_rc_number):
        ra = {"status": "listed" if expected.get("ra_assumed_listed") else "not_listed",
              "list_date": "synthetic", "evidence": "eval stub"}
    hits = run_rules(offer, ra)
    verdict = decide(hits, expected["recruiter_list_date"])
    elapsed_ms = (time.perf_counter() - t0) * 1000
    predicted_facts = {}
    for key in expected["facts"]:
        fv = getattr(offer, key, None)
        predicted_facts[key] = fv.value if isinstance(fv, FieldValue) else None
    return {
        "id": fixture["id"], "language": fixture["language"], "label": fixture["label"],
        "extraction_method": method, "time_ms": elapsed_ms,
        "expected_verdict": expected["verdict"], "predicted_verdict": verdict.level,
        "expected_rule_hits": set(expected["rule_hits"]),
        "rule_statuses": {h.rule_id: h.status for h in hits},
        "expected_facts": expected["facts"], "predicted_facts": predicted_facts,
    }


def _prf(tp: int, fp: int, fn: int) -> dict:
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None
    return {"precision": precision, "recall": recall, "f1": f1}


def rule_metrics(records: list[dict]) -> dict:
    out = {}
    for rid in RULE_IDS:
        tp = fp = fn = tn = 0
        for r in records:
            truth = rid in r["expected_rule_hits"]
            pred = r["rule_statuses"].get(rid) == "hit"
            tp += truth and pred
            fp += (not truth) and pred
            fn += truth and not pred
            tn += (not truth) and (not pred)
        out[rid] = {"tp": tp, "fp": fp, "fn": fn, "tn": tn, **_prf(tp, fp, fn)}
    f1s = [m["f1"] for m in out.values() if m["f1"] is not None]
    return {"per_rule": out, "macro_f1": sum(f1s) / len(f1s) if f1s else None}


def verdict_metrics(records: list[dict]) -> dict:
    matrix = {e: {p: 0 for p in VERDICTS} for e in VERDICTS}
    for r in records:
        matrix[r["expected_verdict"]][r["predicted_verdict"]] += 1
    correct = sum(matrix[v][v] for v in VERDICTS)
    return {"confusion": matrix, "accuracy": correct / len(records) if records else None,
            "n": len(records)}


def _norm(value, key: str):
    if value is None:
        return None
    text = str(value).strip().casefold()
    if key in NUMERIC_FIELDS:
        text = text.replace(",", "")
    return text or None


def _field_match(key: str, expected, predicted) -> bool:
    exp, pred = _norm(expected, key), _norm(predicted, key)
    if exp is None or pred is None:
        return exp is None and pred is None
    if key in NUMERIC_FIELDS:
        try:
            return float(exp) == float(pred)
        except ValueError:
            return False
    return exp == pred


def field_metrics(records: list[dict]) -> dict:
    def tally(rows):
        total = correct = 0
        for r in rows:
            for key, expected in r["expected_facts"].items():
                total += 1
                correct += _field_match(key, expected, r["predicted_facts"].get(key))
        return {"correct": correct, "total": total, "accuracy": correct / total if total else None}

    keys = sorted({k for r in records for k in r["expected_facts"]})
    return {
        "overall": tally(records),
        "by_field": {k: tally([{**r, "expected_facts": {k: r["expected_facts"][k]}} for r in records
                               if k in r["expected_facts"]]) for k in keys},
        "by_language": {lang: tally([r for r in records if r["language"] == lang])
                        for lang in sorted({r["language"] for r in records})},
    }


def timing_metrics(records: list[dict]) -> dict:
    times = sorted(r["time_ms"] for r in records)
    if not times:
        return {"median_ms": None, "p95_ms": None}
    p95 = times[max(0, math.ceil(0.95 * len(times)) - 1)]
    return {"median_ms": statistics.median(times), "p95_ms": p95}


def misclassified(records: list[dict]) -> list[dict]:
    out = []
    for r in records:
        if r["expected_verdict"] == r["predicted_verdict"]:
            continue
        differing = [{"rule": rid, "expected_hit": rid in r["expected_rule_hits"],
                      "predicted_status": r["rule_statuses"].get(rid)}
                     for rid in RULE_IDS
                     if (r["rule_statuses"].get(rid) == "hit") != (rid in r["expected_rule_hits"])]
        out.append({"id": r["id"], "language": r["language"], "label": r["label"],
                    "expected_verdict": r["expected_verdict"], "predicted_verdict": r["predicted_verdict"],
                    "differing_rules": differing})
    return out


def evaluate(fixtures: list[dict], llm_ok: bool = False) -> dict:
    llm_stats = {"failures": 0}
    records = [analyse_offer(f, llm_ok, llm_stats) for f in fixtures]
    rules = rule_metrics(records)
    return {
        "meta": {"date": dt.date.today().isoformat(), "commit": git_commit(),
                 "extractor_mode": "llm" if llm_ok else "fallback", "n_offers": len(records),
                 "llm_failures": llm_stats["failures"], "notice": SYNTHETIC_NOTICE},
        "verdict": verdict_metrics(records),
        "rules": rules,
        "macro_rule_f1": rules["macro_f1"],
        "fields": field_metrics(records),
        "timing_ms": timing_metrics(records),
        "misclassified": misclassified(records),
        "per_offer": [{k: (sorted(v) if isinstance(v, set) else v) for k, v in r.items()} for r in records],
    }


def _pct(x) -> str:
    return "n/a" if x is None else f"{x:.3f}"


def _ms(x) -> str:
    return "n/a" if x is None else f"{x:.2f}"


def render_report(res: dict, preserved_causes: str) -> str:
    m = res["meta"]
    L = [
        "# Saavdhan fallback extraction evaluation", "",
        f"> **{SYNTHETIC_NOTICE}**", "",
        f"- Date: {m['date']}",
        f"- Git commit: `{m['commit']}`",
        f"- Extractor mode: `{m['extractor_mode']}`",
        f"- Offers: {m['n_offers']}; LLM fallbacks on ValueError: {m['llm_failures']}", "",
        "## Headline", "",
        f"- Verdict accuracy: {_pct(res['verdict']['accuracy'])}",
        f"- Macro rule F1: {_pct(res['macro_rule_f1'])}",
        f"- Field accuracy: {_pct(res['fields']['overall']['accuracy'])}",
        f"- Median analysis time: {_ms(res['timing_ms']['median_ms'])} ms (p95 {_ms(res['timing_ms']['p95_ms'])} ms)", "",
        "## Verdict confusion matrix (rows expected, columns predicted)", "",
        "| expected \\ predicted | " + " | ".join(VERDICTS) + " |",
        "|---|" + "---|" * len(VERDICTS),
    ]
    for e in VERDICTS:
        L.append(f"| {e} | " + " | ".join(str(res["verdict"]["confusion"][e][p]) for p in VERDICTS) + " |")
    L += ["", "## Per-rule precision, recall and F1", "",
          "| rule | TP | FP | FN | TN | precision | recall | F1 |", "|---|---|---|---|---|---|---|---|"]
    for rid, v in res["rules"]["per_rule"].items():
        L.append(f"| {rid} | {v['tp']} | {v['fp']} | {v['fn']} | {v['tn']} | {_pct(v['precision'])} | "
                 f"{_pct(v['recall'])} | {_pct(v['f1'])} |")
    L += ["", f"Macro F1 (rules with any truth or prediction): {_pct(res['macro_rule_f1'])}", "",
          "## Extraction field accuracy", "",
          "| field | correct | total | accuracy |", "|---|---|---|---|"]
    for k, v in res["fields"]["by_field"].items():
        L.append(f"| {k} | {v['correct']} | {v['total']} | {_pct(v['accuracy'])} |")
    o = res["fields"]["overall"]
    L += [f"| **overall** | {o['correct']} | {o['total']} | {_pct(o['accuracy'])} |", "",
          "| language | correct | total | accuracy |", "|---|---|---|---|"]
    for k, v in res["fields"]["by_language"].items():
        L.append(f"| {k} | {v['correct']} | {v['total']} | {_pct(v['accuracy'])} |")
    t = res["timing_ms"]
    L += ["", "## Analysis time", "", f"- Median: {_ms(t['median_ms'])} ms",
          f"- p95: {_ms(t['p95_ms'])} ms", "",
          "Time covers extraction, rules and verdict; ingest is excluded.", "",
          "## Misclassified offers", ""]
    if not res["misclassified"]:
        L.append("None.")
    else:
        L += ["| id | language | label | expected | predicted | rules that differ (expected hit / predicted status) |",
              "|---|---|---|---|---|---|"]
        for mis in res["misclassified"]:
            diffs = ", ".join(f"{d['rule']} ({'hit' if d['expected_hit'] else 'not hit'} / {d['predicted_status']})"
                              for d in mis["differing_rules"]) or "none"
            L.append(f"| {mis['id']} | {mis['language']} | {mis['label']} | {mis['expected_verdict']} | "
                     f"{mis['predicted_verdict']} | {diffs} |")
    L += ["", "## Definitions", "",
          "- A rule prediction is a hit when its status is `hit`; ground truth is membership in `expected.rule_hits`.",
          "- F1 = 2TP / (2TP + FP + FN); undefined (excluded from macro) when there is no truth and no prediction.",
          "- Field match: casefold and strip; numeric fields compare as numbers; expected null requires a null prediction.", ""]
    body = "\n".join(L)
    if preserved_causes:
        body = body.rstrip() + "\n\n" + preserved_causes.strip() + "\n"
    return body


def _existing_causes() -> str:
    if not REPORT_PATH.exists():
        return ""
    text = REPORT_PATH.read_text(encoding="utf-8")
    idx = text.find(LIKELY_CAUSES_HEADING)
    return text[idx:] if idx >= 0 else ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--llm", action="store_true", help="use the LLM extractor when it is available")
    parser.add_argument("--limit", type=int, default=None, help="evaluate only the first N offers")
    args = parser.parse_args(argv)
    llm_ok = False
    if args.llm:
        from backend.providers import provider_available
        llm_ok = provider_available()
        if not llm_ok:
            print("LLM not available (SAAVDHAN_ENABLE_LLM / API key); using fallback extractor.", file=sys.stderr)
    res = evaluate(load_offers(limit=args.limit), llm_ok=llm_ok)
    mode = res["meta"]["extractor_mode"]
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / f"{mode}.json").write_text(json.dumps(res, indent=2, ensure_ascii=False, default=str),
                                              encoding="utf-8")
    REPORT_PATH.write_text(render_report(res, _existing_causes()), encoding="utf-8")
    print(f"mode={mode} offers={res['meta']['n_offers']} verdict_acc={_pct(res['verdict']['accuracy'])} "
          f"macro_rule_f1={_pct(res['macro_rule_f1'])} field_acc={_pct(res['fields']['overall']['accuracy'])} "
          f"median_ms={_ms(res['timing_ms']['median_ms'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
