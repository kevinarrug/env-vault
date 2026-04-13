"""CLI commands for env-vault visibility management."""
import click
from env_vault.env_visibility import (
    set_visibility,
    get_visibility,
    remove_visibility,
    list_visibility,
    keys_with_level,
    VALID_LEVELS,
)


@click.group("visibility")
def visibility_cmd() -> None:
    """Manage key visibility levels (public / private / internal)."""


@visibility_cmd.command("set")
@click.argument("key")
@click.argument("level", type=click.Choice(list(VALID_LEVELS)))
@click.option("--vault-dir", default=".", show_default=True)
def set_cmd(key: str, level: str, vault_dir: str) -> None:
    """Set visibility LEVEL for KEY."""
    changed = set_visibility(vault_dir, key, level)
    if changed:
        click.echo(f"Set '{key}' visibility to '{level}'.")
    else:
        click.echo(f"'{key}' visibility already '{level}' — no change.")


@visibility_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key: str, vault_dir: str) -> None:
    """Remove visibility setting for KEY."""
    if remove_visibility(vault_dir, key):
        click.echo(f"Removed visibility setting for '{key}'.")
    else:
        click.echo(f"No visibility setting found for '{key}'.")


@visibility_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key: str, vault_dir: str) -> None:
    """Get visibility level for KEY."""
    level = get_visibility(vault_dir, key)
    if level is None:
        click.echo(f"No visibility set for '{key}'.")
        raise SystemExit(1)
    click.echo(level)


@visibility_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--level", type=click.Choice(list(VALID_LEVELS)), default=None)
def list_cmd(vault_dir: str, level: str) -> None:
    """List all visibility settings, optionally filtered by LEVEL."""
    if level:
        keys = keys_with_level(vault_dir, level)
        if not keys:
            click.echo(f"No keys with visibility '{level}'.")
        else:
            for k in sorted(keys):
                click.echo(f"{k}: {level}")
    else:
        data = list_visibility(vault_dir)
        if not data:
            click.echo("No visibility settings defined.")
        else:
            for k, v in sorted(data.items()):
                click.echo(f"{k}: {v}")
