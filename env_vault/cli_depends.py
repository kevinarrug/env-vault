"""CLI commands for env-vault dependency tracking."""
import click
from env_vault.env_depends import (
    add_dependency,
    remove_dependency,
    get_dependencies,
    get_dependents,
    resolve_order,
)


@click.group("depends")
def depends_cmd() -> None:
    """Manage key dependency relationships."""


@depends_cmd.command("add")
@click.argument("key")
@click.argument("depends_on")
@click.option("--vault-dir", default=".", show_default=True)
def add_cmd(key: str, depends_on: str, vault_dir: str) -> None:
    """Declare that KEY depends on DEPENDS_ON."""
    added = add_dependency(vault_dir, key, depends_on)
    if added:
        click.echo(f"Added dependency: {key} -> {depends_on}")
    else:
        click.echo(f"Dependency already exists: {key} -> {depends_on}")


@depends_cmd.command("remove")
@click.argument("key")
@click.argument("depends_on")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key: str, depends_on: str, vault_dir: str) -> None:
    """Remove a dependency edge between KEY and DEPENDS_ON."""
    removed = remove_dependency(vault_dir, key, depends_on)
    if removed:
        click.echo(f"Removed dependency: {key} -> {depends_on}")
    else:
        click.echo(f"Dependency not found: {key} -> {depends_on}", err=True)
        raise SystemExit(1)


@depends_cmd.command("list")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--reverse", is_flag=True, help="Show dependents instead of dependencies.")
def list_cmd(key: str, vault_dir: str, reverse: bool) -> None:
    """List dependencies (or dependents) of KEY."""
    if reverse:
        items = get_dependents(vault_dir, key)
        label = "dependents"
    else:
        items = get_dependencies(vault_dir, key)
        label = "dependencies"
    if not items:
        click.echo(f"No {label} for '{key}'.")
    else:
        for item in items:
            click.echo(item)


@depends_cmd.command("order")
@click.argument("keys", nargs=-1)
@click.option("--vault-dir", default=".", show_default=True)
def order_cmd(keys: tuple, vault_dir: str) -> None:
    """Print topological load order for KEYS (all keys if omitted)."""
    try:
        ordered = resolve_order(vault_dir, list(keys) if keys else None)
        for k in ordered:
            click.echo(k)
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
