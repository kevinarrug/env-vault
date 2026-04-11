"""cli.py — root CLI entry-point for env-vault."""
import click

from env_vault.cli_export import export_cmd, import_cmd
from env_vault.cli_history import history_cmd
from env_vault.cli_rotate import rotate_cmd
from env_vault.cli_audit import audit_cmd
from env_vault.cli_diff import diff_cmd
from env_vault.cli_tags import tags_cmd
from env_vault.cli_backup import backup_cmd
from env_vault.cli_profile import profile_cmd
from env_vault.cli_merge import merge_cmd
from env_vault.cli_alias import alias_cmd
from env_vault.cli_ttl import ttl_cmd
from env_vault.cli_pin import pin_cmd
from env_vault.cli_notify import notify_cmd
from env_vault.cli_schema import schema_cmd
from env_vault.cli_import_map import import_map_cmd
from env_vault.cli_env_compare import compare_env_cmd
from env_vault.cli_cast import cast_cmd
from env_vault.cli_chain import chain_cmd


@click.group()
@click.version_option()
def cli() -> None:
    """env-vault: encrypt and version environment variables."""


cli.add_command(export_cmd, "export")
cli.add_command(import_cmd, "import")
cli.add_command(history_cmd, "history")
cli.add_command(rotate_cmd, "rotate")
cli.add_command(audit_cmd, "audit")
cli.add_command(diff_cmd, "diff")
cli.add_command(tags_cmd, "tags")
cli.add_command(backup_cmd, "backup")
cli.add_command(profile_cmd, "profile")
cli.add_command(merge_cmd, "merge")
cli.add_command(alias_cmd, "alias")
cli.add_command(ttl_cmd, "ttl")
cli.add_command(pin_cmd, "pin")
cli.add_command(notify_cmd, "notify")
cli.add_command(schema_cmd, "schema")
cli.add_command(import_map_cmd, "import-map")
cli.add_command(compare_env_cmd, "compare-env")
cli.add_command(cast_cmd, "cast")
cli.add_command(chain_cmd, "chain")
