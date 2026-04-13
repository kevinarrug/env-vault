"""CLI commands for managing key-change triggers."""
import click

from env_vault.env_trigger import (
    add_trigger,
    clear_triggers,
    get_triggers,
    list_all_triggers,
    remove_trigger,
)


@click.group("trigger")
def trigger_cmd() -> None:
    """Manage shell triggers fired when a key changes."""


@trigger_cmd.command("add")
@click.argument("key")
@click.argument("command")
@click.option("--vault-dir", default=".", show_default=True)
def add_cmd(key: str, command: str, vault_dir: str) -> None:
    """Register COMMAND to run when KEY changes."""
    added = add_trigger(vault_dir, key, command)
    if added:
        click.echo(f"Trigger added for '{key}'.")
    else:
        click.echo(f"Trigger already registered for '{key}'.")


@trigger_cmd.command("remove")
@click.argument("key")
@click.argument("command")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key: str, command: str, vault_dir: str) -> None:
    """Remove COMMAND from KEY's trigger list."""
    removed = remove_trigger(vault_dir, key, command)
    if removed:
        click.echo(f"Trigger removed from '{key}'.")
    else:
        click.echo(f"Trigger not found for '{key}'.")


@trigger_cmd.command("list")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def list_cmd(key: str, vault_dir: str) -> None:
    """List all triggers registered for KEY."""
    cmds = get_triggers(vault_dir, key)
    if not cmds:
        click.echo(f"No triggers registered for '{key}'.")
    else:
        for cmd in cmds:
            click.echo(cmd)


@trigger_cmd.command("list-all")
@click.option("--vault-dir", default=".", show_default=True)
def list_all_cmd(vault_dir: str) -> None:
    """List every key that has at least one trigger."""
    mapping = list_all_triggers(vault_dir)
    if not mapping:
        click.echo("No triggers defined.")
    else:
        for key, cmds in sorted(mapping.items()):
            click.echo(f"{key}: {len(cmds)} trigger(s)")


@trigger_cmd.command("clear")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def clear_cmd(key: str, vault_dir: str) -> None:
    """Remove all triggers for KEY."""
    n = clear_triggers(vault_dir, key)
    click.echo(f"Cleared {n} trigger(s) for '{key}'.")
