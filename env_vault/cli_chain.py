"""cli_chain.py — CLI commands for vault chain resolution."""
from __future__ import annotations

import json
import click

from env_vault.env_chain import resolve, resolve_all


@click.group("chain")
def chain_cmd() -> None:
    """Resolve keys across a chain of vaults."""


@chain_cmd.command("get")
@click.argument("key")
@click.option(
    "--vault", "vault_dirs", multiple=True, required=True,
    help="Vault directory (repeatable, checked in order).",
)
@click.option("--passphrase", envvar="ENV_VAULT_PASS", prompt=True, hide_input=True)
@click.option("--json", "as_json", is_flag=True, default=False)
def get_cmd(key: str, vault_dirs: tuple, passphrase: str, as_json: bool) -> None:
    """Resolve KEY from the first vault that contains it."""
    result = resolve(key, list(vault_dirs), passphrase)
    if as_json:
        click.echo(json.dumps({
            "key": result.key,
            "value": result.value,
            "source": result.source,
            "found": result.found,
        }))
    elif result.found:
        click.echo(result.value)
    else:
        click.echo(str(result), err=True)
        raise SystemExit(1)


@chain_cmd.command("dump")
@click.option(
    "--vault", "vault_dirs", multiple=True, required=True,
    help="Vault directory (repeatable, checked in order).",
)
@click.option("--passphrase", envvar="ENV_VAULT_PASS", prompt=True, hide_input=True)
@click.option("--json", "as_json", is_flag=True, default=False)
def dump_cmd(vault_dirs: tuple, passphrase: str, as_json: bool) -> None:
    """Dump all resolved key-value pairs across the chain."""
    results = resolve_all(list(vault_dirs), passphrase)
    if as_json:
        click.echo(json.dumps(
            {k: {"value": r.value, "source": r.source} for k, r in sorted(results.items())},
            indent=2,
        ))
    else:
        for key, result in sorted(results.items()):
            click.echo(f"{key}={result.value!r}  # {result.source}")
