"""Encrypted SQLite + evidence backup; restores only into a new directory."""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import sqlite3
import tempfile
import zipfile

from cryptography.fernet import Fernet

# shortcut: bounded in-memory archive for the pilot; use streaming backup before 128 MB.
MAX_BACKUP_BYTES = 128 * 1024 * 1024


def create_backup(data_dir: Path, output: Path, key: bytes):
    data_dir = data_dir.resolve()
    if output.exists() or output.resolve().is_relative_to(data_dir):
        raise ValueError("Backup output must be new and outside the live data directory")
    database = data_dir / "bakaya.sqlite3"
    if not database.is_file():
        raise ValueError("Database is missing")
    with tempfile.TemporaryDirectory() as temporary:
        snapshot = Path(temporary) / database.name
        with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as source, closing(sqlite3.connect(snapshot)) as target:
            source.backup(target)
            if target.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("Database integrity check failed")
        files = {database.name: snapshot.read_bytes()}
        for path in sorted(data_dir.rglob("*")):
            if path.is_symlink():
                raise ValueError("Symlinks are not permitted in a backup")
            if path.is_file() and path not in {database, Path(str(database) + "-wal"), Path(str(database) + "-shm"), Path(str(database) + "-journal")}:
                if sum(map(len, files.values())) + path.stat().st_size > MAX_BACKUP_BYTES:
                    raise ValueError("Backup exceeds 128 MB; use a streaming backup solution")
                files[path.relative_to(data_dir).as_posix()] = path.read_bytes()
        if sum(map(len, files.values())) > MAX_BACKUP_BYTES:
            raise ValueError("Backup exceeds 128 MB")
        manifest = {name: {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)} for name, data in files.items()}
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
            for name, data in files.items():
                bundle.writestr(name, data)
            bundle.writestr("manifest.json", json.dumps(manifest))
        encrypted = Fernet(key).encrypt(archive.getvalue())
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("xb") as destination:
            destination.write(encrypted)
        try:
            output.chmod(0o600)
        except OSError:
            pass
    return manifest


def restore_backup(backup: Path, target: Path, key: bytes):
    if target.exists():
        raise ValueError("Restore target must not exist; live data is never overwritten")
    if backup.stat().st_size > MAX_BACKUP_BYTES * 2:
        raise ValueError("Backup exceeds restore limit")
    decrypted = Fernet(key).decrypt(backup.read_bytes())
    with zipfile.ZipFile(io.BytesIO(decrypted)) as bundle:
        names = bundle.namelist()
        if len(names) != len(set(names)) or sum(x.file_size for x in bundle.infolist()) > MAX_BACKUP_BYTES:
            raise ValueError("Invalid or oversized archive")
        manifest = json.loads(bundle.read("manifest.json"))
        if set(names) != set(manifest) | {"manifest.json"} or "bakaya.sqlite3" not in manifest:
            raise ValueError("Archive manifest mismatch")
        files = {}
        for name, expected in manifest.items():
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
                raise ValueError("Unsafe archive path")
            data = bundle.read(name)
            if expected != {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}:
                raise ValueError("Backup hash mismatch")
            files[name] = data
    with tempfile.TemporaryDirectory(dir=target.parent) as temporary:
        staging = Path(temporary) / "restored"
        staging.mkdir()
        for name, data in files.items():
            destination = staging / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        with closing(sqlite3.connect(staging / "bakaya.sqlite3")) as database:
            if database.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("Restored database integrity failed")
        staging.rename(target)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["create", "restore"])
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    key = os.environ.get("BAKAYA_BACKUP_KEY", "").encode()
    Fernet(key)  # Validate the secret before touching any file.
    result = create_backup(args.source, args.target, key) if args.action == "create" else restore_backup(args.source, args.target, key)
    print(f"{args.action}: verified {len(result)} files")


if __name__ == "__main__":
    main()
