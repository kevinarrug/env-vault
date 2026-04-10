"""Root CLI entry-point that wires all command groups together."""

from __future__ import annotations

import click

from .cli_export import export_cmd, import_cmd
from .cli_history import history_cmd
from .cli_audit import audit_cmd
from .cli_diff import diff_cmd
from .cli_backup import backup_cmd
from .cli_rotate import rotate_cmd
from .cli_tags import tags_cmd
from .cli_profile import profile_cmd
from .cli_merge import merge_cmd
from .cli_lint import lint_cmd
from .cli_template import template_cmd
from .cli_alias import alias_cmd


@click.group()
@click.version_option(package_name="env-vault")
def cli() -> None:
    """env-vault — encrypt and version your environment variables."""


cli.add_command(export_cmd, "export")
cli.add_command(import_cmd, "import")
cli.add_command(history_cmd, "history")
cli.add_command(audit_cmd, "audit")
cli.add_command(diff_cmd, "diff")
cli.add_command(backup_cmd, "backup")
cli.add_command(rotate_cmd, "rotate")
cli.add_command(tags_cmd, "tags")
cli.add_command(profile_cmd, "profile")
cli.add_command(merge_cmd, "merge")
cli.add_command(lint_cmd, "lint")
cli.add_command(template_cmd, "template")
cli.add_command(alias_cmd, "alias")


if __name__ == "__main__":  # pragma: no cover
    cli()
