"""CLI commands for resolving cross-references between vault values."""
from __future__ import annotations

import click

from env_vault.vault import Vault
from env_vault.env_resolve import resolve_value, resolve_all


@click.group("resolve")
def resolve_cmd() -> None:
    """Resolve ${KEY} references inside vault values."""


@resolve_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
@click.option("--passphrase", prompt=True, hide_input=True)
def get_cmd(key: str, vault_dir: str, passphrase: str) -> None:
    """Resolve and print the value of KEY after expanding references."""
    vault = Vault(vault_dir, passphrase)
    try:
        raw = vault.get(key)
    except KeyError:
        raise click.ClickException(f"Key '{key}' not found in vault.")

    secrets = {k: vault.get(k) for k in vault.list_keys()}
    result = resolve_value(key, raw, secrets)

    if result.has_unresolved:
        click.echo(
            click.style(
                f"Warning: unresolved references: {', '.join(result.unresolved)}",
                fg="yellow",
            ),
            err=True,
        )
    click.echo(result.resolved)


@resolve_cmd.command("dump")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
@click.option("--passphrase", prompt=True, hide_input=True)
@click.option("--show-unresolved", is_flag=True, help="Highlight unresolved refs.")
def dump_cmd(vault_dir: str, passphrase: str, show_unresolved: bool) -> None:
    """Resolve all vault values and print them."""
    vault = Vault(vault_dir, passphrase)
    keys = vault.list_keys()
    if not keys:
        click.echo("Vault is empty.")
        return

    secrets = {k: vault.get(k) for k in keys}
    results = resolve_all(secrets)

    for k in sorted(results):
        r = results[k]
        if show_unresolved and r.has_unresolved:
            label = click.style(k, fg="yellow")
        else:
            label = k
        click.echo(f"{label}={r.resolved}")
