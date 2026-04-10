"""CLI commands for managing key aliases."""

from __future__ import annotations

import click

from .alias import add_alias, remove_alias, resolve_alias, list_aliases, rename_alias
from .vault import Vault


@click.group("alias")
def alias_cmd() -> None:
    """Manage key aliases."""


@alias_cmd.command("add")
@click.argument("alias")
@click.argument("target_key")
@click.option("--vault-dir", default=".", show_default=True)
def add_cmd(alias: str, target_key: str, vault_dir: str) -> None:
    """Create or update ALIAS pointing to TARGET_KEY."""
    is_new = add_alias(vault_dir, alias, target_key)
    verb = "Created" if is_new else "Updated"
    click.echo(f"{verb} alias '{alias}' -> '{target_key}'")


@alias_cmd.command("remove")
@click.argument("alias")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(alias: str, vault_dir: str) -> None:
    """Remove an alias."""
    if remove_alias(vault_dir, alias):
        click.echo(f"Removed alias '{alias}'")
    else:
        click.echo(f"Alias '{alias}' not found", err=True)
        raise SystemExit(1)


@alias_cmd.command("resolve")
@click.argument("alias")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--passphrase", prompt=True, hide_input=True)
def resolve_cmd(alias: str, vault_dir: str, passphrase: str) -> None:
    """Resolve ALIAS and print the decrypted value of its target key."""
    target = resolve_alias(vault_dir, alias)
    if target is None:
        click.echo(f"Alias '{alias}' not found", err=True)
        raise SystemExit(1)
    vault = Vault(vault_dir, passphrase)
    vault.load()
    click.echo(vault.get(target))


@alias_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
def list_cmd(vault_dir: str) -> None:
    """List all aliases."""
    entries = list_aliases(vault_dir)
    if not entries:
        click.echo("No aliases defined.")
        return
    for entry in entries:
        click.echo(f"{entry['alias']:30s} -> {entry['target']}")


@alias_cmd.command("rename")
@click.argument("old_alias")
@click.argument("new_alias")
@click.option("--vault-dir", default=".", show_default=True)
def rename_cmd(old_alias: str, new_alias: str, vault_dir: str) -> None:
    """Rename OLD_ALIAS to NEW_ALIAS (target unchanged)."""
    if rename_alias(vault_dir, old_alias, new_alias):
        click.echo(f"Renamed alias '{old_alias}' to '{new_alias}'")
    else:
        click.echo(f"Alias '{old_alias}' not found", err=True)
        raise SystemExit(1)
