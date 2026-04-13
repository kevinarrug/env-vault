"""CLI commands for managing key type annotations."""
import click

from env_vault.env_type import (
    VALID_TYPES,
    get_type,
    list_types,
    remove_type,
    set_type,
    validate_value,
)


@click.group(name="type")
def type_cmd():
    """Manage declared types for vault keys."""


@type_cmd.command(name="set")
@click.argument("key")
@click.argument("type_name")
@click.option("--vault-dir", default=".", show_default=True)
def set_cmd(key: str, type_name: str, vault_dir: str):
    """Set the declared type for KEY."""
    try:
        is_new = set_type(vault_dir, key, type_name)
        action = "Set" if is_new else "Updated"
        click.echo(f"{action} type of '{key}' to '{type_name}'.")
    except ValueError as exc:
        raise click.ClickException(str(exc))


@type_cmd.command(name="remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key: str, vault_dir: str):
    """Remove the type annotation for KEY."""
    if remove_type(vault_dir, key):
        click.echo(f"Removed type annotation for '{key}'.")
    else:
        click.echo(f"No type annotation found for '{key}'.")


@type_cmd.command(name="get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key: str, vault_dir: str):
    """Get the declared type for KEY."""
    t = get_type(vault_dir, key)
    if t is None:
        raise click.ClickException(f"No type annotation for '{key}'.")
    click.echo(t)


@type_cmd.command(name="list")
@click.option("--vault-dir", default=".", show_default=True)
def list_cmd(vault_dir: str):
    """List all key type annotations."""
    types = list_types(vault_dir)
    if not types:
        click.echo("No type annotations defined.")
        return
    for key, type_name in sorted(types.items()):
        click.echo(f"{key}: {type_name}")


@type_cmd.command(name="check")
@click.argument("key")
@click.argument("value")
@click.option("--vault-dir", default=".", show_default=True)
def check_cmd(key: str, value: str, vault_dir: str):
    """Check VALUE against the declared type for KEY."""
    t = get_type(vault_dir, key)
    if t is None:
        raise click.ClickException(f"No type annotation for '{key}'.")
    if validate_value(value, t):
        click.echo(f"OK: '{value}' is a valid {t}.")
    else:
        raise click.ClickException(f"'{value}' is not a valid {t}.")


@type_cmd.command(name="types")
def types_cmd():
    """List all supported type names."""
    for t in sorted(VALID_TYPES):
        click.echo(t)
