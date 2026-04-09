"""Diff utilities for comparing vault snapshots or key sets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DiffResult:
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines = []
        for key in sorted(self.added):
            lines.append(f"+ {key}")
        for key in sorted(self.removed):
            lines.append(f"- {key}")
        for key in sorted(self.changed):
            lines.append(f"~ {key}")
        return "\n".join(lines) if lines else "No changes."


def diff_vaults(
    vault_a,
    vault_b,
    passphrase_a: str,
    passphrase_b: Optional[str] = None,
) -> DiffResult:
    """Compare two Vault instances and return a DiffResult.

    If passphrase_b is None, passphrase_a is used for both vaults.
    """
    if passphrase_b is None:
        passphrase_b = passphrase_a

    keys_a = set(vault_a.list_keys())
    keys_b = set(vault_b.list_keys())

    result = DiffResult()
    result.added = sorted(keys_b - keys_a)
    result.removed = sorted(keys_a - keys_b)

    for key in keys_a & keys_b:
        val_a = vault_a.get(key, passphrase_a)
        val_b = vault_b.get(key, passphrase_b)
        if val_a != val_b:
            result.changed.append(key)
        else:
            result.unchanged.append(key)

    result.changed.sort()
    result.unchanged.sort()
    return result


def diff_dicts(
    dict_a: Dict[str, str],
    dict_b: Dict[str, str],
) -> DiffResult:
    """Compare two plain-text key/value dicts (e.g. from export_json)."""
    keys_a = set(dict_a)
    keys_b = set(dict_b)

    result = DiffResult()
    result.added = sorted(keys_b - keys_a)
    result.removed = sorted(keys_a - keys_b)

    for key in keys_a & keys_b:
        if dict_a[key] != dict_b[key]:
            result.changed.append(key)
        else:
            result.unchanged.append(key)

    result.changed.sort()
    result.unchanged.sort()
    return result
