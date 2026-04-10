"""CLI commands for managing key pins."""

from __future__ import annotations

import click

from env_vault.pin import (
    check_pin,
    get_pin,
    list_pins,
    pin_key,
    unpin_key,
    validate_all,
)
from env_vault.vault import Vault


@click.group("pin")
def pin_cmd() -> None:
    """Pin keys to required value patterns."""


@pin_cmd.command("set")
@click.argument("key")
@click.argument("pattern")
@click.option("--vault-dir", default=".", show_default=True)
def set_cmd(key: str, pattern: str, vault_dir: str) -> None:
    """Pin KEY to a regex PATTERN."""
    is_new = pin_key(vault_dir, key, pattern)
    verb = "Pinned" if is_new else "Updated pin for"
    click.echo(f"{verb} '{key}' → {pattern}")


@pin_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key: str, vault_dir: str) -> None:
    """Remove the pin for KEY."""
    if unpin_key(vault_dir, key):
        click.echo(f"Removed pin for '{key}'.")
    else:
        click.echo(f"No pin found for '{key}'.")


@pin_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key: str, vault_dir: str) -> None:
    """Show the pin pattern for KEY."""
    pattern = get_pin(vault_dir, key)
    if pattern is None:
        click.echo(f"'{key}' is not pinned.")
    else:
        click.echo(f"{key}: {pattern}")


@pin_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
def list_cmd(vault_dir: str) -> None:
    """List all pinned keys and their patterns."""
    pins = list_pins(vault_dir)
    if not pins:
        click.echo("No pins defined.")
        return
    for key, pattern in sorted(pins.items()):
        click.echo(f"  {key}: {pattern}")


@pin_cmd.command("check")
@click.argument("key")
@click.argument("value")
@click.option("--vault-dir", default=".", show_default=True)
def check_cmd(key: str, value: str, vault_dir: str) -> None:
    """Check if VALUE satisfies the pin pattern for KEY."""
    if check_pin(vault_dir, key, value):
        click.echo(f"OK: '{value}' satisfies pin for '{key}'.")
    else:
        pattern = get_pin(vault_dir, key)
        click.echo(f"FAIL: '{value}' does not match pattern '{pattern}' for '{key}'.")
        raise SystemExit(1)


@pin_cmd.command("validate")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--passphrase", prompt=True, hide_input=True)
def validate_cmd(vault_dir: str, passphrase: str) -> None:
    """Validate all vault values against their pins."""
    vault = Vault(vault_dir, passphrase)
    secrets = {k: vault.get(k) for k in vault.list()}
    violations = validate_all(vault_dir, secrets)
    if not violations:
        click.echo("All pinned keys pass validation.")
    else:
        for key, pattern in sorted(violations.items()):
            click.echo(f"  FAIL {key}: must match '{pattern}'")
        raise SystemExit(1)
