"""CLI commands for vault history inspection."""

from __future__ import annotations

import datetime
import sys
from pathlib import Path

import click

from env_vault.crypto import decrypt
from env_vault.history import (
    HISTORY_FILENAME,
    get_history,
    list_keys_with_history,
    purge_key_history,
)


@click.group("history")
def history_cmd() -> None:
    """Inspect or manage vault entry history."""


@history_cmd.command("log")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--passphrase", prompt=True, hide_input=True)
def log_cmd(key: str, vault_dir: str, passphrase: str) -> None:
    """Show decrypted history for KEY."""
    history_path = Path(vault_dir) / HISTORY_FILENAME
    entries = get_history(history_path, key)
    if not entries:
        click.echo(f"No history found for '{key}'.")
        return
    for entry in entries:
        ts = datetime.datetime.fromtimestamp(entry["timestamp"]).isoformat()
        action = entry["action"]
        try:
            value = decrypt(entry["value"], passphrase)
        except Exception:
            value = "<decryption failed>"
        click.echo(f"[{ts}] {action}: {value}")


@history_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
def list_cmd(vault_dir: str) -> None:
    """List all keys that have history entries."""
    history_path = Path(vault_dir) / HISTORY_FILENAME
    keys = list_keys_with_history(history_path)
    if not keys:
        click.echo("No history recorded yet.")
        return
    for k in sorted(keys):
        click.echo(k)


@history_cmd.command("purge")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
@click.confirmation_option(prompt="Are you sure you want to purge history for this key?")
def purge_cmd(key: str, vault_dir: str) -> None:
    """Delete all history entries for KEY."""
    history_path = Path(vault_dir) / HISTORY_FILENAME
    purge_key_history(history_path, key)
    click.echo(f"History purged for '{key}'.")
