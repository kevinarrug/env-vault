"""CLI commands for diffing vault states."""
import json
import click
from env_vault.vault import Vault
from env_vault.diff import diff_vaults, diff_dicts


@click.group()
def diff_cmd():
    """Compare vault contents or snapshots."""
    pass


@diff_cmd.command("vaults")
@click.argument("vault_a", type=click.Path(exists=True))
@click.argument("vault_b", type=click.Path(exists=True))
@click.option("--passphrase-a", prompt=True, hide_input=True, help="Passphrase for vault A")
@click.option("--passphrase-b", default=None, hide_input=True, help="Passphrase for vault B (defaults to A)")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output as JSON")
def compare_vaults_cmd(vault_a, vault_b, passphrase_a, passphrase_b, as_json):
    """Diff two vault files."""
    if passphrase_b is None:
        passphrase_b = passphrase_a

    try:
        va = Vault(vault_a, passphrase_a)
        vb = Vault(vault_b, passphrase_b)
        result = diff_vaults(va, passphrase_a, vb, passphrase_b)
    except Exception as e:
        raise click.ClickException(str(e))

    if as_json:
        click.echo(json.dumps({
            "added": list(result.added),
            "removed": list(result.removed),
            "changed": list(result.changed),
            "unchanged": list(result.unchanged),
        }, indent=2))
    else:
        if not result.has_changes():
            click.echo("No differences found.")
            return
        click.echo(result.summary())
        for key in sorted(result.added):
            click.echo(click.style(f"  + {key}", fg="green"))
        for key in sorted(result.removed):
            click.echo(click.style(f"  - {key}", fg="red"))
        for key in sorted(result.changed):
            click.echo(click.style(f"  ~ {key}", fg="yellow"))


@diff_cmd.command("dicts")
@click.argument("file_a", type=click.Path(exists=True))
@click.argument("file_b", type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True, default=False, help="Output as JSON")
def compare_dicts_cmd(file_a, file_b, as_json):
    """Diff two plain JSON env files."""
    try:
        with open(file_a) as f:
            dict_a = json.load(f)
        with open(file_b) as f:
            dict_b = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        raise click.ClickException(f"Failed to read files: {e}")

    result = diff_dicts(dict_a, dict_b)

    if as_json:
        click.echo(json.dumps({
            "added": list(result.added),
            "removed": list(result.removed),
            "changed": list(result.changed),
            "unchanged": list(result.unchanged),
        }, indent=2))
    else:
        if not result.has_changes():
            click.echo("No differences found.")
            return
        click.echo(result.summary())
        for key in sorted(result.added):
            click.echo(click.style(f"  + {key}", fg="green"))
        for key in sorted(result.removed):
            click.echo(click.style(f"  - {key}", fg="red"))
        for key in sorted(result.changed):
            click.echo(click.style(f"  ~ {key}", fg="yellow"))
