"""Unit tests for env_vault.vault module."""

import json
import pytest
from pathlib import Path
from env_vault.vault import Vault

PASSPHRASE = "vault-test-passphrase"


@pytest.fixture
def tmp_vault(tmp_path):
    vault = Vault(path=str(tmp_path / "test-vault.json"))
    return vault


def test_set_and_get(tmp_vault):
    tmp_vault.set("DB_PASSWORD", "secret123", PASSPHRASE)
    assert tmp_vault.get("DB_PASSWORD", PASSPHRASE) == "secret123"


def test_get_missing_key_raises(tmp_vault):
    with pytest.raises(KeyError):
        tmp_vault.get("NONEXISTENT", PASSPHRASE)


def test_list_keys(tmp_vault):
    tmp_vault.set("KEY_A", "val_a", PASSPHRASE)
    tmp_vault.set("KEY_B", "val_b", PASSPHRASE)
    keys = tmp_vault.list_keys()
    assert set(keys) == {"KEY_A", "KEY_B"}


def test_delete_key(tmp_vault):
    tmp_vault.set("TO_DELETE", "value", PASSPHRASE)
    tmp_vault.delete("TO_DELETE")
    assert "TO_DELETE" not in tmp_vault.list_keys()


def test_delete_missing_key_raises(tmp_vault):
    with pytest.raises(KeyError):
        tmp_vault.delete("GHOST_KEY")


def test_version_history(tmp_vault):
    tmp_vault.set("API_KEY", "v1", PASSPHRASE)
    tmp_vault.set("API_KEY", "v2", PASSPHRASE)
    tmp_vault.set("API_KEY", "v3", PASSPHRASE)
    hist = tmp_vault.history("API_KEY", PASSPHRASE)
    assert len(hist) == 3
    assert [h["value"] for h in hist] == ["v1", "v2", "v3"]


def test_save_and_load(tmp_vault):
    tmp_vault.set("SECRET", "hello", PASSPHRASE)
    tmp_vault.save()
    new_vault = Vault(path=str(tmp_vault.path))
    new_vault.load()
    assert new_vault.get("SECRET", PASSPHRASE) == "hello"


def test_saved_file_is_valid_json(tmp_vault):
    tmp_vault.set("X", "y", PASSPHRASE)
    tmp_vault.save()
    with open(tmp_vault.path) as fh:
        data = json.load(fh)
    assert "entries" in data
    assert "version" in data
