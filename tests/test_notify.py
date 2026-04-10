"""Tests for env_vault.notify module."""
import pytest
from pathlib import Path
from env_vault.notify import (
    register_webhook,
    unregister_webhook,
    get_webhooks,
    emit_event,
    get_event_log,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_register_webhook_returns_true_when_new(vault_dir):
    result = register_webhook(vault_dir, "set", "https://example.com/hook")
    assert result is True


def test_register_webhook_returns_false_when_duplicate(vault_dir):
    register_webhook(vault_dir, "set", "https://example.com/hook")
    result = register_webhook(vault_dir, "set", "https://example.com/hook")
    assert result is False


def test_get_webhooks_returns_registered_urls(vault_dir):
    register_webhook(vault_dir, "set", "https://a.com")
    register_webhook(vault_dir, "set", "https://b.com")
    hooks = get_webhooks(vault_dir, "set")
    assert "https://a.com" in hooks["set"]
    assert "https://b.com" in hooks["set"]


def test_get_webhooks_empty_when_none_registered(vault_dir):
    hooks = get_webhooks(vault_dir)
    assert hooks == {}


def test_unregister_webhook_returns_true_when_found(vault_dir):
    register_webhook(vault_dir, "delete", "https://example.com")
    result = unregister_webhook(vault_dir, "delete", "https://example.com")
    assert result is True


def test_unregister_webhook_returns_false_when_missing(vault_dir):
    result = unregister_webhook(vault_dir, "delete", "https://notregistered.com")
    assert result is False


def test_unregister_removes_url_from_list(vault_dir):
    register_webhook(vault_dir, "rotate", "https://example.com")
    unregister_webhook(vault_dir, "rotate", "https://example.com")
    hooks = get_webhooks(vault_dir, "rotate")
    assert "https://example.com" not in hooks.get("rotate", [])


def test_emit_event_returns_registered_urls(vault_dir):
    register_webhook(vault_dir, "set", "https://hook1.com")
    register_webhook(vault_dir, "set", "https://hook2.com")
    urls = emit_event(vault_dir, "set", "MY_KEY")
    assert "https://hook1.com" in urls
    assert "https://hook2.com" in urls


def test_emit_event_logs_entry(vault_dir):
    emit_event(vault_dir, "set", "MY_KEY", {"old": "x", "new": "y"})
    log = get_event_log(vault_dir)
    assert len(log) == 1
    assert log[0]["event"] == "set"
    assert log[0]["key"] == "MY_KEY"


def test_get_event_log_filtered_by_event(vault_dir):
    emit_event(vault_dir, "set", "A")
    emit_event(vault_dir, "delete", "B")
    log = get_event_log(vault_dir, "delete")
    assert all(e["event"] == "delete" for e in log)
    assert len(log) == 1


def test_get_event_log_empty_when_no_events(vault_dir):
    log = get_event_log(vault_dir)
    assert log == []
