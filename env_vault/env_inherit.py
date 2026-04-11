"""Inheritance: let a vault inherit keys from a parent vault, with child overrides."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from env_vault.vault import Vault


@dataclass
class InheritResult:
    key: str
    value: str
    source: str  # 'child' | 'parent'
    overridden: bool = False

    def __str__(self) -> str:
        tag = "(overridden)" if self.overridden else ""
        return f"{self.key}={self.value!r} [{self.source}] {tag}".strip()


@dataclass
class InheritReport:
    entries: List[InheritResult] = field(default_factory=list)

    @property
    def inherited_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.source == "parent"]

    @property
    def overridden_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.overridden]

    def summary(self) -> str:
        total = len(self.entries)
        inh = len(self.inherited_keys)
        ov = len(self.overridden_keys)
        return f"{total} keys resolved: {inh} inherited, {ov} overridden by child"


def resolve_inherited(
    child: Vault,
    parent: Vault,
    passphrase: str,
) -> InheritReport:
    """Merge parent keys into child, child values take priority."""
    child_keys = set(child.list())
    parent_keys = set(parent.list())

    entries: List[InheritResult] = []

    all_keys = sorted(child_keys | parent_keys)
    for key in all_keys:
        in_child = key in child_keys
        in_parent = key in parent_keys

        if in_child and in_parent:
            value = child.get(key, passphrase)
            entries.append(InheritResult(key=key, value=value, source="child", overridden=True))
        elif in_child:
            value = child.get(key, passphrase)
            entries.append(InheritResult(key=key, value=value, source="child", overridden=False))
        else:
            value = parent.get(key, passphrase)
            entries.append(InheritResult(key=key, value=value, source="parent", overridden=False))

    return InheritReport(entries=entries)


def apply_inheritance(
    child: Vault,
    parent: Vault,
    passphrase: str,
    overwrite: bool = False,
) -> List[str]:
    """Copy parent keys into child vault. Returns list of keys written."""
    child_keys = set(child.list())
    parent_keys = set(parent.list())
    written: List[str] = []

    for key in sorted(parent_keys):
        if key not in child_keys or overwrite:
            value = parent.get(key, passphrase)
            child.set(key, value, passphrase)
            written.append(key)

    return written
