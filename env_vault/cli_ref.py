"""CLI commands for env-ref (key reference tracking)."""
import click

from env_vault.env_ref import (
    set_ref,
    remove_ref,
    get_ref,
    list_refs,
    resolve_ref,
)
from env_vault.vault import Vault


@click.group("ref")
def ref_cmd():
    """Manage key references (aliases that point to another key's value)."""


@ref_cmd.command("set")
@click.argument("key")
@click.argument("target")
@click.option("--vault-dir", default=".", show_default=True)
def set_cmd(key: str, target: str, vault_dir: str):
    """Set KEY to reference TARGET."""
    try:
        is_new = set_ref(vault_dir, key, target)
    except ValueError as exc:
        raise click.ClickException(str(exc))
    verb = "Added" if is_new else "Updated"
    click.echo(f"{verb} reference: {key} -> {target}")


@ref_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key: str, vault_dir: str):
    """Remove the reference for KEY."""
    if remove_ref(vault_dir, key):
        click.echo(f"Removed reference for '{key}'.")
    else:
        click.echo(f"No reference found for '{key}'.")


@ref_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key: str, vault_dir: str):
    """Show the target key that KEY references."""
    target = get_ref(vault_dir, key)
    if target is None:
        raise click.ClickException(f"No reference set for '{key}'.")
    click.echo(target)


@ref_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
def list_cmd(vault_dir: str):
    """List all key references."""
    refs = list_refs(vault_dir)
    if not refs:
        click.echo("No references defined.")
        return
    for key, target in sorted(refs.items()):
        click.echo(f"  {key} -> {target}")


@ref_cmd.command("resolve")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--passphrase", prompt=True, hide_input=True)
def resolve_cmd(key: str, vault_dir: str, passphrase: str):
    """Resolve KEY through its reference chain and print the final value."""
    vault = Vault(vault_dir, passphrase)
    value = resolve_ref(vault_dir, key, vault)
    if value is None:
        raise click.ClickException(f"Could not resolve value for '{key}'.")
    click.echo(value)
