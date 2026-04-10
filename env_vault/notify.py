"""Notification hooks for vault events."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional

HookFn = Callable[[str, str, dict], None]

_HOOKS: Dict[str, List[HookFn]] = {}


def _hooks_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_vault" / "notify_hooks.json"


def _load_hooks(vault_dir: str) -> dict:
    p = _hooks_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_hooks(vault_dir: str, data: dict) -> None:
    p = _hooks_path(vault_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def register_webhook(vault_dir: str, event: str, url: str) -> bool:
    """Register a webhook URL for a given event type. Returns True if newly added."""
    data = _load_hooks(vault_dir)
    hooks = data.setdefault(event, [])
    if url in hooks:
        return False
    hooks.append(url)
    _save_hooks(vault_dir, data)
    return True


def unregister_webhook(vault_dir: str, event: str, url: str) -> bool:
    """Remove a webhook URL for a given event. Returns True if it existed."""
    data = _load_hooks(vault_dir)
    hooks = data.get(event, [])
    if url not in hooks:
        return False
    hooks.remove(url)
    data[event] = hooks
    _save_hooks(vault_dir, data)
    return True


def get_webhooks(vault_dir: str, event: Optional[str] = None) -> dict:
    """Return all webhooks, optionally filtered by event type."""
    data = _load_hooks(vault_dir)
    if event is not None:
        return {event: data.get(event, [])}
    return data


def emit_event(vault_dir: str, event: str, key: str, meta: Optional[dict] = None) -> List[str]:
    """Record a notification event and return list of registered webhook URLs."""
    data = _load_hooks(vault_dir)
    urls = data.get(event, [])
    _append_event_log(vault_dir, event, key, meta or {})
    return list(urls)


def _append_event_log(vault_dir: str, event: str, key: str, meta: dict) -> None:
    log_path = Path(vault_dir) / ".env_vault" / "notify_log.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entries = json.loads(log_path.read_text()) if log_path.exists() else []
    entries.append({"event": event, "key": key, "meta": meta, "ts": time.time()})
    log_path.write_text(json.dumps(entries[-200:], indent=2))


def get_event_log(vault_dir: str, event: Optional[str] = None) -> List[dict]:
    """Return recorded notification events, optionally filtered by type."""
    log_path = Path(vault_dir) / ".env_vault" / "notify_log.json"
    if not log_path.exists():
        return []
    entries = json.loads(log_path.read_text())
    if event:
        entries = [e for e in entries if e["event"] == event]
    return entries
