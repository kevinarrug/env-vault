"""CLI commands for managing key sensitivity levels."""
import click

from env_vault.env_sensitivity import (
    LEVELS,
    get_sensitivity,
    keys_at_level,
    list_sensitivity,
    remove_sensitivity,
    set_sensitivity,
)


@click.group("sensitivity")
def sensitivity_cmd() -> None:
    """Manage sensitivity levels for vault keys."""


@sensitivity_cmd.command("set")
@click.argument("key")
@click.argument("level", type=click.Choice(LEVELS))
@click.option("--vault-dir", default=".", show_default=True)
def set_cmd(key: str, level: str, vault_dir: str) -> None:
    """Assign a sensitivity LEVEL to KEY."""
    try:
        changed = set_sensitivity(vault_dir, key, level)
        if changed:
            click.echo(f"Set '{key}' sensitivity to '{level}'.")
        else:
            click.echo(f"'{key}' already at level '{level}' — no change.")
    except ValueError as exc:
        raise click.ClickException(str(exc))


@sensitivity_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key: str, vault_dir: str) -> None:
    """Remove the sensitivity level for KEY."""
    if remove_sensitivity(vault_dir, key):
        click.echo(f"Removed sensitivity level for '{key}'.")
    else:
        click.echo(f"No sensitivity level set for '{key}'.")


@sensitivity_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key: str, vault_dir: str) -> None:
    """Get the sensitivity level for KEY."""
    level = get_sensitivity(vault_dir, key)
    if level is None:
        click.echo(f"No sensitivity level set for '{key}'.")
    else:
        click.echo(f"{key}: {level}")


@sensitivity_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--level", type=click.Choice(LEVELS), default=None, help="Filter by level.")
def list_cmd(vault_dir: str, level: str) -> None:
    """List all sensitivity assignments, optionally filtered by LEVEL."""
    if level:
        keys = keys_at_level(vault_dir, level)
        if not keys:
            click.echo(f"No keys at level '{level}'.")
        else:
            for k in keys:
                click.echo(f"{k}: {level}")
    else:
        data = list_sensitivity(vault_dir)
        if not data:
            click.echo("No sensitivity levels assigned.")
        else:
            for k, v in sorted(data.items()):
                click.echo(f"{k}: {v}")
