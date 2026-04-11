"""CLI commands for schema validation."""
from __future__ import annotations

import json
import sys

import click

from env_vault.env_schema import SchemaRule, validate
from env_vault.vault import Vault


@click.group("schema")
def schema_cmd() -> None:
    """Validate vault keys against a JSON schema definition."""


@schema_cmd.command("check")
@click.argument("vault_dir")
@click.argument("schema_file", type=click.Path(exists=True))
@click.option("--passphrase", envvar="VAULT_PASSPHRASE", prompt=True, hide_input=True)
@click.option("--strict", is_flag=True, help="Exit non-zero on warnings too.")
def check_cmd(vault_dir: str, schema_file: str, passphrase: str, strict: bool) -> None:
    """Check vault contents against SCHEMA_FILE (JSON)."""
    with open(schema_file) as fh:
        raw = json.load(fh)

    if not isinstance(raw, list):
        click.echo("Schema file must contain a JSON array of rule objects.", err=True)
        sys.exit(2)

    rules = []
    for item in raw:
        rules.append(
            SchemaRule(
                key=item["key"],
                required=item.get("required", False),
                pattern=item.get("pattern"),
                min_length=item.get("min_length"),
                max_length=item.get("max_length"),
                description=item.get("description", ""),
            )
        )

    vault = Vault(vault_dir, passphrase)
    vault_data = {k: vault.get(k) for k in vault.list()}

    result = validate(vault_data, rules)
    click.echo(result.summary())

    if not result.passed:
        sys.exit(1)


@schema_cmd.command("show")
@click.argument("schema_file", type=click.Path(exists=True))
def show_cmd(schema_file: str) -> None:
    """Pretty-print the rules defined in SCHEMA_FILE."""
    with open(schema_file) as fh:
        raw = json.load(fh)

    if not raw:
        click.echo("No rules defined.")
        return

    for item in raw:
        flags = []
        if item.get("required"):
            flags.append("required")
        if item.get("pattern"):
            flags.append(f"pattern={item['pattern']}")
        if item.get("min_length") is not None:
            flags.append(f"min={item['min_length']}")
        if item.get("max_length") is not None:
            flags.append(f"max={item['max_length']}")
        flag_str = f"  [{', '.join(flags)}]" if flags else ""
        desc = f"  # {item['description']}" if item.get("description") else ""
        click.echo(f"{item['key']}{flag_str}{desc}")
