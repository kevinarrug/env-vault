"""CLI commands for env-vault changelog feature."""
import json
import click
from env_vault.env_changelog import add_entry, get_entries, remove_entries, list_keys


@click.group("changelog")
def changelog_cmd():
    """Manage per-key changelog entries."""


@changelog_cmd.command("add")
@click.argument("key")
@click.argument("message")
@click.option("--author", default=None, help="Author name or email.")
@click.option("--vault-dir", default=".", show_default=True)
def add_cmd(key: str, message: str, author, vault_dir: str):
    """Add a changelog entry for KEY."""
    entry = add_entry(vault_dir, key, message, author=author)
    ts = entry["timestamp"]
    click.echo(f"Added changelog entry for '{key}' at {ts}.")


@changelog_cmd.command("get")
@click.argument("key")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key: str, as_json: bool, vault_dir: str):
    """Show changelog entries for KEY."""
    entries = get_entries(vault_dir, key)
    if not entries:
        click.echo(f"No changelog entries for '{key}'.")
        return
    if as_json:
        click.echo(json.dumps(entries, indent=2))
    else:
        for e in entries:
            author_part = f" [{e['author']}]" if e["author"] else ""
            click.echo(f"{e['timestamp']}{author_part}: {e['message']}")


@changelog_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key: str, vault_dir: str):
    """Remove all changelog entries for KEY."""
    removed = remove_entries(vault_dir, key)
    if removed:
        click.echo(f"Removed changelog entries for '{key}'.")
    else:
        click.echo(f"No changelog entries found for '{key}'.")


@changelog_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
def list_cmd(vault_dir: str):
    """List all keys that have changelog entries."""
    keys = list_keys(vault_dir)
    if not keys:
        click.echo("No changelog entries recorded.")
    else:
        for k in keys:
            click.echo(k)
