"""CLI commands for managing key deprecations."""

import click

from env_vault.env_deprecate import (
    deprecate_key,
    get_deprecation,
    is_deprecated,
    list_deprecated,
    undeprecate_key,
)


@click.group("deprecate")
def deprecate_cmd():
    """Manage deprecated vault keys."""


@deprecate_cmd.command("set")
@click.argument("key")
@click.argument("reason")
@click.option("--replace", default=None, help="Suggested replacement key")
@click.option("--vault-dir", default=".", show_default=True)
def set_cmd(key, reason, replace, vault_dir):
    """Mark KEY as deprecated with REASON."""
    is_new = deprecate_key(vault_dir, key, reason, replacement=replace)
    if is_new:
        click.echo(f"Deprecated: {key}")
    else:
        click.echo(f"Updated deprecation for: {key}")


@deprecate_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key, vault_dir):
    """Remove deprecation from KEY."""
    if undeprecate_key(vault_dir, key):
        click.echo(f"Removed deprecation for: {key}")
    else:
        click.echo(f"Key not deprecated: {key}", err=True)
        raise SystemExit(1)


@deprecate_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key, vault_dir):
    """Show deprecation info for KEY."""
    info = get_deprecation(vault_dir, key)
    if info is None:
        click.echo(f"{key} is not deprecated")
    else:
        click.echo(str(info))


@deprecate_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
def list_cmd(vault_dir):
    """List all deprecated keys."""
    items = list_deprecated(vault_dir)
    if not items:
        click.echo("No deprecated keys.")
        return
    for info in items:
        click.echo(str(info))


@deprecate_cmd.command("check")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def check_cmd(key, vault_dir):
    """Exit with code 1 if KEY is deprecated."""
    if is_deprecated(vault_dir, key):
        info = get_deprecation(vault_dir, key)
        click.echo(str(info), err=True)
        raise SystemExit(1)
    click.echo(f"{key} is not deprecated")
