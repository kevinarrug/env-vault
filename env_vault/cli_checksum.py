"""CLI commands for checksum management."""
import click
from env_vault.vault import Vault
from env_vault.env_checksum import (
    record_checksum, get_checksum, remove_checksum,
    verify_checksum, verify_all,
)


@click.group("checksum")
def checksum_cmd():
    """Manage and verify key checksums."""


@checksum_cmd.command("record")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--passphrase", envvar="VAULT_PASSPHRASE", prompt=True, hide_input=True)
def record_cmd(key, vault_dir, passphrase):
    """Record checksum for KEY's current value."""
    v = Vault(vault_dir, passphrase)
    value = v.get(key)
    digest = record_checksum(vault_dir, key, value)
    click.echo(f"Recorded checksum for '{key}': {digest[:16]}...")


@checksum_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key, vault_dir):
    """Show stored checksum for KEY."""
    digest = get_checksum(vault_dir, key)
    if digest is None:
        click.echo(f"No checksum recorded for '{key}'.")
        raise SystemExit(1)
    click.echo(digest)


@checksum_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key, vault_dir):
    """Remove stored checksum for KEY."""
    removed = remove_checksum(vault_dir, key)
    if removed:
        click.echo(f"Removed checksum for '{key}'.")
    else:
        click.echo(f"No checksum found for '{key}'.")


@checksum_cmd.command("verify")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--passphrase", envvar="VAULT_PASSPHRASE", prompt=True, hide_input=True)
def verify_cmd(key, vault_dir, passphrase):
    """Verify checksum for KEY against its current value."""
    v = Vault(vault_dir, passphrase)
    value = v.get(key)
    result = verify_checksum(vault_dir, key, value)
    click.echo(str(result))
    if result.tampered:
        raise SystemExit(1)


@checksum_cmd.command("verify-all")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--passphrase", envvar="VAULT_PASSPHRASE", prompt=True, hide_input=True)
def verify_all_cmd(vault_dir, passphrase):
    """Verify checksums for all tracked keys."""
    v = Vault(vault_dir, passphrase)
    keys = v.list_keys()
    values = {k: v.get(k) for k in keys}
    results = verify_all(vault_dir, values)
    if not results:
        click.echo("No checksums recorded.")
        return
    any_tampered = False
    for r in results:
        click.echo(str(r))
        if r.tampered:
            any_tampered = True
    if any_tampered:
        raise SystemExit(1)
