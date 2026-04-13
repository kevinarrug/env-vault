"""CLI commands for inspecting the aggregated status of vault keys."""
from __future__ import annotations

import json

import click

from env_vault.env_status import get_status, get_all_statuses
from env_vault.vault import Vault


@click.group(name="status")
def status_cmd() -> None:
    """Inspect the status of vault keys."""


@status_cmd.command(name="get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def get_cmd(key: str, vault_dir: str, as_json: bool) -> None:
    """Show the status of a single KEY."""
    status = get_status(vault_dir, key)
    if as_json:
        click.echo(json.dumps({
            "key": status.key,
            "locked": status.locked,
            "frozen": status.frozen,
            "expired": status.expired,
            "deprecated": status.deprecated,
            "ttl_remaining": status.ttl_remaining,
            "deprecation_message": status.deprecation_message,
            "expiry_timestamp": status.expiry_timestamp,
            "active": status.active,
        }))
    else:
        click.echo(f"{key}: {status.summary()}")


@status_cmd.command(name="list")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
@click.option("--passphrase", prompt=True, hide_input=True)
@click.option("--only-issues", is_flag=True, help="Show only keys with a non-ok status.")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def list_cmd(vault_dir: str, passphrase: str, only_issues: bool, as_json: bool) -> None:
    """List the status of all keys in the vault."""
    vault = Vault(vault_dir, passphrase)
    keys = vault.list()
    statuses = get_all_statuses(vault_dir, keys)

    if only_issues:
        statuses = [s for s in statuses if not s.active or s.locked or s.frozen or s.ttl_remaining is not None]

    if as_json:
        click.echo(json.dumps([
            {
                "key": s.key,
                "locked": s.locked,
                "frozen": s.frozen,
                "expired": s.expired,
                "deprecated": s.deprecated,
                "ttl_remaining": s.ttl_remaining,
                "active": s.active,
            }
            for s in statuses
        ], indent=2))
    else:
        if not statuses:
            click.echo("No keys found.")
            return
        for s in statuses:
            click.echo(f"  {s.key:<30} {s.summary()}")
