"""Checks en/hi/mr copy and backend verdict templates. Stdlib only.

Run from anywhere: python frontend/src/i18n/check_i18n.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # repo root: frontend/src/i18n -> repo
LANGS = ("en", "hi", "mr")
TEMPLATE_DIR = ROOT / "backend" / "templates"
CONTRACTS = ROOT / "docs" / "CONTRACTS.md"

RULE_IDS = [
    "R1_TOURIST_VISA", "R2_RA_NOT_LISTED", "R3_NO_RC_NUMBER", "R4_FEE_OVER_CAP",
    "R5_NO_TRIPARTITE_CONTRACT", "R6_HIGH_RISK_CORRIDOR", "R7_INFORMAL_CHANNEL_ONLY",
    "R8_NO_RECEIPT", "R9_PBBY_MISSING", "H1_SALARY_ANOMALY", "H2_PASSPORT_HANDOVER",
    "H3_PRESSURE",
]

# Same text as the "i18n keys" code block in docs/CONTRACTS.md (lead-owned).
# Kept here so the check runs when the docs folder is not present.
EMBEDDED_CONTRACT = """
app.name app.tagline app.synthetic_badge lang.en lang.hi lang.mr
nav.check nav.verdict nav.safety nav.family nav.map nav.limits
check.title check.intro check.paste_label check.paste_placeholder check.upload_label check.submit
check.demo_title check.demo_scam check.demo_near_miss check.privacy_note check.analyzing
verdict.title verdict.STOP.title verdict.STOP.body verdict.VERIFY_FIRST.title verdict.VERIFY_FIRST.body
verdict.NO_RED_FLAGS_FOUND.title verdict.NO_RED_FLAGS_FOUND.body verdict.ra_list_date({date})
verdict.quote_label verdict.source_label verdict.rule_source verdict.heuristic_badge
verdict.status.hit verdict.status.clear verdict.status.unknown verdict.method.llm verdict.method.fallback
verdict.download_packet verdict.make_safety_plan verdict.facts_title verdict.not_found
severity.critical severity.high severity.medium severity.low severity.info
rule.<ID>.title rule.<ID>.hit rule.<ID>.clear rule.<ID>.unknown   (for all 12 rule ids)
next.STOP next.VERIFY_FIRST next.NO_RED_FLAGS_FOUND
safety.title safety.intro safety.traveller_alias safety.contact_alias safety.contact_channel safety.add_contact
safety.itinerary safety.itinerary_placeholder safety.interval_hours safety.save safety.checkin safety.checkin_note
safety.status.ok safety.status.due safety.status.missed safety.next_due({time}) safety.last_checkin({time})
safety.demo_advance safety.simulated_note
family.title family.alert_title family.alert_body({alias}) family.open_packet family.no_alerts family.simulated_badge
map.title map.login_required map.email map.password map.sign_in map.sign_out map.synthetic_badge
map.repeated_agents map.repeated_templates map.districts map.reports
limits.title limits.what_it_does limits.what_it_does_not limits.not_legal_advice limits.no_auto_report
limits.sources_title limits.helplines_title limits.verify_contacts
error.generic error.network common.loading common.back common.close
"""

# App-side keys that are not in docs/CONTRACTS.md. Remove once the contract lists them.
EXTRA_KEYS = {
    "checkin.change_time",
    "checkin.contacts",
    "checkin.contacts_list",
    "checkin.cta",
    "checkin.done",
    "checkin.get_help",
    "checkin.missed_note",
    "checkin.next",
    "checkin.no_plan_body",
    "checkin.no_plan_title",
    "checkin.no_trip",
    "checkin.previous",
    "checkin.see_family",
    "checkin.simulated",
    "checkin.timeline",
    "checkin.title_due",
    "checkin.title_missed",
    "checkin.title_ok",
    "checkin.today",
    "checkin.tomorrow",
    "checkin.trip",
    "checkin.yesterday",
    "demo.bangkok_hint",
    "demo.dubai_hint",
    "error.unavailable",
    "evidence.ask_next",
    "evidence.back",
    "evidence.counter",
    "evidence.download",
    "evidence.heuristic_note",
    "evidence.next",
    "evidence.no_quote",
    "evidence.none",
    "evidence.offer_text",
    "evidence.prev",
    "evidence.quoted_line",
    "evidence.rule_reference",
    "evidence.title",
    "fact.agent",
    "fact.channel",
    "fact.contract",
    "fact.country",
    "fact.employer",
    "fact.fee",
    "fact.passport",
    "fact.payment",
    "fact.pbby",
    "fact.rc",
    "fact.receipt",
    "fact.role",
    "fact.salary",
    "fact.transit",
    "fact.visa",
    "family2.back_checkin",
    "family2.cta_report",
    "family2.phone_view",
    "family2.reporting",
    "family2.simulated",
    "family2.sub",
    "family2.sub_none",
    "family2.title",
    "family2.title_none",
    "family2.to",
    "help.cyber.name",
    "help.cyber.what",
    "help.demo_directory",
    "help.embassy.name",
    "help.embassy.what",
    "help.emigrate.name",
    "help.emigrate.what",
    "help.limit_demo",
    "help.limit_legal",
    "help.limit_report",
    "help.limit_wrong",
    "help.madad.name",
    "help.madad.what",
    "help.mea.name",
    "help.mea.what",
    "help.police.name",
    "help.police.what",
    "help.report_zip",
    "help.title",
    "help.verify",
    "help.zip_none",
    "help.zip_note",
    "home.cta",
    "home.hindi_line",
    "home.step_add",
    "home.step_checkins",
    "home.step_evidence",
    "home.steps_label",
    "home.sub",
    "home.title",
    "illo.job_offer",
    "illo.tourist_visa",
    "illo.visa_type",
    "login.cta",
    "login.hero",
    "login.restricted",
    "login.show_password",
    "login.title",
    "nav2.check",
    "nav2.checkins",
    "nav2.help",
    "pdetail.back",
    "pdetail.copied",
    "pdetail.copy",
    "pdetail.district_total",
    "pdetail.districts",
    "pdetail.full_hash",
    "pdetail.graph_label",
    "pdetail.hash",
    "pdetail.hash_explain",
    "pdetail.not_found",
    "pdetail.reports",
    "pdetail.reports_body",
    "pdetail.side_label",
    "pdetail.title_agent",
    "pdetail.title_template",
    "plan.channel_placeholder",
    "plan.contact_n",
    "plan.cta",
    "plan.demo_only",
    "plan.every",
    "plan.half_contact",
    "plan.hours_option",
    "plan.hours_short",
    "plan.interval_label",
    "plan.name_placeholder",
    "plan.need_body",
    "plan.need_title",
    "plan.optional",
    "plan.permission",
    "plan.ring_label",
    "plan.sub",
    "plan.title",
    "plan.trip",
    "plan.you",
    "pmap.all_districts",
    "pmap.chips_label",
    "pmap.demo",
    "pmap.explore",
    "pmap.filter_label",
    "pmap.hash_note",
    "pmap.illustrative",
    "pmap.repeated_hashes",
    "pmap.row",
    "pmap.synthetic",
    "pmap.title",
    "result.cta_evidence",
    "result.cta_report",
    "result.foot_confirm",
    "result.foot_quotes",
    "result.get_help",
    "result.not_clearance",
    "result.passed",
    "result.plan_checkins",
    "result.points_heading",
    "result.severity",
    "result.sub.NO_RED_FLAGS_FOUND",
    "result.sub.STOP",
    "result.sub.VERIFY_FIRST",
    "result.tag.NO_RED_FLAGS_FOUND",
    "result.tag.STOP",
    "result.tag.VERIFY_FIRST",
    "result.word.FIRST",
    "result.word.NO_RED_FLAGS_FOUND",
    "result.word.STOP",
    "result.word.VERIFY",
    "review.cta",
    "review.edit",
    "review.flagged",
    "review.more",
    "review.no_quote",
    "review.not_analyzed",
    "review.source_quote",
    "review.sub",
    "review.title",
    "steps.add",
    "steps.done",
    "steps.label",
    "steps.result",
    "steps.review",
    "submit.cta",
    "submit.drop_title",
    "submit.drop_types",
    "submit.files_label",
    "submit.has_text",
    "submit.paste_hint",
    "submit.paste_placeholder",
    "submit.remove_file",
    "submit.sub",
    "submit.tab_paste",
    "submit.tab_upload",
    "submit.tabs_label",
    "submit.title",
    "submit.try_demo",
    "ui.demo",
    "ui.demo_data",
    "ui.footer",
    "ui.home_label",
    "ui.institution_link",
    "ui.language",
    "ui.main_nav",
    "ui.main_nav_mobile",
    "ui.new_tab",
    "ui.no",
    "ui.skip",
    "ui.yes",
    "value.token.agent",
    "value.token.bank_transfer",
    "value.token.card",
    "value.token.cash",
    "value.token.crypto",
    "value.token.email",
    "value.token.employer",
    "value.token.facebook",
    "value.token.instagram",
    "value.token.office_address",
    "value.token.other",
    "value.token.phone",
    "value.token.telegram",
    "value.token.upi",
    "value.token.website",
    "value.token.whatsapp",
    "value.token.worker",
    "value.visa.employment",
    "value.visa.tourist",
    "value.visa.unknown",
    "value.visa.visit",
    "value.visa.work",
    "verdict.ra_not_checked",
}

FORBIDDEN = [
    "safe", "guaranteed", "genuine", "verified", "100%", "no risk", "fraud", "scam", "scammer",
    "सुरक्षित", "सुरक्षीत", "सुरक्षा", "धोखेबाज", "फसवणूक करणारा",
]

TEMPLATE_PREFIXES = ("verdict.", "rule.", "next.", "severity.", "safety.status.")
TEMPLATE_EXTRA = {"family.alert_body", "limits.helplines_title", "limits.verify_contacts"}
EXACT_NO_RED_FLAGS_EN = (
    "No red flags found. Confirm with the Protector of Emigrants before paying anything."
)

KEY_RE = re.compile(r"^[a-z]+\.[A-Za-z0-9_.<>]+$")


def tokens_to_keys(block: str) -> set[str]:
    keys: set[str] = set()
    for raw in block.split():
        tok = re.sub(r"\(\{\w+\}\)$", "", raw)  # verdict.ra_list_date({date}) -> verdict.ra_list_date
        if "<ID>" in tok:
            keys.update(tok.replace("<ID>", rid) for rid in RULE_IDS)
        elif KEY_RE.match(tok):
            keys.add(tok)
    return keys


def contract_block_keys(text: str) -> set[str] | None:
    if "## i18n keys" not in text:
        return None
    section = text.split("## i18n keys", 1)[1]
    parts = section.split("```")
    if len(parts) < 2:
        return None
    return tokens_to_keys(parts[1])


def load(path: Path, errors: list[str]) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.name}: cannot load ({exc})")
        return None
    if not isinstance(data, dict) or not all(isinstance(v, str) and v.strip() for v in data.values()):
        errors.append(f"{path.name}: must be a flat object of non-empty strings")
        return None
    return data


def sentences(text: str) -> int:
    return len([s for s in re.split(r"(?<=[.!?।])\s+", text.strip()) if s])


def main() -> int:
    errors: list[str] = []
    contract_keys = tokens_to_keys(EMBEDDED_CONTRACT)
    expected = contract_keys | EXTRA_KEYS

    if CONTRACTS.exists():
        contract = contract_block_keys(CONTRACTS.read_text(encoding="utf-8"))
        if contract is None:
            errors.append("docs/CONTRACTS.md: no i18n keys block found")
        elif contract != contract_keys:
            errors.append(
                f"embedded key list drifted from docs/CONTRACTS.md: "
                f"missing={sorted(contract - contract_keys)} extra={sorted(contract_keys - contract)}"
            )
    else:
        print("note: docs/CONTRACTS.md not in this worktree; checked against embedded key list")

    data = {lang: load(HERE / f"{lang}.json", errors) for lang in LANGS}
    if any(d is None for d in data.values()):
        return report(errors, expected)

    en, hi, mr = data["en"], data["hi"], data["mr"]

    # 1. identical key sets, and all contract keys present
    for lang in ("hi", "mr"):
        if set(data[lang]) != set(en):
            diff = sorted(set(data[lang]) ^ set(en))
            errors.append(f"{lang}.json key set differs from en.json: {diff}")
    missing = sorted(expected - set(en))
    extra = sorted(set(en) - expected)
    if missing:
        errors.append(f"contract keys missing from en.json: {missing}")
    if extra:
        errors.append(f"keys in en.json not in contract: {extra}")

    # 2. placeholders match per key
    for key in sorted(en):
        ph = {lang: sorted(set(re.findall(r"\{(\w+)\}", data[lang].get(key, "")))) for lang in LANGS}
        if not (ph["en"] == ph["hi"] == ph["mr"]):
            errors.append(f"placeholder mismatch for {key}: {ph}")

    # 3. forbidden words in any copy value (keys are not user-facing)
    for lang in LANGS:
        for key, value in data[lang].items():
            low = value.casefold()
            for word in FORBIDDEN:
                if word.casefold() in low:
                    errors.append(f"{lang}.json {key}: forbidden word {word!r}")

    # 4. exact verdict text and length rules
    if en.get("verdict.NO_RED_FLAGS_FOUND.body") != EXACT_NO_RED_FLAGS_EN:
        errors.append("verdict.NO_RED_FLAGS_FOUND.body (en) is not the required wording")
    for lang, d in data.items():
        for key, value in d.items():
            if key.startswith("rule.") and key.endswith(".title") and len(value.split()) > 6:
                errors.append(f"{lang}.json {key}: title over 6 words")
            is_body = (key.startswith("rule.") and key.rsplit(".", 1)[1] in ("hit", "clear", "unknown")) \
                or (key.startswith("verdict.") and key.endswith(".body"))
            if is_body and sentences(value) > 2:
                errors.append(f"{lang}.json {key}: more than 2 sentences")

    # 5. backend templates: exact subset, identical text
    expected_tpl = {k for k in en if k.startswith(TEMPLATE_PREFIXES) or k in TEMPLATE_EXTRA}
    for lang in LANGS:
        path = TEMPLATE_DIR / f"verdict.{lang}.json"
        tpl = load(path, errors)
        if tpl is None:
            continue
        if set(tpl) != expected_tpl:
            errors.append(
                f"{path.name}: key set wrong; missing={sorted(expected_tpl - set(tpl))} "
                f"extra={sorted(set(tpl) - expected_tpl)}"
            )
        for key, value in tpl.items():
            if key in data[lang] and data[lang][key] != value:
                errors.append(f"{path.name} {key}: text differs from frontend {lang}.json")

    return report(errors, expected, len(en), len(expected_tpl))


def report(errors: list[str], expected: set[str], n_en: int | None = None, n_tpl: int | None = None) -> int:
    if errors:
        print(f"FAIL: {len(errors)} problem(s)")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"OK: {len(expected)} contract keys; en/hi/mr {n_en} keys each; "
          f"backend templates {n_tpl} keys each")
    return 0


if __name__ == "__main__":
    sys.exit(main())
