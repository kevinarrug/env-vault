"""Main CLI entry point for env-vault."""

from __future__ import annotations

import click

from env_vault.cli_export import export_cmd, import_cmd
from env_vault.cli_history import history_cmd
from env_vault.cli_rotate import rotate_cmd
from env_vault.cli_audit import audit_cmd
from env_vault.cli_diff import diff_cmd
from env_vault.cli_tags import tags_cmd
from env_vault.cli_backup import backup_cmd
from env_vault.cli_lint import lint_cmd
from env_vault.cli_template import template_cmd
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
from env_vault.cli_flag import flag_cmd
from env_vault.cli_badge import badge_cmd
from env_vault.cli_origin import origin_cmd


@click.group()
@click.version_option()
def cli():
    """env-vault: encrypt and version environment variables."""


cli.add_command(export_cmd, name="export")
cli.add_command(import_cmd, name="import")
cli.add_command(history_cmd, name="history")
cli.add_command(rotate_cmd, name="rotate")
cli.add_command(audit_cmd, name="audit")
cli.add_command(diff_cmd, name="diff")
cli.add_command(tags_cmd, name="tags")
cli.add_command(backup_cmd, name="backup")
cli.add_command(lint_cmd, name="lint")
cli.add_command(template_cmd, name="template")
cli.add_command(profile_cmd, name="profile")
cli.add_command(merge_cmd, name="merge")
cli.add_command(alias_cmd, name="alias")
cli.add_command(ttl_cmd, name="ttl")
cli.add_command(pin_cmd, name="pin")
cli.add_command(notify_cmd, name="notify")
cli.add_command(schema_cmd, name="schema")
cli.add_command(import_map_cmd, name="import-map")
cli.add_command(compare_env_cmd, name="compare-env")
cli.add_command(cast_cmd, name="cast")
cli.add_command(chain_cmd, name="chain")
cli.add_command(scope_cmd, name="scope")
cli.add_command(fmt_cmd, name="fmt")
cli.add_command(resolve_cmd, name="resolve")
cli.add_command(mask_cmd, name="mask")
cli.add_command(transform_cmd, name="transform")
cli.add_command(placeholder_cmd, name="placeholder")
cli.add_command(depends_cmd, name="depends")
cli.add_command(inherit_cmd, name="inherit")
cli.add_command(freeze_cmd, name="freeze")
cli.add_command(access_cmd, name="access")
cli.add_command(deprecate_cmd, name="deprecate")
cli.add_command(comment_cmd, name="comment")
cli.add_command(ref_cmd, name="ref")
cli.add_command(priority_cmd, name="priority")
cli.add_command(note_cmd, name="note")
cli.add_command(sensitivity_cmd, name="sensitivity")
cli.add_command(owner_cmd, name="owner")
cli.add_command(status_cmd, name="status")
cli.add_command(visibility_cmd, name="visibility")
cli.add_command(changelog_cmd, name="changelog")
cli.add_command(type_cmd, name="type")
cli.add_command(retention_cmd, name="retention")
cli.add_command(checksum_cmd, name="checksum")
cli.add_command(namespace_cmd, name="namespace")
cli.add_command(trigger_cmd, name="trigger")
cli.add_command(rating_cmd, name="rating")
cli.add_command(severity_cmd, name="severity")
cli.add_command(flag_cmd, name="flag")
cli.add_command(badge_cmd, name="badge")
cli.add_command(origin_cmd, name="origin")
