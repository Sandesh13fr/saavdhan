import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend import auth, storage

@pytest.fixture
def secure(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, 'DATA_DIR', tmp_path)
    monkeypatch.setenv('BAKAYA_ENV', 'production')
    monkeypatch.setenv('BAKAYA_PUBLIC_ORIGIN', 'https://testserver')
    auth.provision('a@example.com', 'Actual reviewer', 'tenant-a', 'reviewer', 'a long password 123')
    auth.provision('b@example.com', 'Other reviewer', 'tenant-b', 'reviewer', 'b long password 123')
    auth.provision('e@example.com', 'Editor', 'tenant-a', 'editor', 'e long password 123')
    return TestClient(app, base_url='https://testserver')

def login(client, email, password):
    result=client.post('/api/auth/login',json={'email':email,'password':password},headers={'Origin':'https://testserver'})
    assert result.status_code==200
    client.headers['X-CSRF-Token']=result.json()['csrf_token']
    return result

def test_session_csrf_expiry_logout_and_cookie(secure):
    assert secure.get('/api/cases').status_code==401
    result=login(secure,'a@example.com','a long password 123')
    cookie=result.headers['set-cookie']
    assert 'HttpOnly' in cookie and 'Secure' in cookie and 'SameSite=strict' in cookie
    secure.headers.pop('X-CSRF-Token')
    assert secure.post('/api/cases/demo').status_code==403
    secure.headers['X-CSRF-Token']=result.json()['csrf_token']
    assert secure.post('/api/cases/demo',headers={'Origin':'https://evil.example'}).status_code==403
    assert secure.post('/api/auth/logout').status_code==200
    assert secure.get('/api/cases').status_code==401
    login(secure,'a@example.com','a long password 123')
    with auth.database() as conn:
        conn.execute('UPDATE sessions SET expires=0')
    assert secure.get('/api/cases').status_code==401

def test_tenant_isolation_all_case_surfaces_and_actual_reviewer(secure):
    login(secure,'a@example.com','a long password 123')
    case=secure.post('/api/cases/demo').json(); cid=case['id']
    review={'reviewer':'Spoofed name','rate_confirmed':True,'buyer_confirmed':True,'resolutions':[{'payment_id':'PAY-003','source_id':'REMIT-003','reason':'Confirmed remittance note INV-004','allocations':[{'invoice_id':'INV-004','amount':'150000.00','tds_amount':'0'}]}]}
    assert secure.patch(f'/api/cases/{cid}/review',json=review).status_code==200
    result=secure.post(f'/api/cases/{cid}/approve',json={'reviewer':'Spoofed name'})
    assert result.status_code==200 and result.json()['approval']['reviewer']=='Actual reviewer'
    login(secure,'b@example.com','b long password 123')
    assert secure.get('/api/cases').json()==[]
    for tail in ('','/sources/REMIT-003','/sources/REMIT-003/download','/export','/agent'):
        assert secure.get(f'/api/cases/{cid}'+tail).status_code==404
    for tail in ('/agent/run','/agent/resume','/buyer-context','/run'):
        assert secure.post(f'/api/cases/{cid}'+tail,json=({'domain':'stripe.com','confirm':True} if tail=='/buyer-context' else {})).status_code==404
    login(secure,'e@example.com','e long password 123')
    assert secure.post(f'/api/cases/{cid}/approve',json={'reviewer':'Spoof'}).status_code==403

def test_legacy_demo_and_storage_collision_are_isolated(secure):
    with storage.connect() as conn:
        conn.execute("INSERT INTO cases(id,payload) VALUES ('legacy','{}')")
    login(secure,'a@example.com','a long password 123')
    assert secure.get('/api/cases/legacy').status_code==404
    token=storage.TENANT.set('tenant-a')
    try:
        with pytest.raises(PermissionError):
            storage.save_case({'id':'legacy'})
    finally:
        storage.TENANT.reset(token)

def test_password_login_throttling(secure):
    for _ in range(5):
        assert secure.post('/api/auth/login',json={'email':'a@example.com','password':'wrong'},headers={'Origin':'https://testserver'}).status_code==401
    assert secure.post('/api/auth/login',json={'email':'a@example.com','password':'a long password 123'},headers={'Origin':'https://testserver'}).status_code==429


def test_viewer_logout_and_security_headers(secure, monkeypatch):
    auth.provision('v@example.com','Viewer','tenant-a','viewer','v long password 123')
    login(secure,'v@example.com','v long password 123')
    assert secure.post('/api/cases/demo').status_code==403
    monkeypatch.setenv('BAKAYA_ENV','local')
    assert secure.get('/api/demo').status_code==405
    monkeypatch.setenv('BAKAYA_ENV','production')
    result=secure.get('/api/auth/me')
    assert result.headers['x-content-type-options']=='nosniff'
    assert "frame-ancestors 'none'" in result.headers['content-security-policy']
    assert result.headers['strict-transport-security']=='max-age=31536000'
    assert secure.post('/api/auth/logout').status_code==200

