"""Tests for env_vault.cli_notify CLI commands."""
import json
import pytest
from click.testing import CliRunner
from env_vault.cli_notify import notify_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_add_webhook_success(runner, vault_dir):
    result = runner.invoke(
        notify_cmd, ["add", "set", "https://example.com", "--vault-dir", vault_dir]
    )
    assert result.exit_code == 0
    assert "Registered" in result.output


def test_add_webhook_duplicate_reports_already_registered(runner, vault_dir):
    runner.invoke(notify_cmd, ["add", "set", "https://example.com", "--vault-dir", vault_dir])
    result = runner.invoke(
        notify_cmd, ["add", "set", "https://example.com", "--vault-dir", vault_dir]
    )
    assert result.exit_code == 0
    assert "already registered" in result.output


def test_remove_existing_webhook(runner, vault_dir):
    runner.invoke(notify_cmd, ["add", "delete", "https://hook.io", "--vault-dir", vault_dir])
    result = runner.invoke(
        notify_cmd, ["remove", "delete", "https://hook.io", "--vault-dir", vault_dir]
    )
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_missing_webhook_reports_error(runner, vault_dir):
    result = runner.invoke(
        notify_cmd, ["remove", "set", "https://missing.com", "--vault-dir", vault_dir]
    )
    assert "No webhook found" in result.output


def test_list_shows_registered_webhooks(runner, vault_dir):
    runner.invoke(notify_cmd, ["add", "set", "https://a.com", "--vault-dir", vault_dir])
    result = runner.invoke(notify_cmd, ["list", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "https://a.com" in result.output


def test_list_empty_shows_message(runner, vault_dir):
    result = runner.invoke(notify_cmd, ["list", "--vault-dir", vault_dir])
    assert "No webhooks" in result.output


def test_log_shows_events(runner, vault_dir):
    from env_vault.notify import emit_event
    emit_event(vault_dir, "set", "DB_URL")
    result = runner.invoke(notify_cmd, ["log", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    assert "set" in result.output
    assert "DB_URL" in result.output


def test_log_as_json(runner, vault_dir):
    from env_vault.notify import emit_event
    emit_event(vault_dir, "rotate", "SECRET_KEY")
    result = runner.invoke(notify_cmd, ["log", "--as-json", "--vault-dir", vault_dir])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert data[0]["key"] == "SECRET_KEY"
