"""CLI commands for type-casting vault values."""

from __future__ import annotations

import json
import click

from env_vault.vault import Vault
from env_vault.env_cast import cast_key, cast_all, _SUPPORTED_TYPES


@click.group("cast")
def cast_cmd():
    """Cast vault values to Python types."""


@cast_cmd.command("get")
@click.argument("vault_dir")
@click.argument("key")
@click.argument("cast_type", type=click.Choice(list(_SUPPORTED_TYPES)))
@click.option("--passphrase", envvar="ENV_VAULT_PASSPHRASE", prompt=True, hide_input=True)
def get_cmd(vault_dir: str, key: str, cast_type: str, passphrase: str):
    """Retrieve KEY from vault and cast to CAST_TYPE."""
    vault = Vault(vault_dir)
    result = cast_key(vault, key, cast_type, passphrase)
    if result.success:
        click.echo(f"{result.key} ({result.cast_type}): {result.value!r}")
    else:
        click.echo(f"Error: {result.error}", err=True)
        raise SystemExit(1)


@cast_cmd.command("apply")
@click.argument("vault_dir")
@click.argument("schema_file", type=click.Path(exists=True))
@click.option("--passphrase", envvar="ENV_VAULT_PASSPHRASE", prompt=True, hide_input=True)
@click.option("--json", "as_json", is_flag=True, default=False, help="Output as JSON.")
def apply_cmd(vault_dir: str, schema_file: str, passphrase: str, as_json: bool):
    """Cast all keys in SCHEMA_FILE (JSON {key: type}) and display results."""
    with open(schema_file) as fh:
        schema = json.load(fh)

    vault = Vault(vault_dir)
    results = cast_all(vault, schema, passphrase)

    if as_json:
        out = {}
        for r in results:
            out[r.key] = {"value": r.value, "type": r.cast_type, "success": r.success}
            if not r.success:
                out[r.key]["error"] = r.error
        click.echo(json.dumps(out, indent=2))
    else:
        for r in results:
            if r.success:
                click.echo(str(r))
            else:
                click.echo(f"ERROR  {r}", err=True)

    if any(not r.success for r in results):
        raise SystemExit(1)
