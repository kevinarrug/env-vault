"""CLI commands for managing key comments."""

from __future__ import annotations

import click

from env_vault.env_comment import (
    get_comment,
    keys_with_comments,
    list_comments,
    remove_comment,
    set_comment,
)


@click.group("comment")
def comment_cmd() -> None:
    """Manage human-readable comments for vault keys."""


@comment_cmd.command("set")
@click.argument("key")
@click.argument("comment")
@click.option("--vault-dir", default=".", show_default=True)
def set_cmd(key: str, comment: str, vault_dir: str) -> None:
    """Attach COMMENT to KEY."""
    is_new = set_comment(vault_dir, key, comment)
    verb = "Added" if is_new else "Updated"
    click.echo(f"{verb} comment for '{key}'.")


@comment_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key: str, vault_dir: str) -> None:
    """Remove the comment for KEY."""
    if remove_comment(vault_dir, key):
        click.echo(f"Removed comment for '{key}'.")
    else:
        click.echo(f"No comment found for '{key}'.")
        raise SystemExit(1)


@comment_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key: str, vault_dir: str) -> None:
    """Print the comment for KEY."""
    comment = get_comment(vault_dir, key)
    if comment is None:
        click.echo(f"No comment set for '{key}'.")
        raise SystemExit(1)
    click.echo(comment)


@comment_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--keys-only", is_flag=True, default=False)
def list_cmd(vault_dir: str, keys_only: bool) -> None:
    """List all keys that have comments."""
    if keys_only:
        for k in keys_with_comments(vault_dir):
            click.echo(k)
        return
    data = list_comments(vault_dir)
    if not data:
        click.echo("No comments recorded.")
        return
    for k, v in sorted(data.items()):
        click.echo(f"{k}: {v}")
