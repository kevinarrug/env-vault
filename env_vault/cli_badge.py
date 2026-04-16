import click
from env_vault.env_badge import (
    set_badge,
    remove_badge,
    get_badge,
    list_badges,
    filter_by_badge,
    VALID_BADGES,
)


@click.group("badge")
def badge_cmd():
    """Manage key badges."""


@badge_cmd.command("set")
@click.argument("key")
@click.argument("badge")
@click.option("--vault-dir", default=".", show_default=True)
def set_cmd(key, badge, vault_dir):
    """Assign a badge to KEY."""
    try:
        changed = set_badge(vault_dir, key, badge)
    except ValueError as e:
        raise click.ClickException(str(e))
    if changed:
        click.echo(f"Badge '{badge}' set on '{key}'.")
    else:
        click.echo(f"Badge '{badge}' unchanged for '{key}'.")


@badge_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key, vault_dir):
    """Remove badge from KEY."""
    if remove_badge(vault_dir, key):
        click.echo(f"Badge removed from '{key}'.")
    else:
        click.echo(f"No badge found for '{key}'.")


@badge_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key, vault_dir):
    """Get badge for KEY."""
    badge = get_badge(vault_dir, key)
    if badge is None:
        raise click.ClickException(f"No badge set for '{key}'.")
    click.echo(badge)


@badge_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
def list_cmd(vault_dir):
    """List all key badges."""
    badges = list_badges(vault_dir)
    if not badges:
        click.echo("No badges set.")
        return
    for key, badge in sorted(badges.items()):
        click.echo(f"{key}: {badge}")


@badge_cmd.command("filter")
@click.argument("badge")
@click.option("--vault-dir", default=".", show_default=True)
def filter_cmd(badge, vault_dir):
    """List keys with a specific BADGE."""
    if badge not in VALID_BADGES:
        raise click.ClickException(f"Invalid badge '{badge}'. Valid: {sorted(VALID_BADGES)}")
    keys = filter_by_badge(vault_dir, badge)
    if not keys:
        click.echo(f"No keys with badge '{badge}'.")
        return
    for key in sorted(keys):
        click.echo(key)
