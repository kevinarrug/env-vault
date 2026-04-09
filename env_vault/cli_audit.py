"""CLI commands for the audit log feature."""

import json
from datetime import datetime

import click

from env_vault.audit import clear_audit_log, get_audit_log


@click.group("audit")
def audit_cmd():
    """Inspect and manage the vault audit log."""


@audit_cmd.command("log")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
@click.option("--key", default=None, help="Filter by variable name.")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def log_cmd(vault_dir: str, key: str, as_json: bool):
    """Show audit log entries."""
    entries = get_audit_log(vault_dir, key=key)
    if not entries:
        click.echo("No audit entries found.")
        return
    if as_json:
        click.echo(json.dumps(entries, indent=2))
        return
    for entry in entries:
        ts = datetime.fromtimestamp(entry["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        click.echo(f"[{ts}] {entry['action']:10s}  {entry['key']:30s}  actor={entry['actor']}")


@audit_cmd.command("clear")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
@click.confirmation_option(prompt="Clear all audit entries?")
def clear_cmd(vault_dir: str):
    """Delete all audit log entries."""
    count = clear_audit_log(vault_dir)
    click.echo(f"Cleared {count} audit entries.")
