"""Tests for env_vault.snapshot."""

import json
import time
from pathlib import Path

import pytest

from env_vault.snapshot import (
    create_snapshot,
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
)


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    vault_file = tmp_path / "vault.json"
    vault_file.write_text(
        json.dumps({"KEY_A": "enc_a", "KEY_B": "enc_b"}), encoding="utf-8"
    )
    return tmp_path


def test_create_snapshot_returns_path(vault_dir: Path) -> None:
    path = create_snapshot(str(vault_dir))
    assert path.exists()
    assert path.suffix == ".json"


def test_create_snapshot_with_label(vault_dir: Path) -> None:
    path = create_snapshot(str(vault_dir), label="before-deploy")
    assert "before-deploy" in path.name


def test_create_snapshot_no_vault_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        create_snapshot(str(tmp_path))


def test_snapshot_contains_vault_data(vault_dir: Path) -> None:
    path = create_snapshot(str(vault_dir))
    meta = json.loads(path.read_text())
    assert meta["vault"] == {"KEY_A": "enc_a", "KEY_B": "enc_b"}
    assert isinstance(meta["timestamp"], int)


def test_list_snapshots_empty(tmp_path: Path) -> None:
    (tmp_path / "vault.json").write_text(json.dumps({}))
    # no snapshots yet
    assert list_snapshots(str(tmp_path)) == []


def test_list_snapshots_returns_newest_first(vault_dir: Path) -> None:
    create_snapshot(str(vault_dir), label="first")
    time.sleep(0.01)
    create_snapshot(str(vault_dir), label="second")
    snaps = list_snapshots(str(vault_dir))
    assert len(snaps) == 2
    assert snaps[0]["label"] == "second"
    assert snaps[1]["label"] == "first"


def test_restore_snapshot_overwrites_vault(vault_dir: Path) -> None:
    path = create_snapshot(str(vault_dir))
    # Modify the vault
    vault_file = vault_dir / "vault.json"
    vault_file.write_text(json.dumps({"KEY_C": "enc_c"}))
    restore_snapshot(str(vault_dir), path.name)
    restored = json.loads(vault_file.read_text())
    assert restored == {"KEY_A": "enc_a", "KEY_B": "enc_b"}


def test_restore_snapshot_missing_raises(vault_dir: Path) -> None:
    with pytest.raises(FileNotFoundError):
        restore_snapshot(str(vault_dir), "nonexistent.json")


def test_delete_snapshot_returns_true(vault_dir: Path) -> None:
    path = create_snapshot(str(vault_dir))
    assert delete_snapshot(str(vault_dir), path.name) is True
    assert not path.exists()


def test_delete_snapshot_missing_returns_false(vault_dir: Path) -> None:
    assert delete_snapshot(str(vault_dir), "ghost.json") is False
