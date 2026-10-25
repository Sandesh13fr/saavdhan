"""Safety net: check-in schedule, simulated alerts, packet itinerary. All synthetic aliases."""
import io
import zipfile
from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from backend import safety
from backend.exports import packet_zip
from backend.models import Contact, SafetyPlan

NOW = datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc)


def make_plan(contacts=None):
    return SafetyPlan(
        traveller_alias="Brother (demo)",
        contacts=contacts or [Contact(alias="Sister (demo)", channel="sms (demo)"),
                              Contact(alias="Uncle (demo)", channel="email (demo)")],
        itinerary=["Flight to Bangkok (demo)"],
        checkin_interval_hours=24,
    )


def fresh_state():
    state = {"alerts": []}
    safety.create_plan(state, make_plan(), NOW)
    return state


def test_create_plan_sets_last_checkin_and_resets_history():
    state = fresh_state()
    safety.checkin(state, "landed", NOW + timedelta(hours=1))
    safety.create_plan(state, make_plan(), NOW)
    assert state["safety"]["checkins"] == []
    assert state["safety"]["alerts"] == []
    assert state["safety"]["plan"]["last_checkin"] == NOW.isoformat()


def test_max_two_contacts_enforced():
    three = [Contact(alias=f"C{i} (demo)", channel="sms (demo)") for i in range(3)]
    with pytest.raises(ValidationError):
        make_plan(three)


def test_checkin_updates_last_checkin_and_truncates_note():
    state = fresh_state()
    later = NOW + timedelta(hours=3)
    safety.checkin(state, "x" * 300, later)
    assert state["safety"]["plan"]["last_checkin"] == later.isoformat()
    assert len(state["safety"]["checkins"]) == 1
    assert len(state["safety"]["checkins"][0]["note"]) == 280


def test_checkin_requires_plan():
    with pytest.raises(ValueError):
        safety.checkin({}, "hi", NOW)


def test_advance_clock_bounds():
    state = fresh_state()
    for bad in (0, -1, 721):
        with pytest.raises(ValueError):
            safety.advance_clock(state, bad)
    safety.advance_clock(state, 1)
    safety.advance_clock(state, 720)
    assert state["safety"]["clock_offset_hours"] == 721
    assert safety.simulated_now(state, NOW) == NOW + timedelta(hours=721)


def test_status_none_without_plan():
    assert safety.status({}, NOW) is None


def test_ok_due_missed_transitions():
    state = fresh_state()
    assert safety.status(state, NOW)["status"] == "ok"
    safety.advance_clock(state, 23)
    assert safety.status(state, NOW)["status"] == "ok"
    safety.advance_clock(state, 2)  # 25h: past due, inside 2h grace
    assert safety.status(state, NOW)["status"] == "due"
    safety.advance_clock(state, 1)  # 26h: grace over
    result = safety.status(state, NOW)
    assert result["status"] == "missed"
    assert result["next_due"] == (NOW + timedelta(hours=24)).isoformat()
    assert result["now"] == (NOW + timedelta(hours=26)).isoformat()


def test_one_alert_per_contact_per_missed_due_time():
    state = fresh_state()
    safety.advance_clock(state, 26)
    first = safety.status(state, NOW)
    second = safety.status(state, NOW)
    assert len(first["alerts"]) == 2
    assert len(second["alerts"]) == 2
    assert {a["to_alias"] for a in second["alerts"]} == {"Sister (demo)", "Uncle (demo)"}
    for alert in second["alerts"]:
        assert alert["simulated"] is True
        assert alert["message_key"] == "family.alert_body"
        assert alert["due"] == (NOW + timedelta(hours=24)).isoformat()


def test_checkin_after_missed_clears_and_later_miss_alerts_again():
    state = fresh_state()
    safety.advance_clock(state, 26)
    assert len(safety.status(state, NOW)["alerts"]) == 2
    safety.checkin(state, "safe at hostel? no, just checking in", NOW)
    assert safety.status(state, NOW)["status"] == "ok"
    safety.advance_clock(state, 27)  # next due at 50h, now 53h: missed
    result = safety.status(state, NOW)
    assert result["status"] == "missed"
    assert len(result["alerts"]) == 4
    new = [a for a in result["alerts"] if a["due"] == (NOW + timedelta(hours=50)).isoformat()]
    assert len(new) == 2


def test_status_is_json_serialisable():
    import json
    state = fresh_state()
    safety.advance_clock(state, 26)
    json.dumps(safety.status(state, NOW))


def read_zip(view):
    with zipfile.ZipFile(io.BytesIO(packet_zip(view))) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def test_packet_includes_itinerary_when_safety_present():
    state = fresh_state()
    safety.advance_clock(state, 26)
    view = {"sources": [], "analysis": None, "safety": safety.status(state, NOW)}
    files = read_zip(view)
    assert "itinerary-and-checkins.txt" in files
    text = files["itinerary-and-checkins.txt"].decode("utf-8")
    assert "Brother (demo)" in text
    assert "Sister (demo) via sms (demo)" in text
    assert "Flight to Bangkok (demo)" in text
    assert "every 24 hours" in text
    assert "SIMULATED" in text
    assert files["summary.pdf"].startswith(b"%PDF")


def test_packet_omits_itinerary_when_safety_absent():
    files = read_zip({"sources": [], "analysis": None})
    assert "itinerary-and-checkins.txt" not in files
    assert "summary.pdf" in files
