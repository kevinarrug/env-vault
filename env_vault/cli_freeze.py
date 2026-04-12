"""CLI commands for freeze/unfreeze vault keys."""

import click

from env_vault.env_freeze import freeze_key, unfreeze_key, is_frozen, list_frozen


@click.group("freeze")
def freeze_cmd():
    """Freeze or unfreeze vault keys to prevent modification."""


@freeze_cmd.command("set")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def set_cmd(key: str, vault_dir: str):
    """Freeze KEY so it cannot be modified."""
    added = freeze_key(vault_dir, key)
    if added:
        click.echo(f"Key '{key}' is now frozen.")
    else:
        click.echo(f"Key '{key}' was already frozen.")


@freeze_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def remove_cmd(key: str, vault_dir: str):
    """Unfreeze KEY to allow modification."""
    removed = unfreeze_key(vault_dir, key)
    if removed:
        click.echo(f"Key '{key}' has been unfrozen.")
    else:
        click.echo(f"Key '{key}' was not frozen.")


@freeze_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def get_cmd(key: str, vault_dir: str):
    """Check whether KEY is frozen."""
    frozen = is_frozen(vault_dir, key)
    state = "frozen" if frozen else "not frozen"
    click.echo(f"Key '{key}' is {state}.")


@freeze_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def list_cmd(vault_dir: str):
    """List all frozen keys."""
    keys = list_frozen(vault_dir)
    if not keys:
        click.echo("No frozen keys.")
    else:
        for k in keys:
            click.echo(k)
