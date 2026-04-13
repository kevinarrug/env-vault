"""Main CLI entry point for env-vault."""
import click

from env_vault.cli_audit import audit_cmd
from env_vault.cli_alias import alias_cmd
from env_vault.cli_backup import backup_cmd
from env_vault.cli_cast import cast_cmd
from env_vault.cli_chain import chain_cmd
from env_vault.cli_changelog import changelog_cmd
from env_vault.cli_comment import comment_cmd
from env_vault.cli_depends import depends_cmd
from env_vault.cli_deprecate import deprecate_cmd
from env_vault.cli_diff import diff_cmd
from env_vault.cli_env_compare import compare_env_cmd
from env_vault.cli_export import export_cmd, import_cmd
from env_vault.cli_fmt import fmt_cmd
from env_vault.cli_freeze import freeze_cmd
from env_vault.cli_history import history_cmd
from env_vault.cli_import_map import import_map_cmd
from env_vault.cli_inherit import inherit_cmd
from env_vault.cli_lint import lint_cmd
from env_vault.cli_mask import mask_cmd
from env_vault.cli_merge import merge_cmd
from env_vault.cli_notify import notify_cmd
from env_vault.cli_note import note_cmd
from env_vault.cli_owner import owner_cmd
from env_vault.cli_pin import pin_cmd
from env_vault.cli_placeholder import placeholder_cmd
from env_vault.cli_priority import priority_cmd
from env_vault.cli_profile import profile_cmd
from env_vault.cli_ref import ref_cmd
from env_vault.cli_resolve import resolve_cmd
from env_vault.cli_rotate import rotate_cmd
from env_vault.cli_schema import schema_cmd
from env_vault.cli_scope import scope_cmd
from env_vault.cli_sensitivity import sensitivity_cmd
from env_vault.cli_status import status_cmd
from env_vault.cli_tags import tags_cmd
from env_vault.cli_template import template_cmd
from env_vault.cli_transform import transform_cmd
from env_vault.cli_ttl import ttl_cmd
from env_vault.cli_type import type_cmd
from env_vault.cli_visibility import visibility_cmd
from env_vault.cli_access import access_cmd


@click.group()
@click.version_option()
def cli():
    """env-vault: Encrypt and version your environment variables."""


cli.add_command(access_cmd)
cli.add_command(alias_cmd)
cli.add_command(audit_cmd)
cli.add_command(backup_cmd)
cli.add_command(cast_cmd)
cli.add_command(chain_cmd)
cli.add_command(changelog_cmd)
cli.add_command(comment_cmd)
cli.add_command(compare_env_cmd)
cli.add_command(depends_cmd)
cli.add_command(deprecate_cmd)
cli.add_command(diff_cmd)
cli.add_command(export_cmd)
cli.add_command(fmt_cmd)
cli.add_command(freeze_cmd)
cli.add_command(history_cmd)
cli.add_command(import_cmd)
cli.add_command(import_map_cmd)
cli.add_command(inherit_cmd)
cli.add_command(lint_cmd)
cli.add_command(mask_cmd)
cli.add_command(merge_cmd)
cli.add_command(note_cmd)
cli.add_command(notify_cmd)
cli.add_command(owner_cmd)
cli.add_command(pin_cmd)
cli.add_command(placeholder_cmd)
cli.add_command(priority_cmd)
cli.add_command(profile_cmd)
cli.add_command(ref_cmd)
cli.add_command(resolve_cmd)
cli.add_command(rotate_cmd)
cli.add_command(schema_cmd)
cli.add_command(scope_cmd)
cli.add_command(sensitivity_cmd)
cli.add_command(status_cmd)
cli.add_command(tags_cmd)
cli.add_command(template_cmd)
cli.add_command(transform_cmd)
cli.add_command(ttl_cmd)
cli.add_command(type_cmd)
cli.add_command(visibility_cmd)
