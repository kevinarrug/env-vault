"""CLI commands for vault backup and restore."""

from __future__ import annotations

import click

from env_vault.backup import (
    create_backup,
    delete_backup,
    list_backups,
    purge_backups,
    restore_backup,
)


@click.group("backup")
def backup_cmd() -> None:
    """Manage vault backups."""


@backup_cmd.command("create")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
@click.option("--label", default=None, help="Optional label appended to the backup filename.")
def create_cmd(vault_dir: str, label: str | None) -> None:
    """Create a snapshot of the current vault."""
    try:
        path = create_backup(vault_dir, label=label)
        click.echo(f"Backup created: {path}")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))


@backup_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def list_cmd(vault_dir: str) -> None:
    """List all available backups."""
    backups = list_backups(vault_dir)
    if not backups:
        click.echo("No backups found.")
        return
    for p in backups:
        click.echo(str(p))


@backup_cmd.command("restore")
@click.argument("backup_path")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def restore_cmd(backup_path: str, vault_dir: str) -> None:
    """Restore the vault from BACKUP_PATH."""
    try:
        restore_backup(vault_dir, backup_path)
        click.echo(f"Vault restored from {backup_path}")
    except (FileNotFoundError, ValueError) as exc:
        raise click.ClickException(str(exc))


@backup_cmd.command("delete")
@click.argument("backup_path")
def delete_cmd(backup_path: str) -> None:
    """Delete a specific backup file."""
    try:
        delete_backup(backup_path)
        click.echo(f"Deleted backup: {backup_path}")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))


@backup_cmd.command("purge")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
@click.option("--keep", default=5, show_default=True, help="Number of recent backups to keep.")
def purge_cmd(vault_dir: str, keep: int) -> None:
    """Purge old backups, keeping the most recent ones."""
    deleted = purge_backups(vault_dir, keep=keep)
    if deleted:
        for p in deleted:
            click.echo(f"Deleted: {p}")
        click.echo(f"{len(deleted)} backup(s) removed.")
    else:
        click.echo("Nothing to purge.")
