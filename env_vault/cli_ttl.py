"""CLI commands for managing key TTLs."""

from __future__ import annotations

import click

from .ttl import get_ttl, is_expired, list_ttls, purge_expired, remove_ttl, set_ttl


@click.group("ttl")
def ttl_cmd():
    """Manage time-to-live (TTL) expiry for vault keys."""


@ttl_cmd.command("set")
@click.argument("vault_dir")
@click.argument("key")
@click.argument("seconds", type=int)
def set_cmd(vault_dir: str, key: str, seconds: int):
    """Set a TTL of SECONDS for KEY in VAULT_DIR."""
    try:
        expires_at = set_ttl(vault_dir, key, seconds)
        click.echo(f"TTL set for '{key}': expires in {seconds}s (at {expires_at:.2f})")
    except ValueError as exc:
        raise click.ClickException(str(exc))


@ttl_cmd.command("remove")
@click.argument("vault_dir")
@click.argument("key")
def remove_cmd(vault_dir: str, key: str):
    """Remove the TTL for KEY in VAULT_DIR."""
    removed = remove_ttl(vault_dir, key)
    if removed:
        click.echo(f"TTL removed for '{key}'.")
    else:
        click.echo(f"No TTL found for '{key}'.")


@ttl_cmd.command("get")
@click.argument("vault_dir")
@click.argument("key")
def get_cmd(vault_dir: str, key: str):
    """Show remaining TTL seconds for KEY."""
    remaining = get_ttl(vault_dir, key)
    if remaining is None:
        click.echo(f"No TTL set for '{key}'.")
    elif is_expired(vault_dir, key):
        click.echo(f"'{key}' has expired (0s remaining).")
    else:
        click.echo(f"'{key}' expires in {remaining:.1f}s.")


@ttl_cmd.command("list")
@click.argument("vault_dir")
def list_cmd(vault_dir: str):
    """List all keys with active TTLs."""
    ttls = list_ttls(vault_dir)
    if not ttls:
        click.echo("No TTLs configured.")
        return
    for key, remaining in sorted(ttls.items()):
        status = "EXPIRED" if remaining == 0.0 else f"{remaining:.1f}s"
        click.echo(f"  {key}: {status}")


@ttl_cmd.command("purge")
@click.argument("vault_dir")
def purge_cmd(vault_dir: str):
    """Remove all expired TTL entries."""
    expired = purge_expired(vault_dir)
    if expired:
        click.echo(f"Purged {len(expired)} expired key(s): {', '.join(expired)}")
    else:
        click.echo("No expired TTLs to purge.")
