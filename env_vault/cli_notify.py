"""CLI commands for notification webhooks."""
import json
import click
from env_vault.notify import (
    register_webhook,
    unregister_webhook,
    get_webhooks,
    get_event_log,
)


@click.group("notify")
def notify_cmd():
    """Manage notification webhooks for vault events."""


@notify_cmd.command("add")
@click.argument("event")
@click.argument("url")
@click.option("--vault-dir", default=".", show_default=True)
def add_cmd(event: str, url: str, vault_dir: str):
    """Register a webhook URL for EVENT (e.g. set, delete, rotate)."""
    added = register_webhook(vault_dir, event, url)
    if added:
        click.echo(f"Registered webhook for '{event}': {url}")
    else:
        click.echo(f"Webhook already registered for '{event}': {url}")


@notify_cmd.command("remove")
@click.argument("event")
@click.argument("url")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(event: str, url: str, vault_dir: str):
    """Unregister a webhook URL for EVENT."""
    removed = unregister_webhook(vault_dir, event, url)
    if removed:
        click.echo(f"Removed webhook for '{event}': {url}")
    else:
        click.echo(f"No webhook found for '{event}': {url}", err=True)


@notify_cmd.command("list")
@click.option("--event", default=None, help="Filter by event type")
@click.option("--vault-dir", default=".", show_default=True)
def list_cmd(event: str, vault_dir: str):
    """List registered webhooks."""
    hooks = get_webhooks(vault_dir, event)
    if not any(hooks.values()):
        click.echo("No webhooks registered.")
        return
    for ev, urls in hooks.items():
        for url in urls:
            click.echo(f"{ev}: {url}")


@notify_cmd.command("log")
@click.option("--event", default=None, help="Filter by event type")
@click.option("--as-json", is_flag=True)
@click.option("--vault-dir", default=".", show_default=True)
def log_cmd(event: str, as_json: bool, vault_dir: str):
    """Show the notification event log."""
    entries = get_event_log(vault_dir, event)
    if not entries:
        click.echo("No events recorded.")
        return
    if as_json:
        click.echo(json.dumps(entries, indent=2))
    else:
        for e in entries:
            click.echo(f"[{e['event']}] key={e['key']} ts={e['ts']:.0f} meta={e['meta']}")
