"""CLI commands for env-vault transform feature."""
from __future__ import annotations

import click

from env_vault.env_transform import (
    list_transforms,
    transform_and_save,
    transform_key,
)
from env_vault.vault import Vault


@click.group("transform")
def transform_cmd() -> None:
    """Apply transformation pipelines to vault values."""


@transform_cmd.command("apply")
@click.argument("vault_dir")
@click.argument("key")
@click.option("--passphrase", prompt=True, hide_input=True)
@click.option(
    "--step",
    "pipeline",
    multiple=True,
    required=True,
    help="Transform step (repeatable, applied in order).",
)
@click.option("--dry-run", is_flag=True, default=False, help="Preview without saving.")
def apply_cmd(
    vault_dir: str, key: str, passphrase: str, pipeline: tuple, dry_run: bool
) -> None:
    """Apply transform pipeline to KEY and optionally save the result."""
    vault = Vault(vault_dir)
    steps = list(pipeline)
    if dry_run:
        result = transform_key(vault, passphrase, key, steps)
        if result.ok:
            click.echo(f"Preview: {result.original!r} -> {result.transformed!r}")
        else:
            click.echo(f"Error: {result.error}", err=True)
            raise SystemExit(1)
    else:
        result = transform_and_save(vault, passphrase, key, steps)
        if result.ok:
            click.echo(f"Transformed and saved '{key}'.")
        else:
            click.echo(f"Error: {result.error}", err=True)
            raise SystemExit(1)


@transform_cmd.command("preview")
@click.argument("vault_dir")
@click.argument("key")
@click.option("--passphrase", prompt=True, hide_input=True)
@click.option("--step", "pipeline", multiple=True, required=True)
def preview_cmd(
    vault_dir: str, key: str, passphrase: str, pipeline: tuple
) -> None:
    """Preview the result of a pipeline without modifying the vault."""
    vault = Vault(vault_dir)
    result = transform_key(vault, passphrase, key, list(pipeline))
    click.echo(str(result))
    if not result.ok:
        raise SystemExit(1)


@transform_cmd.command("list")
def list_cmd() -> None:
    """List all available transform names."""
    for name in list_transforms():
        click.echo(name)
