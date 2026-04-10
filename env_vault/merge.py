"""Merge two vaults with configurable conflict resolution strategies."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple


class ConflictStrategy(str, Enum):
    OURS = "ours"       # keep value from base vault
    THEIRS = "theirs"   # take value from other vault
    ERROR = "error"     # raise on any conflict


@dataclass
class MergeConflict:
    key: str
    ours: str
    theirs: str

    def __str__(self) -> str:
        return f"CONFLICT {self.key!r}: ours={self.ours!r} theirs={self.theirs!r}"


@dataclass
class MergeResult:
    merged: Dict[str, str] = field(default_factory=dict)
    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    conflicts: List[MergeConflict] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.updated:
            parts.append(f"{len(self.updated)} updated")
        if self.conflicts:
            parts.append(f"{len(self.conflicts)} conflict(s)")
        return ", ".join(parts) if parts else "no changes"


class MergeConflictError(Exception):
    """Raised when strategy=ERROR and a conflict is detected."""


def merge_dicts(
    base: Dict[str, str],
    other: Dict[str, str],
    strategy: ConflictStrategy = ConflictStrategy.OURS,
) -> MergeResult:
    """Merge *other* into *base* and return a MergeResult."""
    result = MergeResult(merged=dict(base))

    for key, other_val in other.items():
        if key not in base:
            result.merged[key] = other_val
            result.added.append(key)
        elif base[key] != other_val:
            conflict = MergeConflict(key=key, ours=base[key], theirs=other_val)
            result.conflicts.append(conflict)
            if strategy == ConflictStrategy.ERROR:
                raise MergeConflictError(str(conflict))
            elif strategy == ConflictStrategy.THEIRS:
                result.merged[key] = other_val
                result.updated.append(key)
            # OURS: keep existing value, still record conflict

    return result


def merge_vaults(
    base_vault,
    other_vault,
    passphrase: str,
    strategy: ConflictStrategy = ConflictStrategy.OURS,
) -> MergeResult:
    """Decrypt both vaults, merge, and write result into *base_vault*."""
    base_data = {k: base_vault.get(k, passphrase) for k in base_vault.list_keys()}
    other_data = {k: other_vault.get(k, passphrase) for k in other_vault.list_keys()}

    result = merge_dicts(base_data, other_data, strategy=strategy)

    for key, value in result.merged.items():
        base_vault.set(key, value, passphrase)

    return result
