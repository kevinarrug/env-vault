"""CLI commands for managing key priority levels."""
import click
from env_vault.env_priority import (
    VALID_PRIORITIES,
    get_priority,
    keys_by_priority,
    list_priorities,
    remove_priority,
    set_priority,
)


@click.group("priority")
def priority_cmd():
    """Manage priority levels for vault keys."""


@priority_cmd.command("set")
@click.argument("key")
@click.argument("priority", type=click.Choice(VALID_PRIORITIES))
@click.option("--vault-dir", default=".", show_default=True)
def set_cmd(key: str, priority: str, vault_dir: str):
    """Assign a priority level to a key."""
    try:
        changed = set_priority(vault_dir, key, priority)
        if changed:
            click.echo(f"Priority for '{key}' set to '{priority}'.")
        else:
            click.echo(f"Priority for '{key}' is already '{priority}'.")
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@priority_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key: str, vault_dir: str):
    """Remove the priority assignment for a key."""
    removed = remove_priority(vault_dir, key)
    if removed:
        click.echo(f"Priority for '{key}' removed.")
    else:
        click.echo(f"No priority set for '{key}'.")


@priority_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key: str, vault_dir: str):
    """Show the priority level for a key."""
    value = get_priority(vault_dir, key)
    if value is None:
        click.echo(f"No priority set for '{key}'.")
    else:
        click.echo(value)


@priority_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--filter", "filter_priority", type=click.Choice(VALID_PRIORITIES), default=None)
def list_cmd(vault_dir: str, filter_priority):
    """List all key priority assignments."""
    if filter_priority:
        keys = keys_by_priority(vault_dir, filter_priority)
        if not keys:
            click.echo(f"No keys with priority '{filter_priority}'.")
        for k in keys:
            click.echo(f"{k}: {filter_priority}")
    else:
        data = list_priorities(vault_dir)
        if not data:
            click.echo("No priorities set.")
        for k, v in sorted(data.items()):
            click.echo(f"{k}: {v}")
