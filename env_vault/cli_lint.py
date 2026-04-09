"""CLI commands for linting vault contents."""

from __future__ import annotations

import click

from env_vault.vault import Vault
from env_vault.lint import lint_vault


@click.group(name="lint")
def lint_cmd() -> None:
    """Lint and validate environment variable keys and values."""


@lint_cmd.command(name="check")
@click.argument("vault_path")
@click.option("--passphrase", "-p", required=True, envvar="ENV_VAULT_PASSPHRASE",
              help="Passphrase to decrypt the vault.")
@click.option("--strict", is_flag=True, default=False,
              help="Exit with non-zero status on warnings as well as errors.")
@click.option("--json", "as_json", is_flag=True, default=False,
              help="Output issues as JSON.")
def check_cmd(vault_path: str, passphrase: str, strict: bool, as_json: bool) -> None:
    """Check a vault for key/value issues."""
    import json as _json

    try:
        vault = Vault(vault_path)
        vault.load(passphrase)
    except Exception as exc:
        raise click.ClickException(f"Failed to open vault: {exc}")

    result = lint_vault(vault, passphrase)

    if as_json:
        data = [
            {"key": i.key, "level": i.level, "message": i.message}
            for i in result.issues
        ]
        click.echo(_json.dumps(data, indent=2))
    else:
        if result.issues:
            click.echo(result.summary())
        else:
            click.echo("✔ No issues found.")

    if not result.passed or (strict and result.warnings):
        raise SystemExit(1)
