"""Family safety net: check-in schedule and simulated alerts.

Pure functions on the case state dict. No I/O, no network, no real messages:
alerts are SIMULATED records only. Times are timezone-aware UTC.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from backend.models import SafetyPlan

GRACE = timedelta(hours=2)
MAX_NOTE = 280
MAX_ADVANCE_HOURS = 720


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")
    return value.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return _utc(value).isoformat()


def _require(state: dict) -> dict:
    safety = state.get("safety")
    if not safety:
        raise ValueError("no safety plan for this case")
    return safety


def create_plan(state: dict, plan: SafetyPlan, now: datetime) -> None:
    # ponytail: replacing a plan wipes check-ins and alerts; no history kept.
    data = plan.model_dump(mode="json")
    data["last_checkin"] = _iso(now)
    state["safety"] = {"plan": data, "checkins": [], "clock_offset_hours": 0, "alerts": []}


def simulated_now(state: dict, real_now: datetime) -> datetime:
    offset = (state.get("safety") or {}).get("clock_offset_hours", 0)
    return _utc(real_now) + timedelta(hours=offset)


def checkin(state: dict, note: str, real_now: datetime) -> None:
    safety = _require(state)
    now = simulated_now(state, real_now)
    safety["checkins"].append({"at": _iso(now), "note": note[:MAX_NOTE]})
    safety["plan"]["last_checkin"] = _iso(now)


def advance_clock(state: dict, hours: int) -> None:
    # Demo only: moves the simulated clock so the schedule can be shown without waiting.
    if isinstance(hours, bool) or not isinstance(hours, int) or not 1 <= hours <= MAX_ADVANCE_HOURS:
        raise ValueError(f"hours must be an integer from 1 to {MAX_ADVANCE_HOURS}")
    safety = _require(state)
    safety["clock_offset_hours"] += hours


def status(state: dict, real_now: datetime) -> dict | None:
    safety = state.get("safety")
    if not safety:
        return None
    plan = safety["plan"]
    now = simulated_now(state, real_now)
    next_due = datetime.fromisoformat(plan["last_checkin"]) + timedelta(hours=plan["checkin_interval_hours"])
    if now < next_due:
        label = "ok"
    elif now < next_due + GRACE:
        label = "due"
    else:
        label = "missed"

    if label == "missed":
        due = _iso(next_due)
        # One alert per contact per missed due time; repeated status calls add nothing.
        sent = {(a["to_alias"], a["channel"]) for a in safety["alerts"] if a["due"] == due}
        for contact in plan["contacts"]:
            key = (contact["alias"], contact["channel"])
            if key not in sent:
                safety["alerts"].append({
                    "to_alias": contact["alias"],
                    "channel": contact["channel"],
                    "at": _iso(now),
                    "due": due,
                    "message_key": "family.alert_body",
                    "simulated": True,
                })
                sent.add(key)

    return {
        "plan": plan,
        "checkins": safety["checkins"],
        "status": label,
        "next_due": _iso(next_due),
        "now": _iso(now),
        "alerts": safety["alerts"],
    }
