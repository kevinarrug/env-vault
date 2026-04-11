"""env_chain.py — chain multiple vaults together with fallback resolution."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from env_vault.vault import Vault


@dataclass
class ChainResult:
    key: str
    value: Optional[str]
    source: Optional[str]  # vault_dir that provided the value
    checked: List[str] = field(default_factory=list)  # all dirs checked in order

    @property
    def found(self) -> bool:
        return self.value is not None

    def __str__(self) -> str:
        if self.found:
            return f"{self.key}={self.value!r} (from {self.source})"
        return f"{self.key}: not found in chain ({', '.join(self.checked)})"


def resolve(key: str, vault_dirs: List[str], passphrase: str) -> ChainResult:
    """Resolve *key* by searching vaults in order; return first match."""
    checked: List[str] = []
    for vault_dir in vault_dirs:
        checked.append(vault_dir)
        vault = Vault(vault_dir, passphrase)
        try:
            value = vault.get(key)
            return ChainResult(key=key, value=value, source=vault_dir, checked=checked)
        except KeyError:
            continue
    return ChainResult(key=key, value=None, source=None, checked=checked)


def resolve_all(vault_dirs: List[str], passphrase: str) -> Dict[str, ChainResult]:
    """Resolve every key visible across the chain; later vaults are overridden by earlier ones."""
    seen: Dict[str, ChainResult] = {}
    # Walk in *reverse* so earlier vaults win (overwrite later entries)
    for vault_dir in reversed(vault_dirs):
        vault = Vault(vault_dir, passphrase)
        try:
            keys = vault.list_keys()
        except Exception:
            continue
        for key in keys:
            try:
                value = vault.get(key)
                seen[key] = ChainResult(
                    key=key, value=value, source=vault_dir, checked=vault_dirs
                )
            except Exception:
                pass
    return seen
