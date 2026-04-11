"""CLI commands for placeholder detection."""
from __future__ import annotations

import click

from env_vault.vault import Vault
from env_vault import env_placeholder as ph


@click.group("placeholder")
def placeholder_cmd() -> None:
    """Detect and fill placeholder values in the vault."""


@placeholder_cmd.command("scan")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--passphrase", envvar="VAULT_PASSPHRASE", prompt=True, hide_input=True)
def scan_cmd(vault_dir: str, passphrase: str) -> None:
    """List all keys and whether they contain placeholder values."""
    vault = Vault(vault_dir)
    results = ph.scan_vault(vault, passphrase)
    if not results:
        click.echo("Vault is empty.")
        return
    for r in results:
        marker = click.style("PLACEHOLDER", fg="yellow") if r.is_placeholder else click.style("set", fg="green")
        click.echo(f"  {r.key}: [{marker}]")


@placeholder_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--passphrase", envvar="VAULT_PASSPHRASE", prompt=True, hide_input=True)
def list_cmd(vault_dir: str, passphrase: str) -> None:
    """Print only keys that still hold placeholder values."""
    vault = Vault(vault_dir)
    keys = ph.list_placeholders(vault, passphrase)
    if not keys:
        click.echo("No placeholders found.")
        return
    for key in keys:
        click.echo(key)


@placeholder_cmd.command("fill")
@click.argument("key")
@click.argument("value")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--passphrase", envvar="VAULT_PASSPHRASE", prompt=True, hide_input=True)
def fill_cmd(key: str, value: str, vault_dir: str, passphrase: str) -> None:
    """Replace a placeholder with a real value."""
    vault = Vault(vault_dir)
    was_placeholder = ph.fill_placeholder(vault, passphrase, key, value)
    if was_placeholder:
        click.echo(f"Filled placeholder for '{key}'.")
    else:
        click.echo(f"'{key}' was not a placeholder — value updated anyway.")
