"""Server-provisioned users and revocable, tenant-bound cookie sessions."""
import argparse
from contextvars import ContextVar
import getpass
import hashlib
import hmac
import os
import secrets
import time
import uuid

from fastapi import HTTPException
from . import storage

USER = ContextVar("bakaya_user", default=None)
SESSION_SECONDS = 8 * 60 * 60


def production():
    return os.getenv("BAKAYA_ENV", "local") != "local"


def database():
    conn = storage.connect()
    conn.execute("CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT NOT NULL, tenant_id TEXT NOT NULL, role TEXT NOT NULL, salt TEXT NOT NULL, password TEXT NOT NULL)")
    conn.execute("CREATE TABLE IF NOT EXISTS sessions (digest TEXT PRIMARY KEY, user_id TEXT NOT NULL, csrf TEXT NOT NULL, expires REAL NOT NULL)")
    conn.execute("CREATE TABLE IF NOT EXISTS login_attempts (email TEXT PRIMARY KEY, failures INTEGER NOT NULL, until REAL NOT NULL)")
    conn.commit()
    return conn


def password_hash(password, salt):
    return hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()


def provision(email, name, tenant, role, password):
    if role not in {"viewer", "editor", "reviewer", "admin"} or not tenant.strip() or tenant.strip() == "local-demo" or not name.strip() or "@" not in email or not 12 <= len(password) <= 1024:
        raise ValueError("Valid email, name, tenant, role and a password of at least 12 characters are required")
    salt = secrets.token_hex(16)
    with database() as conn:
        conn.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)", (uuid.uuid4().hex, email.strip().lower(), name.strip(), tenant.strip(), role, salt, password_hash(password, salt)))


def public_user(row):
    return dict(zip(("id", "email", "name", "tenant_id", "role"), row[:5]))


def session(token):
    if not token:
        return None
    with database() as conn:
        row = conn.execute("SELECT u.id,u.email,u.name,u.tenant_id,u.role,s.csrf FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.digest=? AND s.expires>?", (hashlib.sha256(token.encode()).hexdigest(), time.time())).fetchone()
    return {"user": public_user(row), "csrf_token": row[5]} if row else None


def login(email, password, ip="unknown"):
    email = email.strip().lower()
    if len(email) > 254 or len(password) > 1024:
        raise HTTPException(401, "Invalid credentials")
    with database() as conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM login_attempts WHERE until<=?",(time.time(),))
        ip_key="ip:" + ip
        ip_attempt=conn.execute("SELECT failures,until FROM login_attempts WHERE email=?", (ip_key,)).fetchone()
        if ip_attempt and ip_attempt[0]>=20 and ip_attempt[1]>time.time():
            raise HTTPException(429, "Too many login attempts; try again in 15 minutes")
        attempt = conn.execute("SELECT failures,until FROM login_attempts WHERE email=?", (email,)).fetchone()
        if attempt and attempt[0] >= 5 and attempt[1] > time.time():
            raise HTTPException(429, "Too many login attempts; try again in 15 minutes")
        row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        valid = hmac.compare_digest(password_hash(password, row[5] if row else "00" * 16), row[6] if row else "00" * 64)
        if not row or not valid:
            count = attempt[0] + 1 if attempt and attempt[1] > time.time() else 1
            conn.execute("INSERT OR REPLACE INTO login_attempts VALUES (?,?,?)", (email, count, time.time() + 900))
            ip_count=ip_attempt[0]+1 if ip_attempt and ip_attempt[1]>time.time() else 1
            conn.execute("INSERT OR REPLACE INTO login_attempts VALUES (?,?,?)", (ip_key,ip_count,time.time()+900))
            conn.commit()
            raise HTTPException(401, "Invalid credentials")
        conn.execute("DELETE FROM login_attempts WHERE email=?", (email,))
        conn.execute("DELETE FROM sessions WHERE expires<=?", (time.time(),))
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        conn.execute("DELETE FROM sessions WHERE user_id=? AND digest NOT IN (SELECT digest FROM sessions WHERE user_id=? ORDER BY expires DESC LIMIT 4)",(row[0],row[0]))
        conn.execute("INSERT INTO sessions VALUES (?,?,?,?)", (hashlib.sha256(token.encode()).hexdigest(), row[0], csrf, time.time() + SESSION_SECONDS))
    return token, {"authenticated": True, "local_demo": False, "user": public_user(row), "csrf_token": csrf}


def external_calls_allowed():
    user=USER.get()
    return not production() or bool(user and user["role"] == "admin")


def require_role(*roles):
    user = USER.get()
    if user and user["role"] not in roles:
        raise HTTPException(403, "Your account does not have permission for this action")
    return user


def reset_password(email, password):
    if not 12 <= len(password) <= 1024:
        raise ValueError("Password must contain 12 to 1024 characters")
    salt=secrets.token_hex(16)
    with database() as conn:
        row=conn.execute("SELECT id FROM users WHERE email=?",(email.strip().lower(),)).fetchone()
        if not row:
            raise ValueError("Account not found")
        conn.execute("UPDATE users SET salt=?,password=? WHERE id=?",(salt,password_hash(password,salt),row[0]))
        conn.execute("DELETE FROM sessions WHERE user_id=?",(row[0],))
        conn.execute("DELETE FROM login_attempts WHERE email=?",(email.strip().lower(),))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Provision an account; tenant membership is assigned by the server operator")
    parser.add_argument("command", choices=["create-user", "reset-password"])
    for field in ("email", "name", "tenant", "role"):
        parser.add_argument("--" + field, required=field=="email")
    args = parser.parse_args()
    password = getpass.getpass("Password (12+ characters): ")
    if password != getpass.getpass("Confirm password: "):
        raise SystemExit("Passwords differ")
    if args.command == "create-user":
        if not all((args.name,args.tenant,args.role)):
            parser.error("create-user requires --name, --tenant and --role")
        provision(args.email, args.name, args.tenant, args.role, password)
        print("Account created")
    else:
        reset_password(args.email,password)
        print("Password reset and all account sessions revoked")
