"""Tests for env_vault.backup and env_vault.cli_backup."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from env_vault.backup import (
    create_backup,
    delete_backup,
    list_backups,
    purge_backups,
    restore_backup,
)
from env_vault.cli_backup import backup_cmd


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    vault_file = tmp_path / "vault.json"
    vault_file.write_text(json.dumps({"KEY": "encrypted_value"}))
    return tmp_path


# --- unit tests ---

def test_create_backup_returns_path(vault_dir: Path) -> None:
    path = create_backup(str(vault_dir))
    assert path.exists()
    assert path.suffix == ".json"


def test_create_backup_with_label(vault_dir: Path) -> None:
    path = create_backup(str(vault_dir), label="before-deploy")
    assert "before-deploy" in path.name


def test_create_backup_no_vault_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        create_backup(str(tmp_path))


def test_list_backups_empty(tmp_path: Path) -> None:
    assert list_backups(str(tmp_path)) == []


def test_list_backups_sorted(vault_dir: Path) -> None:
    b1 = create_backup(str(vault_dir))
    b2 = create_backup(str(vault_dir), label="second")
    backups = list_backups(str(vault_dir))
    assert backups[0] == b1
    assert backups[1] == b2


def test_restore_backup_overwrites_vault(vault_dir: Path) -> None:
    backup = create_backup(str(vault_dir))
    (vault_dir / "vault.json").write_text(json.dumps({"NEW": "data"}))
    restore_backup(str(vault_dir), str(backup))
    data = json.loads((vault_dir / "vault.json").read_text())
    assert data == {"KEY": "encrypted_value"}


def test_restore_backup_missing_raises(vault_dir: Path) -> None:
    with pytest.raises(FileNotFoundError):
        restore_backup(str(vault_dir), str(vault_dir / "nonexistent.json"))


def test_delete_backup(vault_dir: Path) -> None:
    backup = create_backup(str(vault_dir))
    delete_backup(str(backup))
    assert not backup.exists()


def test_purge_keeps_recent(vault_dir: Path) -> None:
    for _ in range(7):
        create_backup(str(vault_dir))
    deleted = purge_backups(str(vault_dir), keep=3)
    assert len(deleted) == 4
    assert len(list_backups(str(vault_dir))) == 3


# --- CLI tests ---

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_cli_create_backup(runner: CliRunner, vault_dir: Path) -> None:
    result = runner.invoke(backup_cmd, ["create", "--vault-dir", str(vault_dir)])
    assert result.exit_code == 0
    assert "Backup created" in result.output


def test_cli_list_backups(runner: CliRunner, vault_dir: Path) -> None:
    create_backup(str(vault_dir))
    result = runner.invoke(backup_cmd, ["list", "--vault-dir", str(vault_dir)])
    assert result.exit_code == 0
    assert ".json" in result.output


def test_cli_purge(runner: CliRunner, vault_dir: Path) -> None:
    for _ in range(4):
        create_backup(str(vault_dir))
    result = runner.invoke(backup_cmd, ["purge", "--vault-dir", str(vault_dir), "--keep", "2"])
    assert result.exit_code == 0
    assert "removed" in result.output