def test_ip_throttle_and_password_reset_revoke(secure):
    login(secure,'a@example.com','a long password 123')
    auth.reset_password('a@example.com','replacement password 123')
    assert secure.get('/api/cases').status_code==401
    login(secure,'a@example.com','replacement password 123')
    for n in range(20):
        assert secure.post('/api/auth/login',json={'email':f'missing{n}@example.com','password':'wrong'},headers={'Origin':'https://testserver'}).status_code==401
    assert secure.post('/api/auth/login',json={'email':'new@example.com','password':'wrong'},headers={'Origin':'https://testserver'}).status_code==429


def test_database_context_closes_and_preserves_transactions(secure):
    import sqlite3
    with storage.connect() as conn:
        conn.execute("INSERT INTO cases(id,payload) VALUES ('committed','{}')")
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute('SELECT 1')
    with pytest.raises(ValueError):
        with storage.connect() as rolled_back:
            rolled_back.execute("INSERT INTO cases(id,payload) VALUES ('rolled-back','{}')")
            raise ValueError('rollback')
    with pytest.raises(sqlite3.ProgrammingError):
        rolled_back.execute('SELECT 1')
    with storage.connect() as fresh:
        assert fresh.execute("SELECT id FROM cases WHERE id IN ('committed','rolled-back')").fetchall()==[('committed',)]


def test_paid_calls_admin_only_and_approval_identity(secure,monkeypatch):
    from backend import providers, enrichment
    monkeypatch.setenv('BAKAYA_ENABLE_LLM','true')
    monkeypatch.setenv('LITELLM_API_KEY','test-non-secret')
    login(secure,'a@example.com','a long password 123')
    assert secure.get('/api/auth/me').json()['external_calls_allowed'] is False
    case=secure.post('/api/cases/demo').json()
    monkeypatch.setattr(enrichment,'lookup',lambda *args: pytest.fail('Paid lookup attempted'))
    assert secure.post(f"/api/cases/{case['id']}/buyer-context",json={'domain':'stripe.com','confirm':True}).status_code==403
    assert secure.post(f"/api/cases/{case['id']}/agent/run",json={'allow_model_planning':True}).status_code==403
    token=auth.USER.set({'role':'reviewer'})
    try:
        assert not providers.provider_available()
    finally:
        auth.USER.reset(token)
    token=auth.USER.set({'role':'admin'})
    try:
        assert providers.provider_available()
    finally:
        auth.USER.reset(token)


def test_tenant_capacity_and_original_metadata(secure):
    from backend.fixtures import demo_case
    login(secure,'a@example.com','a long password 123')
    payload=demo_case().model_dump(mode='json')
    payload['sources'][0]['stored_name']='server-secret.sqlite3'
    payload['sources'][0]['sha256']='forgedhash'
    created=secure.post('/api/cases',json=payload)
    assert created.status_code==200
    assert created.json()['sources'][0]['stored_name'] is None
    assert created.json()['sources'][0]['sha256']==''
    for _ in range(9):
        assert secure.post('/api/cases/demo').status_code==200
    assert secure.post('/api/cases/demo').status_code==413
    token=storage.TENANT.set('tenant-a')
    try:
        storage.reserve_upload_bytes(49*1024*1024)
        with pytest.raises(storage.TenantCapacityExceeded):
            storage.reserve_upload_bytes(2*1024*1024)
    finally:
        storage.TENANT.reset(token)


def test_active_sessions_are_bounded(secure):
    for _ in range(8):
        login(secure,'a@example.com','a long password 123')
    with auth.database() as conn:
        assert conn.execute('SELECT count(*) FROM sessions').fetchone()[0]==5


def test_environment_typo_fails_closed(secure,monkeypatch):
    monkeypatch.setenv('BAKAYA_ENV','prodution')
    assert secure.get('/api/cases').status_code==401
    with pytest.raises(RuntimeError,match='BAKAYA_ENV'):
        with TestClient(app,base_url='https://testserver'):
            pass


def test_source_text_and_audit_caps_fail_closed(secure):
    from backend.models import SourceRef
    from pydantic import ValidationError
    with pytest.raises(ValidationError,match='200000'):
        SourceRef(id='large',file='large.txt',kind='invoice',text='x'*200001)
    token=storage.TENANT.set('tenant-a')
    try:
        with pytest.raises(storage.TenantCapacityExceeded):
            storage.save_case({'id':'too-many-events','audit':[{}]*1001})
        assert storage.get_case('too-many-events') is None
    finally:
        storage.TENANT.reset(token)
    rejected=secure.get('/api/cases')
    assert rejected.status_code==401
    assert rejected.headers['cache-control']=='no-store'
    assert rejected.headers['x-content-type-options']=='nosniff'
