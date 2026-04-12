"""CLI commands for env-vault access control."""
import click

from env_vault.env_access import (
    can,
    clear_key,
    get_permissions,
    grant,
    list_accessible_keys,
    revoke,
)


@click.group("access")
def access_cmd() -> None:
    """Manage role-based access control for vault keys."""


@access_cmd.command("grant")
@click.argument("key")
@click.argument("role")
@click.argument("permission", type=click.Choice(["read", "write"]))
@click.option("--vault-dir", default=".", show_default=True)
def grant_cmd(key: str, role: str, permission: str, vault_dir: str) -> None:
    """Grant ROLE the PERMISSION on KEY."""
    added = grant(vault_dir, key, role, permission)
    if added:
        click.echo(f"Granted {permission} on '{key}' to role '{role}'.")
    else:
        click.echo(f"Role '{role}' already has {permission} on '{key}'.")


@access_cmd.command("revoke")
@click.argument("key")
@click.argument("role")
@click.argument("permission", type=click.Choice(["read", "write"]))
@click.option("--vault-dir", default=".", show_default=True)
def revoke_cmd(key: str, role: str, permission: str, vault_dir: str) -> None:
    """Revoke ROLE's PERMISSION on KEY."""
    removed = revoke(vault_dir, key, role, permission)
    if removed:
        click.echo(f"Revoked {permission} on '{key}' from role '{role}'.")
    else:
        click.echo(f"Role '{role}' did not have {permission} on '{key}'.")


@access_cmd.command("check")
@click.argument("key")
@click.argument("role")
@click.argument("permission", type=click.Choice(["read", "write"]))
@click.option("--vault-dir", default=".", show_default=True)
def check_cmd(key: str, role: str, permission: str, vault_dir: str) -> None:
    """Check whether ROLE has PERMISSION on KEY."""
    allowed = can(vault_dir, key, role, permission)
    symbol = "✓" if allowed else "✗"
    click.echo(f"{symbol} Role '{role}' {'can' if allowed else 'cannot'} {permission} '{key}'.")


@access_cmd.command("list")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def list_cmd(key: str, vault_dir: str) -> None:
    """List all roles and permissions for KEY."""
    perms = get_permissions(vault_dir, key)
    if not perms:
        click.echo(f"No ACL entries for '{key}'.")
        return
    for role, ps in sorted(perms.items()):
        click.echo(f"  {role}: {', '.join(sorted(ps))}")


@access_cmd.command("keys")
@click.argument("role")
@click.argument("permission", type=click.Choice(["read", "write"]))
@click.option("--vault-dir", default=".", show_default=True)
def keys_cmd(role: str, permission: str, vault_dir: str) -> None:
    """List all keys accessible to ROLE with PERMISSION."""
    keys = list_accessible_keys(vault_dir, role, permission)
    if not keys:
        click.echo(f"No keys accessible to role '{role}' with {permission}.")
        return
    for k in keys:
        click.echo(f"  {k}")


@access_cmd.command("clear")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def clear_cmd(key: str, vault_dir: str) -> None:
    """Remove all ACL entries for KEY."""
    removed = clear_key(vault_dir, key)
    if removed:
        click.echo(f"Cleared all ACL entries for '{key}'.")
    else:
        click.echo(f"No ACL entries found for '{key}'.")
