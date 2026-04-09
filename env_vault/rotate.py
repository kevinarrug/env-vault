"""Key rotation utilities for env-vault."""

from __future__ import annotations

from typing import List, Tuple

from .crypto import decrypt, encrypt
from .vault import Vault


def rotate_passphrase(
    vault: Vault,
    old_passphrase: str,
    new_passphrase: str,
) -> List[str]:
    """Re-encrypt every key in *vault* with *new_passphrase*.

    The vault is saved after all keys have been rotated successfully.
    Returns the list of key names that were rotated.

    Raises
    ------
    ValueError
        If *old_passphrase* is incorrect for any stored value.
    """
    keys = vault.list_keys()
    rotated: List[Tuple[str, str]] = []

    # Decrypt everything first so we fail fast before writing anything.
    for key in keys:
        raw_ciphertext = vault._data["secrets"][key]
        plaintext = decrypt(raw_ciphertext, old_passphrase)
        new_ciphertext = encrypt(plaintext, new_passphrase)
        rotated.append((key, new_ciphertext))

    # Commit all re-encrypted values.
    for key, new_ciphertext in rotated:
        vault._data["secrets"][key] = new_ciphertext

    vault.save()
    return keys


def rotate_single_key(
    vault: Vault,
    key: str,
    passphrase: str,
) -> str:
    """Re-encrypt a single *key* with the same passphrase (refreshes nonce).

    Returns the new ciphertext string.
    """
    if key not in vault._data.get("secrets", {}):
        raise KeyError(f"Key '{key}' not found in vault.")

    raw_ciphertext = vault._data["secrets"][key]
    plaintext = decrypt(raw_ciphertext, passphrase)
    new_ciphertext = encrypt(plaintext, passphrase)
    vault._data["secrets"][key] = new_ciphertext
    vault.save()
    return new_ciphertext
