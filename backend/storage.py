from __future__ import annotations

import json
import os
import shutil
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from contextvars import ContextVar

ANONYMOUS = "local-demo"
TENANT = ContextVar("saavdhan_tenant", default=ANONYMOUS)

DATA_DIR = Path(os.getenv("SAAVDHAN_DATA_DIR", Path(__file__).resolve().parents[1] / "data"))


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()


def connect():
    DATA_DIR.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(DATA_DIR/"saavdhan.sqlite3",timeout=15,factory=ClosingConnection)
    conn.execute("CREATE TABLE IF NOT EXISTS cases (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
    columns={row[1] for row in conn.execute("PRAGMA table_info(cases)")}
    if "tenant_id" not in columns:
        try:
            conn.execute("ALTER TABLE cases ADD COLUMN tenant_id TEXT NOT NULL DEFAULT 'local-demo'")
            conn.commit()
        except sqlite3.OperationalError:
            if "tenant_id" not in {row[1] for row in conn.execute("PRAGMA table_info(cases)")}:
                raise
    return conn


class ConcurrentCaseUpdate(RuntimeError):
    pass


class TenantCapacityExceeded(RuntimeError):
    pass


def reserve_upload_bytes(size):
    # Reservations are retained on failed writes; operator review is required to reclaim capacity.
    if os.getenv("SAAVDHAN_ENV") != "production":
        return
    if TENANT.get() == ANONYMOUS:
        # Recomputed from disk each time, so purged anonymous cases free their space.
        with connect() as conn:
            ids = [row[0] for row in conn.execute("SELECT id FROM cases WHERE tenant_id=?", (ANONYMOUS,))]
        used = sum(f.stat().st_size for cid in ids for f in (DATA_DIR/"uploads"/cid).glob("*") if f.is_file())
        if used + size > int(os.getenv("SAAVDHAN_ANON_UPLOAD_MB", "500")) * 1024 * 1024:
            raise TenantCapacityExceeded("Upload capacity is full right now; paste the offer text or try later")
        return
    with connect() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS upload_budget (tenant_id TEXT PRIMARY KEY, bytes INTEGER NOT NULL)")
        conn.commit()
        conn.execute("BEGIN IMMEDIATE")
        row=conn.execute("SELECT bytes FROM upload_budget WHERE tenant_id=?",(TENANT.get(),)).fetchone()
        if row:
            used=row[0]
        else:
            ids=[item[0] for item in conn.execute("SELECT id FROM cases WHERE tenant_id=?",(TENANT.get(),))]
            used=sum(file.stat().st_size for case_id in ids for file in (DATA_DIR/"uploads"/case_id).glob("*") if file.is_file())
        if used+size>50*1024*1024:
            raise TenantCapacityExceeded("Tenant upload capacity reached (50 MiB); contact the operator")
        conn.execute("INSERT INTO upload_budget VALUES (?,?) ON CONFLICT(tenant_id) DO UPDATE SET bytes=excluded.bytes",(TENANT.get(),used+size))


def save_case(case: dict, expected_revision: int | None = None):
    if os.getenv("SAAVDHAN_ENV", "local") != "local" and len(case.get("audit",[]))>1000:
        raise TenantCapacityExceeded("Case audit capacity reached (1000 events); contact the operator")
    with connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        if expected_revision is not None:
            row=conn.execute("SELECT payload FROM cases WHERE id=? AND tenant_id=?",(case["id"],TENANT.get())).fetchone()
            if not row or json.loads(row[0])["revision"]!=expected_revision:
                raise ConcurrentCaseUpdate("Case changed while agent was working; resume against latest reviewer decisions")
        existing=conn.execute("SELECT tenant_id FROM cases WHERE id=?",(case["id"],)).fetchone()
        if not existing and os.getenv("SAAVDHAN_ENV") == "production" and TENANT.get() != ANONYMOUS and conn.execute("SELECT count(*) FROM cases WHERE tenant_id=?",(TENANT.get(),)).fetchone()[0]>=10:
            raise TenantCapacityExceeded("Tenant case capacity reached (10); contact the operator")
        if existing and existing[0]!=TENANT.get():
            raise PermissionError("Case belongs to another tenant")
        updated=conn.execute("INSERT INTO cases(id,payload,tenant_id) VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload WHERE cases.tenant_id=excluded.tenant_id",(case["id"],json.dumps(case),TENANT.get()))
        if not updated.rowcount:
            raise PermissionError("Case belongs to another tenant")


def get_case(case_id: str):
    with connect() as conn:
        row=conn.execute("SELECT payload FROM cases WHERE id=? AND tenant_id=?",(case_id,TENANT.get())).fetchone()
    return json.loads(row[0]) if row else None


def list_cases():
    with connect() as conn:
        rows=conn.execute("SELECT payload FROM cases WHERE tenant_id=? ORDER BY rowid DESC",(TENANT.get(),)).fetchall()
    return [json.loads(row[0]) for row in rows]


def purge_anonymous(max_age_hours: float, keep: int | None = None):
    """Delete expired anonymous cases, also enforcing `keep` when provided."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=max_age_hours)).isoformat()
    with connect() as conn:
        rows = conn.execute("SELECT id, payload FROM cases WHERE tenant_id=? ORDER BY rowid DESC", (ANONYMOUS,)).fetchall()
        doomed = [cid for n, (cid, payload) in enumerate(rows) if (keep is not None and n >= keep) or json.loads(payload).get("created_at", "") < cutoff]
        conn.executemany("DELETE FROM cases WHERE id=? AND tenant_id=?", [(cid, ANONYMOUS) for cid in doomed])
    for cid in doomed:
        shutil.rmtree(DATA_DIR / "uploads" / cid, ignore_errors=True)
    return len(doomed)


def upload_dir(case_id):
    # IDs are created by server and validated on API lookup.
    path=DATA_DIR/"uploads"/case_id
    path.mkdir(parents=True,exist_ok=True)
    return path
