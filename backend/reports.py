"""Authority pattern map: anonymised reports aggregated by district. SYNTHETIC data only.

Raw phone numbers never leave this module: they are salted+hashed before aggregation.
"""
from __future__ import annotations

import hashlib
import os
import re
from collections import defaultdict
from datetime import datetime, timezone

from .models import Report


def phone_hash(phone: str) -> str:
    salt = os.getenv("SAAVDHAN_HASH_SALT", "local-demo-salt")
    return hashlib.sha256((salt + re.sub(r"\D", "", phone)).encode()).hexdigest()


def template_hash(text: str) -> str:
    """64-bit simhash over word 3-grams of normalised text; near-identical offers collide."""
    words = re.sub(r"[\d\W_]+", " ", text.casefold()).split()
    grams = [" ".join(words[i:i + 3]) for i in range(max(1, len(words) - 2))]
    weights = [0] * 64
    for gram in grams:
        h = int.from_bytes(hashlib.sha256(gram.encode()).digest()[:8], "big")
        for bit in range(64):
            weights[bit] += 1 if h >> bit & 1 else -1
    return format(sum(1 << b for b in range(64) if weights[b] > 0), "016x")


# Fictional numbers (+91 90000 0xxxx) and offer templates; districts get repeat patterns.
_TEMPLATES = {
    "bangkok": "Data entry job in Bangkok Thailand salary 1.2 lakh per month tourist visa processing fee pay by UPI",
    "cambodia": "Customer support job Cambodia free flight visa on arrival deposit 2 lakh confirm today",
    "dubai": "Electrician job Dubai employment visa service charge receipt contract signed",
}
_SYNTHETIC = [
    ("+919000000001", "bangkok", ["Pune", "Nashik", "Kolhapur", "Nagpur", "Thane"]),
    ("+919000000002", "cambodia", ["Mumbai", "Thane", "Palghar"]),
    ("+919000000003", "bangkok", ["Aurangabad", "Jalgaon"]),
    ("+919000000004", "dubai", ["Satara"]),
    ("+919000000005", "cambodia", ["Solapur"]),
    ("+919000000006", "bangkok", ["Pune", "Sangli"]),
    ("+919000000007", "dubai", ["Ratnagiri"]),
    ("+919000000008", "cambodia", ["Latur", "Nanded"]),
]


def synthetic_reports() -> list[Report]:
    at = datetime(2026, 10, 1, tzinfo=timezone.utc)
    return [Report(district=d, agent_phone_hash=phone_hash(phone), offer_template_hash=template_hash(_TEMPLATES[t]), created_at=at)
            for phone, t, districts in _SYNTHETIC for d in districts]


def aggregate(reports: list[Report]) -> dict:
    counts: dict[str, int] = defaultdict(int)
    by_agent: dict[str, set] = defaultdict(set)
    by_template: dict[str, set] = defaultdict(set)
    agent_n: dict[str, int] = defaultdict(int)
    template_n: dict[str, int] = defaultdict(int)
    for r in reports:
        counts[r.district] += 1
        by_agent[r.agent_phone_hash].add(r.district); agent_n[r.agent_phone_hash] += 1
        by_template[r.offer_template_hash].add(r.district); template_n[r.offer_template_hash] += 1
    return {
        "synthetic": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "districts": [{"district": d, "count": n} for d, n in sorted(counts.items())],
        "repeated_agents": sorted(({"agent_phone_hash": h, "districts": sorted(ds), "count": agent_n[h]}
                                   for h, ds in by_agent.items() if len(ds) > 1), key=lambda x: -len(x["districts"])),
        "repeated_templates": sorted(({"offer_template_hash": h, "districts": sorted(ds), "count": template_n[h]}
                                      for h, ds in by_template.items() if len(ds) > 1), key=lambda x: -len(x["districts"])),
    }
