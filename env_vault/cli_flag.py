"""CLI commands for boolean flag metadata."""
import click
from env_vault.env_flag import set_flag, remove_flag, get_flag, list_flags, keys_with_flag


@click.group("flag")
def flag_cmd():
    """Manage boolean flags on vault keys."""


@flag_cmd.command("set")
@click.argument("key")
@click.argument("value", type=click.BOOL)
@click.option("--vault-dir", default=".", show_default=True)
def set_cmd(key: str, value: bool, vault_dir: str):
    """Set a boolean flag on KEY."""
    changed = set_flag(vault_dir, key, value)
    if changed:
        click.echo(f"Flag '{key}' set to {value}.")
    else:
        click.echo(f"Flag '{key}' unchanged ({value}).")


@flag_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key: str, vault_dir: str):
    """Remove the flag from KEY."""
    if remove_flag(vault_dir, key):
        click.echo(f"Flag removed from '{key}'.")
    else:
        click.echo(f"No flag found for '{key}'.")
        raise SystemExit(1)


@flag_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key: str, vault_dir: str):
    """Get the flag value for KEY."""
    val = get_flag(vault_dir, key)
    if val is None:
        click.echo(f"No flag set for '{key}'.")
        raise SystemExit(1)
    click.echo(str(val))


@flag_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--filter", "filter_val", type=click.BOOL, default=None)
def list_cmd(vault_dir: str, filter_val):
    """List all flags, optionally filtered by value."""
    if filter_val is not None:
        keys = keys_with_flag(vault_dir, filter_val)
        flags = {k: filter_val for k in keys}
    else:
        flags = list_flags(vault_dir)
    if not flags:
        click.echo("No flags set.")
        return
    for k, v in sorted(flags.items()):
        click.echo(f"{k}: {v}")
