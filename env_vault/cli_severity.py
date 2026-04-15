"""CLI commands for managing key severity levels."""

from __future__ import annotations

import click

from env_vault.env_severity import (
    VALID_LEVELS,
    get_severity,
    keys_by_level,
    list_severity,
    remove_severity,
    set_severity,
)


@click.group("severity")
def severity_cmd():
    """Manage severity levels for vault keys."""


@severity_cmd.command("set")
@click.argument("key")
@click.argument("level", type=click.Choice(sorted(VALID_LEVELS), case_sensitive=False))
@click.option("--vault-dir", default=".", show_default=True)
def set_cmd(key: str, level: str, vault_dir: str):
    """Set severity level for KEY."""
    level = level.lower()
    changed = set_severity(vault_dir, key, level)
    if changed:
        click.echo(f"Set severity of '{key}' to '{level}'.")
    else:
        click.echo(f"Severity of '{key}' is already '{level}'. No change.")


@severity_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key: str, vault_dir: str):
    """Remove severity level for KEY."""
    removed = remove_severity(vault_dir, key)
    if removed:
        click.echo(f"Removed severity for '{key}'.")
    else:
        click.echo(f"No severity set for '{key}'.")


@severity_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key: str, vault_dir: str):
    """Get severity level for KEY."""
    level = get_severity(vault_dir, key)
    if level is None:
        click.echo(f"No severity set for '{key}'.")
        raise SystemExit(1)
    click.echo(level)


@severity_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--level", type=click.Choice(sorted(VALID_LEVELS), case_sensitive=False), default=None)
def list_cmd(vault_dir: str, level: str | None):
    """List severity levels, optionally filtered by LEVEL."""
    if level:
        keys = keys_by_level(vault_dir, level.lower())
        if not keys:
            click.echo(f"No keys with severity '{level}'.")
        else:
            for k in keys:
                click.echo(f"{k}: {level}")
    else:
        data = list_severity(vault_dir)
        if not data:
            click.echo("No severity levels set.")
        else:
            for k, v in sorted(data.items()):
                click.echo(f"{k}: {v}")
