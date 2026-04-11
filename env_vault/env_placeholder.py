"""Placeholder detection and management for vault keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

PLACEHOLDER_MARKER = "__PLACEHOLDER__"


@dataclass
class PlaceholderResult:
    key: str
    is_placeholder: bool
    current_value: Optional[str] = None

    def __str__(self) -> str:
        status = "placeholder" if self.is_placeholder else "set"
        return f"{self.key}: [{status}]"


def is_placeholder(value: str) -> bool:
    """Return True if value looks like an unfilled placeholder."""
    v = value.strip()
    return (
        v == PLACEHOLDER_MARKER
        or (v.startswith("<") and v.endswith(">"))
        or (v.startswith("{") and v.endswith("}"))
        or v == ""
    )


def check_key(vault, passphrase: str, key: str) -> PlaceholderResult:
    """Check whether a single vault key holds a placeholder value."""
    value = vault.get(key, passphrase)
    return PlaceholderResult(
        key=key,
        is_placeholder=is_placeholder(value),
        current_value=value,
    )


def scan_vault(vault, passphrase: str) -> List[PlaceholderResult]:
    """Scan all keys in the vault and return placeholder status for each."""
    results = []
    for key in vault.list_keys():
        results.append(check_key(vault, passphrase, key))
    return results


def list_placeholders(vault, passphrase: str) -> List[str]:
    """Return only keys whose values are placeholders."""
    return [
        r.key for r in scan_vault(vault, passphrase) if r.is_placeholder
    ]


def fill_placeholder(vault, passphrase: str, key: str, value: str) -> bool:
    """Set a real value for a placeholder key.

    Returns True if the key was previously a placeholder, False otherwise.
    """
    result = check_key(vault, passphrase, key)
    vault.set(key, value, passphrase)
    return result.is_placeholder
