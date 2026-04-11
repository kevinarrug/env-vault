"""CLI commands for formatting/normalising vault values."""

from __future__ import annotations

import click

from env_vault.vault import Vault
from env_vault.env_fmt import apply_format, fmt_key, fmt_all, _FORMATTERS


@click.group("fmt")
def fmt_cmd():
    """Format and normalise environment variable values."""


@fmt_cmd.command("apply")
@click.argument("vault_dir")
@click.argument("passphrase")
@click.argument("key")
@click.option(
    "--format", "fmt",
    required=True,
    type=click.Choice(list(_FORMATTERS)),
    help="Formatter to apply.",
)
def apply_cmd(vault_dir: str, passphrase: str, key: str, fmt: str):
    """Apply a formatter to a single KEY in the vault."""
    vault = Vault(vault_dir)
    vault.load()
    try:
        result = fmt_key(vault, passphrase, key, fmt)
    except KeyError:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)
    if result.changed:
        click.echo(f"Reformatted '{key}': '{result.original}' -> '{result.formatted}'")
    else:
        click.echo(f"'{key}' already formatted; no change.")


@fmt_cmd.command("apply-all")
@click.argument("vault_dir")
@click.argument("passphrase")
@click.option(
    "--format", "fmt",
    required=True,
    type=click.Choice(list(_FORMATTERS)),
    help="Formatter to apply.",
)
@click.option("--dry-run", is_flag=True, help="Preview changes without saving.")
def apply_all_cmd(vault_dir: str, passphrase: str, fmt: str, dry_run: bool):
    """Apply a formatter to ALL keys in the vault."""
    vault = Vault(vault_dir)
    vault.load()
    if dry_run:
        for key in vault.list_keys():
            original = vault.get(key, passphrase)
            formatted = apply_format(original, fmt)
            status = "would change" if formatted != original else "no change"
            click.echo(f"  {key}: {status}")
        return
    report = fmt_all(vault, passphrase, fmt)
    click.echo(report.summary())
    for key in report.changed_keys:
        click.echo(f"  reformatted: {key}")
