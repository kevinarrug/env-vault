"""Masking/redaction utilities for sensitive vault values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

_DEFAULT_MASK = "********"
_PARTIAL_VISIBLE = 4  # chars shown at end for partial masking


@dataclass
class MaskResult:
    key: str
    original: str
    masked: str
    mode: str  # 'full' | 'partial' | 'none'

    def __str__(self) -> str:
        return f"{self.key}={self.masked}  [{self.mode}]"


def mask_full(value: str) -> str:
    """Replace the entire value with the mask string."""
    return _DEFAULT_MASK


def mask_partial(value: str, visible: int = _PARTIAL_VISIBLE) -> str:
    """Show only the last *visible* characters; mask the rest."""
    if len(value) <= visible:
        return _DEFAULT_MASK
    return "*" * (len(value) - visible) + value[-visible:]


def mask_value(value: str, mode: str = "full") -> str:
    """Return a masked representation of *value* according to *mode*.

    Modes:
        full    – replace everything with ``********``
        partial – keep last 4 characters, mask the rest
        none    – return value unchanged
    """
    if mode == "full":
        return mask_full(value)
    if mode == "partial":
        return mask_partial(value)
    if mode == "none":
        return value
    raise ValueError(f"Unknown mask mode: {mode!r}. Choose full, partial, or none.")


def mask_key(vault, passphrase: str, key: str, mode: str = "full") -> MaskResult:
    """Decrypt *key* from *vault* and return a :class:`MaskResult`."""
    value = vault.get(key, passphrase)
    masked = mask_value(value, mode)
    return MaskResult(key=key, original=value, masked=masked, mode=mode)


def mask_all(vault, passphrase: str, mode: str = "full") -> List[MaskResult]:
    """Return :class:`MaskResult` for every key in *vault*."""
    results: List[MaskResult] = []
    for key in vault.list_keys():
        results.append(mask_key(vault, passphrase, key, mode))
    return sorted(results, key=lambda r: r.key)
