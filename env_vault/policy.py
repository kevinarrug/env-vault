"""Policy enforcement for vault keys — define and validate rules such as
required keys, forbidden patterns, and value constraints."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class PolicyViolation:
    key: str
    rule: str
    message: str

    def __str__(self) -> str:
        return f"[{self.rule}] {self.key}: {self.message}"


@dataclass
class PolicyResult:
    violations: List[PolicyViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def summary(self) -> str:
        if self.passed:
            return "All policy checks passed."
        lines = [f"{len(self.violations)} violation(s) found:"]
        for v in self.violations:
            lines.append(f"  - {v}")
        return "\n".join(lines)


def _policy_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".env_vault_policy.json"


def load_policy(vault_dir: str) -> dict:
    path = _policy_path(vault_dir)
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def save_policy(vault_dir: str, policy: dict) -> None:
    path = _policy_path(vault_dir)
    with path.open("w") as fh:
        json.dump(policy, fh, indent=2)


def enforce_policy(vault_keys: dict, policy: dict) -> PolicyResult:
    """Validate *vault_keys* (mapping of key -> plaintext value) against *policy*.

    Policy schema (all fields optional):
      required_keys   : list[str]  — keys that must be present
      forbidden_regex : list[str]  — key name patterns that must NOT exist
      value_min_length: int        — minimum length for every non-empty value
      key_pattern     : str        — regex every key name must match
    """
    result = PolicyResult()

    for key in policy.get("required_keys", []):
        if key not in vault_keys:
            result.violations.append(
                PolicyViolation(key, "required_keys", "key is missing from vault")
            )

    for pattern in policy.get("forbidden_regex", []):
        rx = re.compile(pattern)
        for key in vault_keys:
            if rx.search(key):
                result.violations.append(
                    PolicyViolation(key, "forbidden_regex",
                                    f"key matches forbidden pattern '{pattern}'")
                )

    min_len: Optional[int] = policy.get("value_min_length")
    if min_len is not None:
        for key, value in vault_keys.items():
            if value and len(value) < min_len:
                result.violations.append(
                    PolicyViolation(key, "value_min_length",
                                    f"value length {len(value)} < required {min_len}")
                )

    key_pattern: Optional[str] = policy.get("key_pattern")
    if key_pattern:
        rx = re.compile(key_pattern)
        for key in vault_keys:
            if not rx.fullmatch(key):
                result.violations.append(
                    PolicyViolation(key, "key_pattern",
                                    f"key does not match required pattern '{key_pattern}'")
                )

    return result
