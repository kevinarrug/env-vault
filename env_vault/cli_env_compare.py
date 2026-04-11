"""CLI commands for comparing vault contents against the live environment."""
from __future__ import annotations

import json
import os

import click

from env_vault.env_compare import compare_vault_to_env
from env_vault.vault import Vault


@click.group(name="compare-env")
def compare_env_cmd() -> None:
    """Compare vault keys with the live environment."""


@compare_env_cmd.command(name="run")
@click.argument("vault_dir")
@click.option("--passphrase", envvar="ENV_VAULT_PASSPHRASE", prompt=True, hide_input=True)
@click.option("--only-mismatches", is_flag=True, default=False, help="Show only mismatches.")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text")
def run_cmd(vault_dir: str, passphrase: str, only_mismatches: bool, fmt: str) -> None:
    """Compare vault values against the current process environment."""
    vault = Vault(vault_dir)
    result = compare_vault_to_env(vault, passphrase)

    entries = result.mismatches if only_mismatches else result.entries

    if fmt == "json":
        data = [
            {
                "key": e.key,
                "status": e.status,
                "vault_value": e.vault_value,
                "env_value": e.env_value,
            }
            for e in entries
        ]
        click.echo(json.dumps(data, indent=2))
        return

    if not entries:
        click.echo("No keys to display.")
        return

    for entry in entries:
        status_color = {
            "match": "green",
            "mismatch": "red",
            "vault_only": "yellow",
            "env_only": "cyan",
        }.get(entry.status, "white")
        click.echo(
            f"{entry.key}: " + click.style(entry.status.upper(), fg=status_color)
        )

    click.echo()
    click.echo(result.summary())
    if not result.all_match:
        raise SystemExit(1)


@compare_env_cmd.command(name="summary")
@click.argument("vault_dir")
@click.option("--passphrase", envvar="ENV_VAULT_PASSPHRASE", prompt=True, hide_input=True)
def summary_cmd(vault_dir: str, passphrase: str) -> None:
    """Print a one-line summary of vault vs environment differences."""
    vault = Vault(vault_dir)
    result = compare_vault_to_env(vault, passphrase)
    click.echo(result.summary())
