"""CLI commands for managing key notes."""
from __future__ import annotations

import click

from .env_note import set_note, get_note, remove_note, list_notes, clear_notes


@click.group(name="note")
def note_cmd():
    """Manage notes attached to vault keys."""


@note_cmd.command(name="set")
@click.argument("key")
@click.argument("note")
@click.option("--vault-dir", default=".", show_default=True)
def set_cmd(key: str, note: str, vault_dir: str):
    """Attach NOTE to KEY."""
    is_new = set_note(vault_dir, key, note)
    if is_new:
        click.echo(f"Note added for '{key}'.")
    else:
        click.echo(f"Note updated for '{key}'.")


@note_cmd.command(name="get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key: str, vault_dir: str):
    """Print the note for KEY."""
    note = get_note(vault_dir, key)
    if note is None:
        click.echo(f"No note set for '{key}'.", err=True)
        raise SystemExit(1)
    click.echo(note)


@note_cmd.command(name="remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key: str, vault_dir: str):
    """Remove the note for KEY."""
    if remove_note(vault_dir, key):
        click.echo(f"Note removed for '{key}'.")
    else:
        click.echo(f"No note found for '{key}'.", err=True)
        raise SystemExit(1)


@note_cmd.command(name="list")
@click.option("--vault-dir", default=".", show_default=True)
def list_cmd(vault_dir: str):
    """List all notes."""
    notes = list_notes(vault_dir)
    if not notes:
        click.echo("No notes recorded.")
        return
    for key, note in notes.items():
        click.echo(f"{key}: {note}")


@note_cmd.command(name="clear")
@click.option("--vault-dir", default=".", show_default=True)
@click.confirmation_option(prompt="Remove all notes?")
def clear_cmd(vault_dir: str):
    """Remove all notes."""
    count = clear_notes(vault_dir)
    click.echo(f"Cleared {count} note(s).")
