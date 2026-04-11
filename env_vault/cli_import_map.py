"""CLI commands for managing import key mappings."""
from __future__ import annotations

import click

from .env_import_map import (
    apply_map,
    get_mappings,
    remove_mapping,
    set_mapping,
)


@click.group("import-map")
def import_map_cmd() -> None:
    """Manage key remapping rules applied during import."""


@import_map_cmd.command("set")
@click.argument("source_key")
@click.argument("target_key")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def set_cmd(source_key: str, target_key: str, vault_dir: str) -> None:
    """Map SOURCE_KEY to TARGET_KEY on import."""
    is_new = set_mapping(vault_dir, source_key, target_key)
    verb = "Added" if is_new else "Updated"
    click.echo(f"{verb} mapping: {source_key} -> {target_key}")


@import_map_cmd.command("remove")
@click.argument("source_key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(source_key: str, vault_dir: str) -> None:
    """Remove the mapping for SOURCE_KEY."""
    if remove_mapping(vault_dir, source_key):
        click.echo(f"Removed mapping for '{source_key}'.")
    else:
        click.echo(f"No mapping found for '{source_key}'.")


@import_map_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
def list_cmd(vault_dir: str) -> None:
    """List all current import mappings."""
    mappings = get_mappings(vault_dir)
    if not mappings:
        click.echo("No mappings defined.")
        return
    for src, tgt in sorted(mappings.items()):
        click.echo(f"  {src} -> {tgt}")


@import_map_cmd.command("apply")
@click.argument("json_file", type=click.Path(exists=True))
@click.option("--vault-dir", default=".", show_default=True)
@click.option("--strict", is_flag=True, default=False, help="Skip unmapped keys.")
def apply_cmd(json_file: str, vault_dir: str, strict: bool) -> None:
    """Preview applying mappings to a JSON file of key=value pairs."""
    import json

    with open(json_file) as fh:
        data: dict = json.load(fh)

    remapped, report = apply_map(vault_dir, data, strict=strict)
    click.echo(report.summary())
    for warning in report.warnings:
        click.echo(f"  WARNING: {warning}", err=True)
    click.echo(json.dumps(remapped, indent=2, sort_keys=True))
