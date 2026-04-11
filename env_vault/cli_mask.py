"""CLI commands for masking/redacting vault values."""
from __future__ import annotations

import click

from env_vault.vault import Vault
from env_vault.env_mask import mask_key, mask_all


@click.group("mask")
def mask_cmd() -> None:
    """Mask or redact sensitive vault values."""


@mask_cmd.command("get")
@click.argument("vault_dir")
@click.argument("key")
@click.option("--passphrase", "-p", required=True, help="Vault passphrase.")
@click.option(
    "--mode",
    "-m",
    default="full",
    show_default=True,
    type=click.Choice(["full", "partial", "none"]),
    help="Masking mode.",
)
def get_cmd(vault_dir: str, key: str, passphrase: str, mode: str) -> None:
    """Print a single masked value for KEY."""
    vault = Vault(vault_dir)
    try:
        result = mask_key(vault, passphrase, key, mode)
    except KeyError:
        raise click.ClickException(f"Key not found: {key}")
    except ValueError as exc:
        raise click.ClickException(str(exc))
    click.echo(f"{result.key}={result.masked}")


@mask_cmd.command("dump")
@click.argument("vault_dir")
@click.option("--passphrase", "-p", required=True, help="Vault passphrase.")
@click.option(
    "--mode",
    "-m",
    default="full",
    show_default=True,
    type=click.Choice(["full", "partial", "none"]),
    help="Masking mode.",
)
@click.option("--reveal", is_flag=True, default=False, help="Show original values too.")
def dump_cmd(vault_dir: str, passphrase: str, mode: str, reveal: bool) -> None:
    """Dump all vault keys with masked values."""
    vault = Vault(vault_dir)
    results = mask_all(vault, passphrase, mode)
    if not results:
        click.echo("(vault is empty)")
        return
    for r in results:
        if reveal:
            click.echo(f"{r.key}={r.masked}  # {r.original}")
        else:
            click.echo(f"{r.key}={r.masked}")
