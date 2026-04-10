"""Template rendering: substitute vault values into template strings."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from env_vault.vault import Vault

_PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


@dataclass
class RenderResult:
    rendered: str
    missing: List[str] = field(default_factory=list)
    substituted: List[str] = field(default_factory=list)

    @property
    def has_missing(self) -> bool:
        return len(self.missing) > 0

    def summary(self) -> str:
        parts = []
        if self.substituted:
            parts.append(f"substituted: {', '.join(sorted(self.substituted))}")
        if self.missing:
            parts.append(f"missing: {', '.join(sorted(self.missing))}")
        return "; ".join(parts) if parts else "no placeholders found"


def render_template(
    template: str,
    vault: Vault,
    passphrase: str,
    strict: bool = False,
) -> RenderResult:
    """Replace ``{{ KEY }}`` placeholders with decrypted vault values.

    Args:
        template: Raw template string containing ``{{ KEY }}`` placeholders.
        vault: Vault instance to read values from.
        passphrase: Passphrase used to decrypt vault values.
        strict: If *True*, raise ``KeyError`` for any missing key.

    Returns:
        :class:`RenderResult` with the rendered string and metadata.
    """
    missing: List[str] = []
    substituted: List[str] = []

    def _replace(match: re.Match) -> str:  # type: ignore[type-arg]
        key = match.group(1)
        try:
            value = vault.get(key, passphrase)
            substituted.append(key)
            return value
        except KeyError:
            if strict:
                raise KeyError(f"Template key '{key}' not found in vault")
            missing.append(key)
            return match.group(0)  # leave placeholder unchanged

    rendered = _PLACEHOLDER.sub(_replace, template)
    return RenderResult(rendered=rendered, missing=missing, substituted=substituted)


def render_file(
    path: str,
    vault: Vault,
    passphrase: str,
    strict: bool = False,
) -> RenderResult:
    """Read a file and render it as a template."""
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()
    return render_template(content, vault, passphrase, strict=strict)
