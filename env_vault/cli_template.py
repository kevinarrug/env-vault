"""CLI commands for template rendering."""
from __future__ import annotations

import sys

import click

from env_vault.template import render_file, render_template
from env_vault.vault import Vault


@click.group("template")
def template_cmd() -> None:
    """Render templates using vault values."""


@template_cmd.command("render")
@click.argument("template_file", type=click.Path(exists=True))
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
@click.option("--passphrase", envvar="ENV_VAULT_PASS", prompt=True, hide_input=True)
@click.option("--output", "-o", default="-", help="Output file (default: stdout).")
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with error if any placeholder is missing.",
)
def render_cmd(
    template_file: str,
    vault_dir: str,
    passphrase: str,
    output: str,
    strict: bool,
) -> None:
    """Render TEMPLATE_FILE substituting {{ KEY }} placeholders from the vault."""
    vault = Vault(vault_dir)
    try:
        result = render_file(template_file, vault, passphrase, strict=strict)
    except KeyError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if result.has_missing:
        click.echo(
            f"Warning: {len(result.missing)} placeholder(s) not resolved: "
            + ", ".join(result.missing),
            err=True,
        )

    if output == "-":
        click.echo(result.rendered, nl=False)
    else:
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(result.rendered)
        click.echo(f"Written to {output}")


@template_cmd.command("preview")
@click.argument("template_string")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--passphrase", envvar="ENV_VAULT_PASS", prompt=True, hide_input=True)
def preview_cmd(template_string: str, vault_dir: str, passphrase: str) -> None:
    """Render an inline TEMPLATE_STRING and print the result."""
    vault = Vault(vault_dir)
    result = render_template(template_string, vault, passphrase)
    click.echo(result.rendered)
    click.echo(f"[{result.summary()}]", err=True)
