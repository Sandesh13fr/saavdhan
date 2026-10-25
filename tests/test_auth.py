import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend import auth, storage

ORIGIN = {'Origin': 'https://testserver'}
MAP = '/api/reports/map'


@pytest.fixture
def secure(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, 'DATA_DIR', tmp_path)
    monkeypatch.setenv('SAAVDHAN_ENV', 'production')
    monkeypatch.setenv('SAAVDHAN_PUBLIC_ORIGIN', 'https://testserver')
    auth.provision('a@example.com', 'Officer A', 'tenant-a', 'reviewer', 'a long password 123')
    auth.provision('b@example.com', 'Officer B', 'tenant-b', 'reviewer', 'b long password 123')
    return TestClient(app, base_url='https://testserver')


def login(client, email, password):
    result = client.post('/api/auth/login', json={'email': email, 'password': password}, headers=ORIGIN)
    assert result.status_code == 200
    client.headers['X-CSRF-Token'] = result.json()['csrf_token']
    return result


def test_offer_check_needs_no_login_but_pattern_map_does(secure):
    assert secure.post('/api/offers', data={'text': 'Data entry job in Bangkok'}).status_code == 200
    assert secure.get(MAP).status_code == 401


def test_session_csrf_logout_and_cookie(secure):
    result = login(secure, 'a@example.com', 'a long password 123')
    cookie = result.headers['set-cookie']
    assert 'HttpOnly' in cookie and 'Secure' in cookie and 'SameSite=strict' in cookie
    assert secure.get(MAP).json()['synthetic'] is True
    secure.headers.pop('X-CSRF-Token')
    assert secure.post('/api/demo/offers/bangkok-data-entry').status_code == 403
    secure.headers['X-CSRF-Token'] = result.json()['csrf_token']
    assert secure.post('/api/demo/offers/bangkok-data-entry', headers={'Origin': 'https://evil.example'}).status_code == 403
    assert secure.post('/api/auth/logout').status_code == 200
    assert secure.get(MAP).status_code == 401


def test_tenant_isolation_of_offer_cases(secure):
    login(secure, 'a@example.com', 'a long password 123')
    cid = secure.post('/api/demo/offers/bangkok-data-entry').json()['id']
    sid = secure.get(f'/api/offers/{cid}').json()['sources'][0]['id']
    login(secure, 'b@example.com', 'b long password 123')
    for tail in ('', f'/sources/{sid}', f'/sources/{sid}/download', '/packet'):
        assert secure.get(f'/api/offers/{cid}' + tail).status_code == 404
    assert secure.post(f'/api/offers/{cid}/analyze').status_code == 404


def test_storage_collision_is_isolated(secure):
    with storage.connect() as conn:
        conn.execute("INSERT INTO cases(id,payload) VALUES ('legacy','{}')")
    login(secure, 'a@example.com', 'a long password 123')
    assert secure.get('/api/offers/legacy').status_code == 404
    token = storage.TENANT.set('tenant-a')
    try:
        with pytest.raises(PermissionError):
            storage.save_case({'id': 'legacy'})
    finally:
        storage.TENANT.reset(token)


def test_password_login_throttling(secure):
    for _ in range(5):
        assert secure.post('/api/auth/login', json={'email': 'a@example.com', 'password': 'wrong'}, headers=ORIGIN).status_code == 401
    assert secure.post('/api/auth/login', json={'email': 'a@example.com', 'password': 'a long password 123'}, headers=ORIGIN).status_code == 429


def test_viewer_is_read_only_and_security_headers(secure):
    auth.provision('v@example.com', 'Viewer', 'tenant-a', 'viewer', 'v long password 123')
    login(secure, 'v@example.com', 'v long password 123')
    assert secure.post('/api/demo/offers/bangkok-data-entry').status_code == 403
    result = secure.get('/api/auth/me')
    assert result.headers['x-content-type-options'] == 'nosniff'
    assert "frame-ancestors 'none'" in result.headers['content-security-policy']
    assert result.headers['strict-transport-security'] == 'max-age=31536000'
    assert secure.post('/api/auth/logout').status_code == 200


def test_ip_throttle_and_password_reset_revoke(secure):
    login(secure, 'a@example.com', 'a long password 123')
    auth.reset_password('a@example.com', 'replacement password 123')
    assert secure.get(MAP).status_code == 401
    login(secure, 'a@example.com', 'replacement password 123')
    for n in range(20):
        assert secure.post('/api/auth/login', json={'email': f'missing{n}@example.com', 'password': 'wrong'}, headers=ORIGIN).status_code == 401
    assert secure.post('/api/auth/login', json={'email': 'new@example.com', 'password': 'wrong'}, headers=ORIGIN).status_code == 429


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
    with storage.connect() as fresh:
        assert fresh.execute("SELECT id FROM cases WHERE id IN ('committed','rolled-back')").fetchall() == [('committed',)]


def test_paid_calls_admin_only(secure, monkeypatch):
    from backend import providers
    monkeypatch.setenv('SAAVDHAN_ENABLE_LLM', 'true')
    monkeypatch.setenv('LITELLM_API_KEY', 'test-non-secret')
    assert not providers.provider_available()  # anonymous visitor in production
    token = auth.USER.set({'role': 'reviewer'})
    try:
        assert not providers.provider_available()
    finally:
        auth.USER.reset(token)
    token = auth.USER.set({'role': 'admin'})
    try:
        assert providers.provider_available()
    finally:
        auth.USER.reset(token)


def test_tenant_capacity(secure):
    login(secure, 'a@example.com', 'a long password 123')
    for _ in range(10):
        assert secure.post('/api/demo/offers/dubai-near-miss').status_code == 200
    assert secure.post('/api/demo/offers/dubai-near-miss').status_code == 413
    token = storage.TENANT.set('tenant-a')
    try:
        storage.reserve_upload_bytes(49 * 1024 * 1024)
        with pytest.raises(storage.TenantCapacityExceeded):
            storage.reserve_upload_bytes(2 * 1024 * 1024)
    finally:
        storage.TENANT.reset(token)


def test_active_sessions_are_bounded(secure):
    for _ in range(8):
        login(secure, 'a@example.com', 'a long password 123')
    with auth.database() as conn:
        assert conn.execute('SELECT count(*) FROM sessions').fetchone()[0] == 5


def test_environment_typo_fails_closed(secure, monkeypatch):
    monkeypatch.setenv('SAAVDHAN_ENV', 'prodution')
    with pytest.raises(RuntimeError, match='SAAVDHAN_ENV'):
        with TestClient(app, base_url='https://testserver'):
            pass


def test_source_text_and_audit_caps_fail_closed(secure):
    from backend.models import SourceRef
    from pydantic import ValidationError
    with pytest.raises(ValidationError, match='200000'):
        SourceRef(id='large', file='large.txt', kind='offer', text='x' * 200001)
    token = storage.TENANT.set('tenant-a')
    try:
        with pytest.raises(storage.TenantCapacityExceeded):
            storage.save_case({'id': 'too-many-events', 'audit': [{}] * 1001})
        assert storage.get_case('too-many-events') is None
    finally:
        storage.TENANT.reset(token)
    rejected = secure.get(MAP)
    assert rejected.status_code == 401
    assert rejected.headers['cache-control'] == 'no-store'
    assert rejected.headers['x-content-type-options'] == 'nosniff'
