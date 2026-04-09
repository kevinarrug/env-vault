"""Lint and validate environment variable keys and values in a vault."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

from env_vault.vault import Vault

# POSIX-compliant env var name: uppercase letters, digits, underscores, not starting with digit
_VALID_KEY_RE = re.compile(r'^[A-Z_][A-Z0-9_]*$')
_WARN_LOWERCASE_RE = re.compile(r'[a-z]')


@dataclass
class LintIssue:
    key: str
    level: str  # 'error' | 'warning'
    message: str

    def __str__(self) -> str:
        return f"[{self.level.upper()}] {self.key}: {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.level == 'error']

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.level == 'warning']

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        if not self.issues:
            return "No issues found."
        lines = [str(i) for i in self.issues]
        lines.append(f"{len(self.errors)} error(s), {len(self.warnings)} warning(s).")
        return "\n".join(lines)


def lint_vault(vault: Vault, passphrase: str) -> LintResult:
    """Run lint checks on all keys and decrypted values in the vault."""
    result = LintResult()
    keys = vault.list_keys()

    if not keys:
        return result

    for key in keys:
        # Key format checks
        if not _VALID_KEY_RE.match(key):
            if _WARN_LOWERCASE_RE.search(key):
                result.issues.append(LintIssue(key, 'warning', "Key contains lowercase letters; prefer UPPER_SNAKE_CASE."))
            else:
                result.issues.append(LintIssue(key, 'error', f"Key '{key}' is not a valid POSIX environment variable name."))

        # Value checks
        try:
            value = vault.get(key, passphrase)
        except Exception:
            result.issues.append(LintIssue(key, 'error', "Failed to decrypt value; vault may be corrupted."))
            continue

        if value == "":
            result.issues.append(LintIssue(key, 'warning', "Value is empty."))

        if len(value) > 32768:
            result.issues.append(LintIssue(key, 'warning', "Value is unusually large (>32 KB)."))

    return result
