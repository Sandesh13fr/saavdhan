"""Check the synthetic offers using only Python's standard library."""

import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
import unicodedata


CRITICAL = {"R1_TOURIST_VISA", "R6_HIGH_RISK_CORRIDOR"}
HIGH = {
    "R2_RA_NOT_LISTED", "R3_NO_RC_NUMBER", "R4_FEE_OVER_CAP",
    "R5_NO_TRIPARTITE_CONTRACT", "H2_PASSPORT_HANDOVER",
}
CORRIDORS = {"Thailand", "Myanmar", "Cambodia", "Laos"}
ROLES = {
    "data entry", "customer support", "it", "digital marketing",
    "online marketing", "chat support",
}
PHONE = re.compile(r"(?<!\w)(?:\+|00)?[0-9](?:[ ().-]*[0-9]){9,14}(?!\w)")
DEMO_PHONE = re.compile(r"\+91 90000 0[0-9]{4}")
TYPES = {
    "object": dict, "array": list, "string": str,
    "boolean": bool, "null": type(None),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(file):
    return json.loads(file.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def validate(value, spec, location):
    """Implement the validation keywords used by the accompanying schema."""
    kinds = spec["type"]
    if isinstance(kinds, str):
        kinds = [kinds]
    require(any(type(value) is TYPES[kind] for kind in kinds), f"{location}: wrong type")
    if "const" in spec:
        require(value == spec["const"], f"{location}: wrong constant")
    if "enum" in spec:
        require(value in spec["enum"], f"{location}: invalid enum value")
    if isinstance(value, dict):
        require(set(spec.get("required", [])) <= value.keys(), f"{location}: missing keys")
        properties = spec.get("properties", {})
        if spec.get("additionalProperties") is False:
            require(value.keys() <= properties.keys(), f"{location}: unknown keys")
        for key, child in value.items():
            if key in properties:
                validate(child, properties[key], f"{location}.{key}")
    elif isinstance(value, list):
        require(len(value) <= spec.get("maxItems", len(value)), f"{location}: too many items")
        if spec.get("uniqueItems"):
            require(len(value) == len(set(value)), f"{location}: duplicate items")
        for index, child in enumerate(value):
            validate(child, spec["items"], f"{location}[{index}]")
    elif isinstance(value, str):
        require(len(value) >= spec.get("minLength", 0), f"{location}: too short")
        if "pattern" in spec:
            require(re.search(spec["pattern"], value) is not None, f"{location}: pattern mismatch")
        if spec.get("format") == "date":
            require(date.fromisoformat(value).isoformat() == value, f"{location}: invalid date")


def check_offer(offer, schema, filename):
    validate(offer, schema, filename)
    require(offer["id"] == Path(filename).stem, f"{filename}: id differs from filename")
    text = offer["text"]
    normalized = "".join(str(unicodedata.decimal(c)) if c.isdecimal() else c for c in json.dumps(offer, ensure_ascii=False))
    for phone in PHONE.finditer(normalized):
        require(DEMO_PHONE.fullmatch(phone.group()) is not None, f"{filename}: non-demo phone")
    require(re.search(r"\bsafe\b", text, re.IGNORECASE) is None, f"{filename}: prohibited assurance")
    expected = offer["expected"]
    hits = set(expected["rule_hits"])
    verdict = "STOP" if hits & CRITICAL else "VERIFY_FIRST" if hits & HIGH else "NO_RED_FLAGS_FOUND"
    require(expected["verdict"] == verdict, f"{filename}: inconsistent verdict")
    facts = expected["facts"]
    derived = {
        "R1_TOURIST_VISA": facts["visa_type"] in {"tourist", "visit"},
        "R3_NO_RC_NUMBER": facts["agent_rc_number"] is None,
        "R4_FEE_OVER_CAP": facts["fees_demanded_inr"] is not None and int(facts["fees_demanded_inr"]) > 35400,
        "R6_HIGH_RISK_CORRIDOR": facts["destination_country"] in CORRIDORS and facts["role_title"].casefold() in ROLES,
    }
    for rule, hit in derived.items():
        require((rule in hits) == hit, f"{filename}: {rule} differs from facts")
    if offer["label"] == "legit_style":
        require(expected.get("ra_assumed_listed") is True, f"{filename}: missing listed-agent stub")
        require("R2_RA_NOT_LISTED" not in hits, f"{filename}: listed-agent stub conflicts with R2")
    else:
        require("ra_assumed_listed" not in expected, f"{filename}: unexpected listed-agent stub")
        if facts["agent_rc_number"] is not None:
            require("R2_RA_NOT_LISTED" in hits, f"{filename}: fictional licence must trigger R2")


def main():
    folder = Path(__file__).resolve().parent
    schema = load_json(folder / "schema.json")
    require(schema["$schema"] == "https://json-schema.org/draft/2020-12/schema", "Wrong schema draft")
    files = sorted(file for file in folder.glob("*.json") if file.name != "schema.json")
    require([file.name for file in files] == [f"{i:03}.json" for i in range(1, 41)], "Expected exactly 001.json through 040.json")
    offers = []
    for file in files:
        offer = load_json(file)
        check_offer(offer, schema, file.name)
        offers.append(offer)
    labels = Counter(offer["label"] for offer in offers)
    languages = Counter(offer["language"] for offer in offers)
    formats = Counter(offer["format"] for offer in offers)
    verdicts = Counter(offer["expected"]["verdict"] for offer in offers)
    require(labels == {"scam_pattern": 20, "legit_style": 20}, "Expected 20 offers per label")
    require(languages["hi"] >= 8 and languages["mr"] >= 6 and languages["hinglish"] >= 8, "Language minimums not met")
    require(set(formats) == {"whatsapp", "letter", "ad"}, "Missing a document format")
    legit_verdicts = Counter(offer["expected"]["verdict"] for offer in offers if offer["label"] == "legit_style")
    require(legit_verdicts == {"VERIFY_FIRST": 5, "NO_RED_FLAGS_FOUND": 15}, "Expected five legit-style near-misses")
    print(json.dumps({"offers": len(offers), "labels": labels, "languages": languages, "formats": formats, "verdicts": verdicts}, indent=2))
    print("PASS: all synthetic offer checks")


if __name__ == "__main__":
    main()
