"""CLI commands for key ownership management."""
from __future__ import annotations

import click

from .env_owner import (
    get_all_owners,
    get_owner,
    list_owned_by,
    remove_owner,
    set_owner,
)


@click.group("owner")
def owner_cmd() -> None:
    """Manage key ownership."""


@owner_cmd.command("set")
@click.argument("key")
@click.argument("owner")
@click.option("--vault-dir", default=".", show_default=True)
def set_cmd(key: str, owner: str, vault_dir: str) -> None:
    """Assign OWNER to KEY."""
    is_new = set_owner(vault_dir, key, owner)
    if is_new:
        click.echo(f"Owner of '{key}' set to '{owner}'.")
    else:
        click.echo(f"Owner of '{key}' unchanged (already '{owner}').")


@owner_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key: str, vault_dir: str) -> None:
    """Remove ownership record for KEY."""
    if remove_owner(vault_dir, key):
        click.echo(f"Ownership record for '{key}' removed.")
    else:
        click.echo(f"No ownership record found for '{key}'.")


@owner_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key: str, vault_dir: str) -> None:
    """Show the owner of KEY."""
    owner = get_owner(vault_dir, key)
    if owner is None:
        click.echo(f"No owner set for '{key}'.")
    else:
        click.echo(owner)


@owner_cmd.command("list")
@click.option("--owner", default=None, help="Filter by owner name.")
@click.option("--vault-dir", default=".", show_default=True)
def list_cmd(owner: str | None, vault_dir: str) -> None:
    """List all key→owner assignments, optionally filtered."""
    if owner:
        keys = list_owned_by(vault_dir, owner)
        if not keys:
            click.echo(f"No keys owned by '{owner}'.")
        else:
            for k in keys:
                click.echo(k)
    else:
        data = get_all_owners(vault_dir)
        if not data:
            click.echo("No ownership records.")
        else:
            for k, v in sorted(data.items()):
                click.echo(f"{k}: {v}")
