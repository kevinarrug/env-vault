"""Compare vault contents against a live environment or another source."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from env_vault.vault import Vault


@dataclass
class CompareEntry:
    key: str
    vault_value: Optional[str]
    env_value: Optional[str]

    @property
    def matches(self) -> bool:
        return self.vault_value == self.env_value

    @property
    def status(self) -> str:
        if self.vault_value is None:
            return "env_only"
        if self.env_value is None:
            return "vault_only"
        if self.matches:
            return "match"
        return "mismatch"

    def __str__(self) -> str:
        return f"{self.key}: [{self.status}]"


@dataclass
class CompareResult:
    entries: List[CompareEntry] = field(default_factory=list)

    @property
    def mismatches(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.status == "mismatch"]

    @property
    def vault_only(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.status == "vault_only"]

    @property
    def env_only(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.status == "env_only"]

    @property
    def all_match(self) -> bool:
        return all(e.matches for e in self.entries)

    def summary(self) -> str:
        if not self.entries:
            return "No keys to compare."
        parts = []
        if self.mismatches:
            parts.append(f"{len(self.mismatches)} mismatch(es)")
        if self.vault_only:
            parts.append(f"{len(self.vault_only)} vault-only")
        if self.env_only:
            parts.append(f"{len(self.env_only)} env-only")
        if not parts:
            return f"All {len(self.entries)} key(s) match."
        return "; ".join(parts) + "."


def compare_vault_to_env(
    vault: Vault,
    passphrase: str,
    env: Optional[Dict[str, str]] = None,
) -> CompareResult:
    """Compare decrypted vault values against a dict (default: os.environ)."""
    if env is None:
        env = dict(os.environ)

    all_keys = set(vault.list_keys()) | set(env.keys())
    entries: List[CompareEntry] = []

    for key in sorted(all_keys):
        vault_val: Optional[str] = None
        if key in vault.list_keys():
            try:
                vault_val = vault.get(key, passphrase)
            except Exception:
                vault_val = None
        env_val = env.get(key)
        entries.append(CompareEntry(key=key, vault_value=vault_val, env_value=env_val))

    return CompareResult(entries=entries)
