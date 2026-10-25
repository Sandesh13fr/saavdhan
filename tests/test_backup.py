import io
import json
import sqlite3
import zipfile

import pytest
from cryptography.fernet import Fernet, InvalidToken
from scripts.backup import create_backup, restore_backup


def fixture_data(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    with sqlite3.connect(data / "bakaya.sqlite3") as database:
        database.execute("CREATE TABLE cases(id TEXT)")
        database.execute("INSERT INTO cases VALUES ('tenant-case')")
    evidence = data / "uploads" / "case" / "invoice.txt"
    evidence.parent.mkdir(parents=True)
    evidence.write_bytes(b"Synthetic evidence")
    return data


def test_encrypted_backup_restore_and_no_overwrite(tmp_path):
    data, key = fixture_data(tmp_path), Fernet.generate_key()
    backup, target = tmp_path / "snapshot.enc", tmp_path / "restored"
    manifest = create_backup(data, backup, key)
    assert b"Synthetic evidence" not in backup.read_bytes()
    assert restore_backup(backup, target, key) == manifest
    assert (target / "uploads/case/invoice.txt").read_bytes() == b"Synthetic evidence"
    with sqlite3.connect(target / "bakaya.sqlite3") as database:
        assert database.execute("SELECT id FROM cases").fetchone()[0] == "tenant-case"
    with pytest.raises(ValueError, match="must not exist"):
        restore_backup(backup, target, key)


def test_corrupt_cipher_and_hash_fail_without_target(tmp_path):
    key = Fernet.generate_key()
    backup = tmp_path / "snapshot.enc"
    create_backup(fixture_data(tmp_path), backup, key)
    cipher = backup.read_bytes()
    backup.write_bytes(cipher[:-10] + b"corruption")
    with pytest.raises(InvalidToken):
        restore_backup(backup, tmp_path / "bad", key)
    assert not (tmp_path / "bad").exists()

    original = zipfile.ZipFile(io.BytesIO(Fernet(key).decrypt(cipher)))
    changed = io.BytesIO()
    with zipfile.ZipFile(changed, "w") as bundle:
        for name in original.namelist():
            value = original.read(name)
            if name == "manifest.json":
                manifest = json.loads(value)
                manifest["bakaya.sqlite3"]["sha256"] = "0" * 64
                value = json.dumps(manifest).encode()
            bundle.writestr(name, value)
    backup.write_bytes(Fernet(key).encrypt(changed.getvalue()))
    with pytest.raises(ValueError, match="hash mismatch"):
        restore_backup(backup, tmp_path / "bad", key)
    assert not (tmp_path / "bad").exists()


def test_backup_refuses_output_in_live_data(tmp_path):
    data, key = fixture_data(tmp_path), Fernet.generate_key()
    with pytest.raises(ValueError, match="outside"):
        create_backup(data, data / "backup.enc", key)


def test_restore_rejects_archive_path_traversal(tmp_path):
    key, payload = Fernet.generate_key(), io.BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr("bakaya.sqlite3", b"not a db")
        archive.writestr("../outside.txt", b"bad")
        import hashlib
        manifest = {name: {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)} for name, data in [("bakaya.sqlite3", b"not a db"), ("../outside.txt", b"bad")]}
        archive.writestr("manifest.json", json.dumps(manifest))
    backup = tmp_path / "malicious.enc"
    backup.write_bytes(Fernet(key).encrypt(payload.getvalue()))
    with pytest.raises(ValueError, match="Unsafe"):
        restore_backup(backup, tmp_path / "restored", key)
    assert not (tmp_path / "outside.txt").exists()
