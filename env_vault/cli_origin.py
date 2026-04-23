"""CLI commands for managing key origins."""

from __future__ import annotations

import click

from env_vault.env_origin import (
    get_origin,
    keys_by_origin,
    list_origins,
    remove_origin,
    set_origin,
)


@click.group(name="origin")
def origin_cmd():
    """Manage key origin metadata."""


@origin_cmd.command(name="set")
@click.argument("key")
@click.argument("origin")
@click.option("--vault-dir", default=".", show_default=True)
def set_cmd(key: str, origin: str, vault_dir: str):
    """Set the origin for a key."""
    is_new = set_origin(vault_dir, key, origin)
    if is_new:
        click.echo(f"Origin for '{key}' set to '{origin}'.")
    else:
        click.echo(f"Origin for '{key}' unchanged (already '{origin}').")


@origin_cmd.command(name="remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key: str, vault_dir: str):
    """Remove the origin for a key."""
    removed = remove_origin(vault_dir, key)
    if removed:
        click.echo(f"Origin for '{key}' removed.")
    else:
        click.echo(f"No origin found for '{key}'.")


@origin_cmd.command(name="get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key: str, vault_dir: str):
    """Get the origin for a key."""
    origin = get_origin(vault_dir, key)
    if origin is None:
        click.echo(f"No origin set for '{key}'.")
        raise SystemExit(1)
    click.echo(origin)


@origin_cmd.command(name="list")
@click.option("--vault-dir", default=".", show_default=True)
def list_cmd(vault_dir: str):
    """List all key origins."""
    origins = list_origins(vault_dir)
    if not origins:
        click.echo("No origins recorded.")
        return
    for key, origin in sorted(origins.items()):
        click.echo(f"{key}: {origin}")


@origin_cmd.command(name="filter")
@click.argument("origin")
@click.option("--vault-dir", default=".", show_default=True)
def filter_cmd(origin: str, vault_dir: str):
    """List keys that share a given origin."""
    keys = keys_by_origin(vault_dir, origin)
    if not keys:
        click.echo(f"No keys with origin '{origin}'.")
        return
    for key in keys:
        click.echo(key)
