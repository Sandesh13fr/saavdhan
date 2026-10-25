import json

from backend.reports import aggregate, phone_hash, synthetic_reports, template_hash


def test_one_hashed_agent_across_five_districts_and_no_raw_numbers():
    data = aggregate(synthetic_reports())
    assert data["synthetic"] is True
    assert len(data["repeated_agents"][0]["districts"]) == 5
    assert "9000000" not in json.dumps(data)


def test_phone_hash_is_salted_and_format_insensitive(monkeypatch):
    assert phone_hash("+91 90000 00001") == phone_hash("+919000000001")
    before = phone_hash("+919000000001")
    monkeypatch.setenv("SAAVDHAN_HASH_SALT", "other")
    assert phone_hash("+919000000001") != before


def test_template_hash_tolerates_small_edits():
    a = template_hash("Data entry job in Bangkok Thailand salary 1.2 lakh per month tourist visa pay by UPI now")
    b = template_hash("Data entry job in Bangkok, Thailand. Salary 1.5 lakh per month, tourist visa, pay by UPI now")
    c = template_hash("Electrician job Dubai employment visa service charge receipt contract signed by all")
    dist = lambda x, y: bin(int(x, 16) ^ int(y, 16)).count("1")
    assert dist(a, b) < dist(a, c)
