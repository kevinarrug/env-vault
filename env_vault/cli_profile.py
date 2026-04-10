"""CLI commands for managing profiles."""

from __future__ import annotations

import click

from env_vault.profile import (
    assign_key,
    create_profile,
    delete_profile,
    get_profile_keys,
    key_profiles,
    list_profiles,
    unassign_key,
)


@click.group("profile")
def profile_cmd() -> None:
    """Manage named profiles (dev, staging, prod, …)."""


@profile_cmd.command("create")
@click.argument("profile")
@click.option("--vault-dir", default=".", show_default=True)
def create_cmd(profile: str, vault_dir: str) -> None:
    """Create a new empty profile."""
    create_profile(vault_dir, profile)
    click.echo(f"Profile '{profile}' created.")


@profile_cmd.command("delete")
@click.argument("profile")
@click.option("--vault-dir", default=".", show_default=True)
def delete_cmd(profile: str, vault_dir: str) -> None:
    """Delete a profile."""
    if delete_profile(vault_dir, profile):
        click.echo(f"Profile '{profile}' deleted.")
    else:
        click.echo(f"Profile '{profile}' not found.", err=True)
        raise SystemExit(1)


@profile_cmd.command("assign")
@click.argument("profile")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def assign_cmd(profile: str, key: str, vault_dir: str) -> None:
    """Assign a key to a profile."""
    assign_key(vault_dir, profile, key)
    click.echo(f"Key '{key}' assigned to profile '{profile}'.")


@profile_cmd.command("unassign")
@click.argument("profile")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def unassign_cmd(profile: str, key: str, vault_dir: str) -> None:
    """Remove a key from a profile."""
    if unassign_key(vault_dir, profile, key):
        click.echo(f"Key '{key}' removed from profile '{profile}'.")
    else:
        click.echo(f"Key '{key}' not in profile '{profile}'.", err=True)
        raise SystemExit(1)


@profile_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
def list_cmd(vault_dir: str) -> None:
    """List all profiles."""
    profiles = list_profiles(vault_dir)
    if not profiles:
        click.echo("No profiles defined.")
    for name in profiles:
        keys = get_profile_keys(vault_dir, name)
        click.echo(f"{name}: {', '.join(keys) if keys else '(empty)'}")


@profile_cmd.command("show")
@click.argument("profile")
@click.option("--vault-dir", default=".", show_default=True)
def show_cmd(profile: str, vault_dir: str) -> None:
    """Show keys in a profile."""
    keys = get_profile_keys(vault_dir, profile)
    if not keys:
        click.echo(f"Profile '{profile}' is empty or does not exist.")
    for key in keys:
        click.echo(key)


@profile_cmd.command("which")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def which_cmd(key: str, vault_dir: str) -> None:
    """Show which profiles contain a given key."""
    profiles = key_profiles(vault_dir, key)
    if not profiles:
        click.echo(f"Key '{key}' is not assigned to any profile.")
    for name in profiles:
        click.echo(name)
