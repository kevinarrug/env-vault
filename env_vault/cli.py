"""Main CLI entry point for env-vault."""
import click

from env_vault.cli_export import export_cmd, import_cmd
from env_vault.cli_history import history_cmd
from env_vault.cli_audit import audit_cmd
from env_vault.cli_diff import diff_cmd
from env_vault.cli_rotate import rotate_cmd
from env_vault.cli_tags import tags_cmd
from env_vault.cli_backup import backup_cmd
from env_vault.cli_profile import profile_cmd
from env_vault.cli_merge import merge_cmd
from env_vault.cli_alias import alias_cmd
from env_vault.cli_ttl import ttl_cmd
from env_vault.cli_notify import notify_cmd
from env_vault.cli_schema import schema_cmd
from env_vault.cli_import_map import import_map_cmd
from env_vault.cli_env_compare import compare_env_cmd
from env_vault.cli_cast import cast_cmd
from env_vault.cli_chain import chain_cmd
from env_vault.cli_scope import scope_cmd
from env_vault.cli_fmt import fmt_cmd
from env_vault.cli_resolve import resolve_cmd
from env_vault.cli_mask import mask_cmd
from env_vault.cli_transform import transform_cmd
from env_vault.cli_placeholder import placeholder_cmd
from env_vault.cli_depends import depends_cmd
from env_vault.cli_inherit import inherit_cmd
from env_vault.cli_freeze import freeze_cmd
from env_vault.cli_access import access_cmd
from env_vault.cli_deprecate import deprecate_cmd
from env_vault.cli_comment import comment_cmd
from env_vault.cli_ref import ref_cmd
from env_vault.cli_priority import priority_cmd
from env_vault.cli_note import note_cmd
from env_vault.cli_sensitivity import sensitivity_cmd
from env_vault.cli_owner import owner_cmd
from env_vault.cli_status import status_cmd
from env_vault.cli_visibility import visibility_cmd
from env_vault.cli_changelog import changelog_cmd
from env_vault.cli_type import type_cmd
from env_vault.cli_retention import retention_cmd
from env_vault.cli_checksum import checksum_cmd
from env_vault.cli_namespace import namespace_cmd
from env_vault.cli_trigger import trigger_cmd
from env_vault.cli_rating import rating_cmd
from env_vault.cli_severity import severity_cmd
from env_vault.cli_pin import pin_cmd
from env_vault.cli_flag import flag_cmd


@click.group()
def cli():
    """env-vault: encrypt and version environment variables."""


cli.add_command(export_cmd, "export")
cli.add_command(import_cmd, "import")
cli.add_command(history_cmd, "history")
cli.add_command(audit_cmd, "audit")
cli.add_command(diff_cmd, "diff")
cli.add_command(rotate_cmd, "rotate")
cli.add_command(tags_cmd, "tags")
cli.add_command(backup_cmd, "backup")
cli.add_command(profile_cmd, "profile")
cli.add_command(merge_cmd, "merge")
cli.add_command(alias_cmd, "alias")
cli.add_command(ttl_cmd, "ttl")
cli.add_command(notify_cmd, "notify")
cli.add_command(schema_cmd, "schema")
cli.add_command(import_map_cmd, "import-map")
cli.add_command(compare_env_cmd, "compare-env")
cli.add_command(cast_cmd, "cast")
cli.add_command(chain_cmd, "chain")
cli.add_command(scope_cmd, "scope")
cli.add_command(fmt_cmd, "fmt")
cli.add_command(resolve_cmd, "resolve")
cli.add_command(mask_cmd, "mask")
cli.add_command(transform_cmd, "transform")
cli.add_command(placeholder_cmd, "placeholder")
cli.add_command(depends_cmd, "depends")
cli.add_command(inherit_cmd, "inherit")
cli.add_command(freeze_cmd, "freeze")
cli.add_command(access_cmd, "access")
cli.add_command(deprecate_cmd, "deprecate")
cli.add_command(comment_cmd, "comment")
cli.add_command(ref_cmd, "ref")
cli.add_command(priority_cmd, "priority")
cli.add_command(note_cmd, "note")
cli.add_command(sensitivity_cmd, "sensitivity")
cli.add_command(owner_cmd, "owner")
cli.add_command(status_cmd, "status")
cli.add_command(visibility_cmd, "visibility")
cli.add_command(changelog_cmd, "changelog")
cli.add_command(type_cmd, "type")
cli.add_command(retention_cmd, "retention")
cli.add_command(checksum_cmd, "checksum")
cli.add_command(namespace_cmd, "namespace")
cli.add_command(trigger_cmd, "trigger")
cli.add_command(rating_cmd, "rating")
cli.add_command(severity_cmd, "severity")
cli.add_command(pin_cmd, "pin")
cli.add_command(flag_cmd, "flag")
