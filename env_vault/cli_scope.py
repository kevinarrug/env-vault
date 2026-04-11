"""CLI commands for env-scope: manage key scopes."""
from __future__ import annotations

import click

from env_vault.env_scope import (
    add_to_scope,
    delete_scope,
    get_keys_in_scope,
    get_scopes_for_key,
    list_scopes,
    remove_from_scope,
)


@click.group("scope")
def scope_cmd() -> None:
    """Manage key scopes (dev, staging, prod, …)."""


@scope_cmd.command("add")
@click.argument("scope")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def add_cmd(scope: str, key: str, vault_dir: str) -> None:
    """Add KEY to SCOPE."""
    added = add_to_scope(vault_dir, scope, key)
    if added:
        click.echo(f"Added '{key}' to scope '{scope}'.")
    else:
        click.echo(f"'{key}' is already in scope '{scope}'.")


@scope_cmd.command("remove")
@click.argument("scope")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(scope: str, key: str, vault_dir: str) -> None:
    """Remove KEY from SCOPE."""
    removed = remove_from_scope(vault_dir, scope, key)
    if removed:
        click.echo(f"Removed '{key}' from scope '{scope}'.")
    else:
        click.echo(f"'{key}' not found in scope '{scope}'.")


@scope_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
def list_cmd(vault_dir: str) -> None:
    """List all defined scopes."""
    scopes = list_scopes(vault_dir)
    if not scopes:
        click.echo("No scopes defined.")
        return
    for s in scopes:
        keys = get_keys_in_scope(vault_dir, s)
        click.echo(f"{s}: {', '.join(keys) if keys else '(empty)'}")


@scope_cmd.command("keys")
@click.argument("scope")
@click.option("--vault-dir", default=".", show_default=True)
def keys_cmd(scope: str, vault_dir: str) -> None:
    """Show all keys in SCOPE."""
    keys = get_keys_in_scope(vault_dir, scope)
    if not keys:
        click.echo(f"No keys in scope '{scope}'.")
        return
    for k in keys:
        click.echo(k)


@scope_cmd.command("where")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def where_cmd(key: str, vault_dir: str) -> None:
    """Show all scopes that contain KEY."""
    scopes = get_scopes_for_key(vault_dir, key)
    if not scopes:
        click.echo(f"'{key}' is not assigned to any scope.")
        return
    for s in scopes:
        click.echo(s)


@scope_cmd.command("delete")
@click.argument("scope")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt.")
def delete_cmd(scope: str, vault_dir: str, yes: bool) -> None:
    """Delete an entire SCOPE."""
    if not yes:
        click.confirm(
            f"Are you sure you want to delete scope '{scope}'?", abort=True
        )
    deleted = delete_scope(vault_dir, scope)
    if deleted:
        click.echo(f"Scope '{scope}' deleted.")
    else:
        click.echo(f"Scope '{scope}' not found.")
