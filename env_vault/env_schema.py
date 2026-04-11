"""Schema validation for vault keys — enforce types, patterns, and required fields."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SchemaRule:
    key: str
    required: bool = False
    pattern: str | None = None          # regex the *value* must match
    min_length: int | None = None
    max_length: int | None = None
    description: str = ""


@dataclass
class SchemaViolation:
    key: str
    message: str

    def __str__(self) -> str:
        return f"{self.key}: {self.message}"


@dataclass
class SchemaResult:
    violations: list[SchemaViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def summary(self) -> str:
        if self.passed:
            return "Schema validation passed."
        lines = [f"{len(self.violations)} violation(s) found:"]
        for v in self.violations:
            lines.append(f"  - {v}")
        return "\n".join(lines)


def validate(vault_data: dict[str, str], rules: list[SchemaRule]) -> SchemaResult:
    """Validate *vault_data* (key -> plaintext value) against *rules*."""
    result = SchemaResult()
    rule_map = {r.key: r for r in rules}

    # Check required keys and value constraints
    for rule in rules:
        value = vault_data.get(rule.key)

        if value is None:
            if rule.required:
                result.violations.append(
                    SchemaViolation(rule.key, "required key is missing")
                )
            continue

        if rule.min_length is not None and len(value) < rule.min_length:
            result.violations.append(
                SchemaViolation(rule.key, f"value too short (min {rule.min_length})")
            )

        if rule.max_length is not None and len(value) > rule.max_length:
            result.violations.append(
                SchemaViolation(rule.key, f"value too long (max {rule.max_length})")
            )

        if rule.pattern is not None and not re.fullmatch(rule.pattern, value):
            result.violations.append(
                SchemaViolation(rule.key, f"value does not match pattern '{rule.pattern}'")
            )

    return result
