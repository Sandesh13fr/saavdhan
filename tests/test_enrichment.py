import json
import pytest
from fastapi.testclient import TestClient
from backend import enrichment, storage
from backend.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    monkeypatch.setenv("CRUSTDATA_API_KEY", "test-only")
    return TestClient(app)


def fake_tool(name, arguments):
    if name == "crustdata_credit_costs":
        return "`crustdata_company_enrich_v2` | Any field groups | 2 credits / company"
    return json.dumps([{"matches":[{"company_data":{"crustdata_company_id":123,"basic_info":{"name":"Sample buyer","primary_domain":"example.com"}}}]}]) + "\n\n_credits: spent 2.0 this call"


def test_cache_separate_from_claim_and_approval(client, monkeypatch):
    calls=[]
    def call(name,args):
        calls.append(name)
        return fake_tool(name,args)
    monkeypatch.setattr(enrichment,"tool",call)
    case=client.post('/api/cases/demo').json()
    before=storage.get_case(case['id'])
    path=f"/api/cases/{case['id']}/buyer-context"
    response=client.post(path,json={"domain":"example.com","confirm":True})
    assert response.status_code == 200
    assert response.json()['buyer_context']['credits_reserved'] == 2
    assert storage.get_case(case['id']) == before
    assert client.post(path,json={"domain":"example.com","confirm":True}).status_code == 200
    assert len(calls)==3
    assert client.get(f"/api/cases/{case['id']}").json()['buyer_context']['result']['context']['name']=='Sample buyer'


def test_budget_and_unverified_cost_stop_calls(client, monkeypatch):
    monkeypatch.setattr(enrichment,"tool",lambda *args: (_ for _ in ()).throw(ValueError('secret-provider-error')))
    case=client.post('/api/cases/demo').json()
    path=f"/api/cases/{case['id']}/buyer-context"
    failed=client.post(path,json={"domain":"example.com","confirm":True})
    assert failed.status_code==502 and 'secret-provider-error' not in failed.text
    assert client.post(path,json={"domain":"other.com","confirm":True}).status_code==409


@pytest.mark.parametrize('failure',['price','cost','ambiguous'])
def test_provider_changes_fail_closed(client,monkeypatch,failure):
    def call(name,args):
        if failure=='price' and name=='crustdata_credit_costs':
            return 'price now 5 credits'
        if failure=='cost' and name=='crustdata_company_enrich_v2':
            return fake_tool(name,args).split('\n\n_credits:')[0]
        if failure=='ambiguous' and name=='crustdata_company_identify_v2':
            return '[{"matches":[]}]'
        return fake_tool(name,args)
    monkeypatch.setattr(enrichment,'tool',call)
    case=client.post('/api/cases/demo').json()
    response=client.post(f"/api/cases/{case['id']}/buyer-context",json={"domain":"example.com","confirm":True})
    assert response.status_code==502
    status=enrichment.read(case['id'])
    assert status['blocked'] and status['credits_reserved']==2 and status['result'] is None
    with enrichment.database() as conn:
        conn.execute('UPDATE enrichment_budget SET reserved=500,blocked=0')
    assert client.post(f"/api/cases/{case['id']}/buyer-context",json={"domain":"other.com","confirm":True}).status_code==409


@pytest.mark.parametrize('body',[{"domain":"http://localhost/private","confirm":True},{"domain":"example.com"},{"domain":['example.com'],"confirm":True}])
def test_lookup_requires_domain_and_confirmation(client,body):
    case=client.post('/api/cases/demo').json()
    assert client.post(f"/api/cases/{case['id']}/buyer-context",json=body).status_code==422
    assert enrichment.read(case['id'])['credits_reserved']==0
