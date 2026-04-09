"""CLI commands for passphrase rotation."""

from __future__ import annotations

import click

from .rotate import rotate_passphrase, rotate_single_key
from .vault import Vault


@click.group()
def rotate_cmd() -> None:
    """Rotate encryption passphrases or refresh individual key nonces."""


@rotate_cmd.command("all")
@click.option("--vault-path", required=True, envvar="ENV_VAULT_PATH", help="Path to vault file.")
@click.option("--old-passphrase", prompt=True, hide_input=True, help="Current passphrase.")
@click.option("--new-passphrase", prompt=True, hide_input=True, confirmation_prompt=True, help="New passphrase.")
def rotate_all_cmd(vault_path: str, old_passphrase: str, new_passphrase: str) -> None:
    """Re-encrypt ALL keys with a new passphrase."""
    vault = Vault(vault_path)
    vault.load()

    try:
        rotated = rotate_passphrase(vault, old_passphrase, new_passphrase)
    except (ValueError, Exception) as exc:
        raise click.ClickException(str(exc)) from exc

    if rotated:
        click.echo(f"Rotated {len(rotated)} key(s): {', '.join(rotated)}")
    else:
        click.echo("No keys found in vault — nothing to rotate.")


@rotate_cmd.command("key")
@click.argument("key_name")
@click.option("--vault-path", required=True, envvar="ENV_VAULT_PATH", help="Path to vault file.")
@click.option("--passphrase", prompt=True, hide_input=True, help="Current passphrase.")
def rotate_key_cmd(key_name: str, vault_path: str, passphrase: str) -> None:
    """Refresh the nonce for a single KEY_NAME without changing the passphrase."""
    vault = Vault(vault_path)
    vault.load()

    try:
        rotate_single_key(vault, key_name, passphrase)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    except ValueError as exc:
        raise click.ClickException(f"Decryption failed: {exc}") from exc

    click.echo(f"Key '{key_name}' re-encrypted with a fresh nonce.")
