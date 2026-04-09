"""CLI sub-commands for exporting and importing vault variables."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from env_vault.export import SUPPORTED_FORMATS, format_output, import_dotenv, import_json
from env_vault.vault import Vault


@click.command("export")
@click.option(
    "--vault",
    "vault_path",
    default=".env-vault",
    show_default=True,
    help="Path to the vault file.",
)
@click.option(
    "--format",
    "fmt",
    default="dotenv",
    show_default=True,
    type=click.Choice(SUPPORTED_FORMATS),
    help="Output format.",
)
@click.option("--output", "-o", default=None, help="Write output to FILE instead of stdout.")
@click.password_option("--passphrase", prompt="Passphrase", confirmation_prompt=False)
def export_cmd(vault_path: str, fmt: str, output: str | None, passphrase: str) -> None:
    """Decrypt and export all variables from the vault."""
    vault = Vault(vault_path, passphrase)
    vault.load()
    variables = {key: vault.get(key) for key in vault.list_keys()}
    rendered = format_output(variables, fmt)
    if output:
        Path(output).write_text(rendered)
        click.echo(f"Exported {len(variables)} variable(s) to {output}")
    else:
        click.echo(rendered, nl=False)


@click.command("import")
@click.argument("source", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--vault",
    "vault_path",
    default=".env-vault",
    show_default=True,
    help="Path to the vault file.",
)
@click.option(
    "--format",
    "fmt",
    default="dotenv",
    show_default=True,
    type=click.Choice(["dotenv", "json"]),
    help="Input file format.",
)
@click.password_option("--passphrase", prompt="Passphrase", confirmation_prompt=False)
def import_cmd(source: str, vault_path: str, fmt: str, passphrase: str) -> None:
    """Import variables from a file into the vault."""
    content = Path(source).read_text()
    if fmt == "dotenv":
        variables = import_dotenv(content)
    else:
        variables = import_json(content)

    vault = Vault(vault_path, passphrase)
    try:
        vault.load()
    except FileNotFoundError:
        pass

    for key, value in variables.items():
        vault.set(key, value)

    vault.save()
    click.echo(f"Imported {len(variables)} variable(s) into {vault_path}")
