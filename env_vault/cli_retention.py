"""CLI commands for retention policy management."""
import click
from env_vault.env_retention import (
    set_retention,
    remove_retention,
    get_retention,
    list_retention,
    expired_keys,
)


@click.group("retention")
def retention_cmd():
    """Manage retention policies for vault keys."""


@retention_cmd.command("set")
@click.argument("key")
@click.argument("days", type=int)
@click.option("--vault-dir", default=".", show_default=True)
def set_cmd(key: str, days: int, vault_dir: str):
    """Set a retention policy of DAYS days for KEY."""
    try:
        is_new = set_retention(vault_dir, key, days)
    except ValueError as exc:
        raise click.ClickException(str(exc))
    action = "Set" if is_new else "Updated"
    click.echo(f"{action} retention for '{key}': {days} day(s).")


@retention_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key: str, vault_dir: str):
    """Remove the retention policy for KEY."""
    removed = remove_retention(vault_dir, key)
    if removed:
        click.echo(f"Removed retention policy for '{key}'.")
    else:
        click.echo(f"No retention policy found for '{key}'.")


@retention_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key: str, vault_dir: str):
    """Show the retention policy for KEY."""
    info = get_retention(vault_dir, key)
    if info is None:
        click.echo(f"No retention policy set for '{key}'.")
        raise SystemExit(1)
    click.echo(f"{key}: {info['days']} day(s)")


@retention_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--expired", is_flag=True, help="Show only expired keys.")
def list_cmd(vault_dir: str, expired: bool):
    """List all retention policies."""
    if expired:
        keys = expired_keys(vault_dir)
        if not keys:
            click.echo("No expired keys.")
            return
        for k in keys:
            click.echo(k)
        return
    policies = list_retention(vault_dir)
    if not policies:
        click.echo("No retention policies defined.")
        return
    for key, info in sorted(policies.items()):
        click.echo(f"{key}: {info['days']} day(s)")
