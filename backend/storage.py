from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from contextvars import ContextVar

TENANT = ContextVar("bakaya_tenant", default="local-demo")

DATA_DIR = Path(os.getenv("BAKAYA_DATA_DIR", Path(__file__).resolve().parents[1] / "data"))


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()


def connect():
    DATA_DIR.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(DATA_DIR/"bakaya.sqlite3",timeout=15,factory=ClosingConnection)
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
    if os.getenv("BAKAYA_ENV") != "production":
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
    if os.getenv("BAKAYA_ENV", "local") != "local" and len(case.get("audit",[]))>1000:
        raise TenantCapacityExceeded("Case audit capacity reached (1000 events); contact the operator")
    with connect() as conn:
        conn.execute("BEGIN IMMEDIATE")
        if expected_revision is not None:
            row=conn.execute("SELECT payload FROM cases WHERE id=? AND tenant_id=?",(case["id"],TENANT.get())).fetchone()
            if not row or json.loads(row[0])["revision"]!=expected_revision:
                raise ConcurrentCaseUpdate("Case changed while agent was working; resume against latest reviewer decisions")
        existing=conn.execute("SELECT tenant_id FROM cases WHERE id=?",(case["id"],)).fetchone()
        if not existing and os.getenv("BAKAYA_ENV") == "production" and conn.execute("SELECT count(*) FROM cases WHERE tenant_id=?",(TENANT.get(),)).fetchone()[0]>=10:
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


def upload_dir(case_id):
    # IDs are created by server and validated on API lookup.
    path=DATA_DIR/"uploads"/case_id
    path.mkdir(parents=True,exist_ok=True)
    return path
