"""CLI commands for vault inheritance."""
import click

from env_vault.vault import Vault
from env_vault.env_inherit import resolve_inherited, apply_inheritance


@click.group("inherit")
def inherit_cmd() -> None:
    """Inherit keys from a parent vault."""


@inherit_cmd.command("show")
@click.argument("child_dir")
@click.argument("parent_dir")
@click.password_option("--passphrase", "-p", confirmation_prompt=False, prompt="Passphrase")
def show_cmd(child_dir: str, parent_dir: str, passphrase: str) -> None:
    """Show merged key resolution between CHILD_DIR and PARENT_DIR."""
    child = Vault(child_dir)
    parent = Vault(parent_dir)
    report = resolve_inherited(child, parent, passphrase)
    if not report.entries:
        click.echo("No keys found in either vault.")
        return
    for entry in report.entries:
        click.echo(str(entry))
    click.echo()
    click.echo(report.summary())


@inherit_cmd.command("apply")
@click.argument("child_dir")
@click.argument("parent_dir")
@click.password_option("--passphrase", "-p", confirmation_prompt=False, prompt="Passphrase")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing child keys.")
def apply_cmd(child_dir: str, parent_dir: str, passphrase: str, overwrite: bool) -> None:
    """Copy parent keys into CHILD_DIR vault (missing keys only unless --overwrite)."""
    child = Vault(child_dir)
    parent = Vault(parent_dir)
    written = apply_inheritance(child, parent, passphrase, overwrite=overwrite)
    if written:
        for key in written:
            click.echo(f"  inherited: {key}")
        click.echo(f"\n{len(written)} key(s) applied to child vault.")
    else:
        click.echo("Nothing to inherit — child vault already has all parent keys.")
