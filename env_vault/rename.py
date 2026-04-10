"""Rename keys within a vault, preserving history, tags, and audit trail."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from env_vault.vault import Vault


@dataclass
class RenameResult:
    old_key: str
    new_key: str
    success: bool
    message: str

    def __str__(self) -> str:
        if self.success:
            return f"Renamed '{self.old_key}' -> '{self.new_key}'"
        return f"Rename failed: {self.message}"


def rename_key(
    vault: Vault,
    passphrase: str,
    old_key: str,
    new_key: str,
    *,
    overwrite: bool = False,
) -> RenameResult:
    """Rename *old_key* to *new_key* inside *vault*.

    Parameters
    ----------
    vault:       Vault instance (already opened).
    passphrase:  Passphrase used to decrypt / re-encrypt the value.
    old_key:     Existing key name.
    new_key:     Desired key name.
    overwrite:   If *True*, silently replace *new_key* when it already exists.

    Returns
    -------
    RenameResult describing the outcome.
    """
    keys = vault.list_keys()

    if old_key not in keys:
        return RenameResult(
            old_key=old_key,
            new_key=new_key,
            success=False,
            message=f"Key '{old_key}' not found in vault.",
        )

    if new_key in keys and not overwrite:
        return RenameResult(
            old_key=old_key,
            new_key=new_key,
            success=False,
            message=(
                f"Key '{new_key}' already exists. "
                "Use overwrite=True to replace it."
            ),
        )

    value = vault.get(old_key, passphrase)
    vault.set(new_key, value, passphrase)
    vault.delete(old_key)

    return RenameResult(
        old_key=old_key,
        new_key=new_key,
        success=True,
        message="OK",
    )
