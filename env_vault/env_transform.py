"""Transform vault values using composable transformation pipelines."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from env_vault.vault import Vault

TRANSFORM_FNS: Dict[str, Callable[[str], str]] = {
    "upper": str.upper,
    "lower": str.lower,
    "strip": str.strip,
    "reverse": lambda v: v[::-1],
    "base64_encode": lambda v: __import__("base64").b64encode(v.encode()).decode(),
    "base64_decode": lambda v: __import__("base64").b64decode(v.encode()).decode(),
    "url_encode": lambda v: __import__("urllib.parse", fromlist=["quote"]).quote(v),
    "url_decode": lambda v: __import__("urllib.parse", fromlist=["unquote"]).unquote(v),
}


@dataclass
class TransformResult:
    key: str
    original: str
    transformed: str
    pipeline: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def __str__(self) -> str:
        status = f"error: {self.error}" if self.error else f"{self.original!r} -> {self.transformed!r}"
        steps = " | ".join(self.pipeline)
        return f"{self.key} [{steps}]: {status}"

    @property
    def ok(self) -> bool:
        return self.error is None


def apply_pipeline(value: str, pipeline: List[str]) -> tuple[str, Optional[str]]:
    """Apply a list of named transforms in order. Returns (result, error)."""
    current = value
    for step in pipeline:
        fn = TRANSFORM_FNS.get(step)
        if fn is None:
            return current, f"unknown transform '{step}'"
        try:
            current = fn(current)
        except Exception as exc:  # noqa: BLE001
            return current, f"transform '{step}' failed: {exc}"
    return current, None


def transform_key(
    vault: Vault, passphrase: str, key: str, pipeline: List[str]
) -> TransformResult:
    """Decrypt a key, run pipeline, return result (does NOT save)."""
    original = vault.get(key, passphrase)
    transformed, error = apply_pipeline(original, pipeline)
    return TransformResult(
        key=key,
        original=original,
        transformed=transformed,
        pipeline=pipeline,
        error=error,
    )


def transform_and_save(
    vault: Vault, passphrase: str, key: str, pipeline: List[str]
) -> TransformResult:
    """Decrypt, transform, and re-encrypt the value in place."""
    result = transform_key(vault, passphrase, key, pipeline)
    if result.ok:
        vault.set(key, result.transformed, passphrase)
    return result


def list_transforms() -> List[str]:
    """Return sorted list of available transform names."""
    return sorted(TRANSFORM_FNS.keys())
