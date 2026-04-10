"""CLI commands for merging vaults."""

from __future__ import annotations

import click

from env_vault.merge import ConflictStrategy, MergeConflictError, merge_vaults
from env_vault.vault import Vault


@click.group("merge")
def merge_cmd() -> None:
    """Merge keys from one vault into another."""


@merge_cmd.command("apply")
@click.argument("base_dir", type=click.Path(exists=True, file_okay=False))
@click.argument("other_dir", type=click.Path(exists=True, file_okay=False))
@click.password_option("--passphrase", "-p", prompt="Passphrase", help="Shared passphrase for both vaults.")
@click.option(
    "--strategy",
    "-s",
    type=click.Choice([s.value for s in ConflictStrategy], case_sensitive=False),
    default=ConflictStrategy.OURS.value,
    show_default=True,
    help="Conflict resolution strategy.",
)
@click.option("--quiet", "-q", is_flag=True, help="Suppress per-key output.")
def apply_cmd(
    base_dir: str,
    other_dir: str,
    passphrase: str,
    strategy: str,
    quiet: bool,
) -> None:
    """Merge OTHER_DIR vault into BASE_DIR vault."""
    base_vault = Vault(base_dir)
    other_vault = Vault(other_dir)
    strat = ConflictStrategy(strategy.lower())

    try:
        result = merge_vaults(base_vault, other_vault, passphrase, strategy=strat)
    except MergeConflictError as exc:
        raise click.ClickException(str(exc)) from exc

    if not quiet:
        for key in result.added:
            click.echo(f"  + {key}")
        for key in result.updated:
            click.echo(f"  ~ {key}")
        for conflict in result.conflicts:
            click.echo(f"  ! {conflict}", err=True)

    click.echo(result.summary())
