"""CLI commands for managing key namespaces."""
import click

from env_vault.env_namespace import (
    set_namespace,
    get_namespace,
    remove_namespace,
    list_namespaces,
    keys_in_namespace,
    list_all_namespaces,
)


@click.group("namespace")
def namespace_cmd() -> None:
    """Manage key namespaces."""


@namespace_cmd.command("set")
@click.argument("key")
@click.argument("namespace")
@click.option("--vault-dir", default=".", show_default=True)
def set_cmd(key: str, namespace: str, vault_dir: str) -> None:
    """Assign KEY to NAMESPACE."""
    is_new = set_namespace(vault_dir, key, namespace)
    if is_new:
        click.echo(f"Assigned '{key}' to namespace '{namespace}'.")
    else:
        click.echo(f"Updated '{key}' namespace to '{namespace}'.")


@namespace_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key: str, vault_dir: str) -> None:
    """Remove namespace assignment for KEY."""
    if remove_namespace(vault_dir, key):
        click.echo(f"Removed namespace for '{key}'.")
    else:
        click.echo(f"No namespace set for '{key}'.")


@namespace_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key: str, vault_dir: str) -> None:
    """Get the namespace for KEY."""
    ns = get_namespace(vault_dir, key)
    if ns is None:
        click.echo(f"No namespace set for '{key}'.")
        raise SystemExit(1)
    click.echo(ns)


@namespace_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--namespace", default=None, help="Filter by namespace name.")
def list_cmd(vault_dir: str, namespace: str) -> None:
    """List key namespace assignments."""
    if namespace:
        keys = keys_in_namespace(vault_dir, namespace)
        if not keys:
            click.echo(f"No keys in namespace '{namespace}'.")
        else:
            for k in keys:
                click.echo(k)
    else:
        data = list_namespaces(vault_dir)
        if not data:
            click.echo("No namespaces defined.")
        else:
            for k, ns in sorted(data.items()):
                click.echo(f"{k}={ns}")


@namespace_cmd.command("namespaces")
@click.option("--vault-dir", default=".", show_default=True)
def namespaces_cmd(vault_dir: str) -> None:
    """List all unique namespace names."""
    names = list_all_namespaces(vault_dir)
    if not names:
        click.echo("No namespaces defined.")
    else:
        for name in names:
            click.echo(name)
