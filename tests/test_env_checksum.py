"""Tests for env_vault.env_checksum."""
import pytest
from pathlib import Path
from env_vault.env_checksum import (
    record_checksum, get_checksum, remove_checksum,
    verify_checksum, verify_all, _compute,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_record_checksum_returns_hex_digest(vault_dir):
    digest = record_checksum(vault_dir, "KEY", "secret")
    assert isinstance(digest, str)
    assert len(digest) == 64  # sha256 hex


def test_record_checksum_matches_sha256(vault_dir):
    import hashlib
    digest = record_checksum(vault_dir, "KEY", "hello")
    expected = hashlib.sha256(b"hello").hexdigest()
    assert digest == expected


def test_get_checksum_returns_stored_value(vault_dir):
    record_checksum(vault_dir, "KEY", "value")
    stored = get_checksum(vault_dir, "KEY")
    assert stored == _compute("value")


def test_get_checksum_missing_key_returns_none(vault_dir):
    assert get_checksum(vault_dir, "MISSING") is None


def test_remove_checksum_returns_true_when_found(vault_dir):
    record_checksum(vault_dir, "KEY", "val")
    assert remove_checksum(vault_dir, "KEY") is True


def test_remove_checksum_returns_false_when_missing(vault_dir):
    assert remove_checksum(vault_dir, "GHOST") is False


def test_remove_checksum_deletes_entry(vault_dir):
    record_checksum(vault_dir, "KEY", "val")
    remove_checksum(vault_dir, "KEY")
    assert get_checksum(vault_dir, "KEY") is None


def test_verify_checksum_ok_when_value_unchanged(vault_dir):
    record_checksum(vault_dir, "KEY", "stable")
    result = verify_checksum(vault_dir, "KEY", "stable")
    assert result.tampered is False
    assert "OK" in str(result)


def test_verify_checksum_tampered_when_value_changed(vault_dir):
    record_checksum(vault_dir, "KEY", "original")
    result = verify_checksum(vault_dir, "KEY", "modified")
    assert result.tampered is True
    assert "TAMPERED" in str(result)


def test_verify_checksum_not_tampered_when_no_record(vault_dir):
    result = verify_checksum(vault_dir, "NEW_KEY", "anything")
    assert result.tampered is False
    assert result.expected is None


def test_verify_all_returns_empty_when_no_checksums(vault_dir):
    results = verify_all(vault_dir, {"KEY": "val"})
    assert results == []


def test_verify_all_detects_tampered_key(vault_dir):
    record_checksum(vault_dir, "A", "original")
    record_checksum(vault_dir, "B", "stable")
    results = verify_all(vault_dir, {"A": "changed", "B": "stable"})
    tampered = [r for r in results if r.tampered]
    ok = [r for r in results if not r.tampered]
    assert len(tampered) == 1
    assert tampered[0].key == "A"
    assert len(ok) == 1
    assert ok[0].key == "B"


def test_verify_all_missing_key_in_values_treated_as_empty(vault_dir):
    record_checksum(vault_dir, "KEY", "nonempty")
    results = verify_all(vault_dir, {})
    assert results[0].tampered is True
