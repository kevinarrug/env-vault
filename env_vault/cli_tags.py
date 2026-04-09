"""CLI commands for tag management."""

from __future__ import annotations

import click

from env_vault.tags import (
    add_tag,
    all_tags,
    get_tags,
    keys_by_tag,
    remove_tag,
)


@click.group("tags")
def tags_cmd() -> None:
    """Manage tags on vault keys."""


@tags_cmd.command("add")
@click.argument("key")
@click.argument("tag")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def add_cmd(key: str, tag: str, vault_dir: str) -> None:
    """Add TAG to KEY."""
    add_tag(vault_dir, key, tag)
    click.echo(f"Tagged '{key}' with '{tag}'.")


@tags_cmd.command("remove")
@click.argument("key")
@click.argument("tag")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def remove_cmd(key: str, tag: str, vault_dir: str) -> None:
    """Remove TAG from KEY."""
    existed = remove_tag(vault_dir, key, tag)
    if existed:
        click.echo(f"Removed tag '{tag}' from '{key}'.")
    else:
        click.echo(f"Tag '{tag}' not found on '{key}'.")


@tags_cmd.command("list")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def list_cmd(key: str, vault_dir: str) -> None:
    """List all tags for KEY."""
    tags = get_tags(vault_dir, key)
    if tags:
        click.echo(", ".join(tags))
    else:
        click.echo(f"No tags found for '{key}'.")


@tags_cmd.command("filter")
@click.argument("tag")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def filter_cmd(tag: str, vault_dir: str) -> None:
    """List all keys that carry TAG."""
    keys = keys_by_tag(vault_dir, tag)
    if keys:
        for k in keys:
            click.echo(k)
    else:
        click.echo(f"No keys found with tag '{tag}'.")


@tags_cmd.command("show-all")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def show_all_cmd(vault_dir: str) -> None:
    """Show all key→tag mappings."""
    mapping = all_tags(vault_dir)
    if not mapping:
        click.echo("No tags recorded.")
        return
    for key, tags in sorted(mapping.items()):
        click.echo(f"{key}: {', '.join(tags)}")
