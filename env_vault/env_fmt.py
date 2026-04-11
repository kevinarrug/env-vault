"""Formatting and normalization utilities for environment variable values."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FmtResult:
    key: str
    original: str
    formatted: str
    changed: bool

    def __str__(self) -> str:
        status = "changed" if self.changed else "unchanged"
        return f"{self.key}: {status}"


@dataclass
class FmtReport:
    results: List[FmtResult] = field(default_factory=list)

    @property
    def changed_keys(self) -> List[str]:
        return [r.key for r in self.results if r.changed]

    def summary(self) -> str:
        total = len(self.results)
        changed = len(self.changed_keys)
        if changed == 0:
            return f"All {total} key(s) already formatted."
        return f"{changed}/{total} key(s) reformatted."


_FORMATTERS = {
    "strip": str.strip,
    "upper": str.upper,
    "lower": str.lower,
    "strip_quotes": lambda v: v.strip("'\"" ),
}


def apply_format(value: str, fmt: str) -> str:
    """Apply a named formatter to a value. Raises ValueError for unknown formats."""
    if fmt not in _FORMATTERS:
        raise ValueError(f"Unknown format '{fmt}'. Available: {list(_FORMATTERS)}.")
    return _FORMATTERS[fmt](value)


def fmt_key(vault, passphrase: str, key: str, fmt: str) -> FmtResult:
    """Format a single key's value in the vault."""
    original = vault.get(key, passphrase)
    formatted = apply_format(original, fmt)
    changed = formatted != original
    if changed:
        vault.set(key, formatted, passphrase)
    return FmtResult(key=key, original=original, formatted=formatted, changed=changed)


def fmt_all(vault, passphrase: str, fmt: str) -> FmtReport:
    """Format all keys in the vault using the specified formatter."""
    report = FmtReport()
    for key in vault.list_keys():
        result = fmt_key(vault, passphrase, key, fmt)
        report.results.append(result)
    return report
