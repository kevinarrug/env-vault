"""CLI commands for env-vault key quality ratings."""

import click

from .env_rating import (
    average_rating,
    get_rating,
    list_ratings,
    remove_rating,
    set_rating,
)


@click.group("rating")
def rating_cmd() -> None:
    """Manage quality ratings for vault keys."""


@rating_cmd.command("set")
@click.argument("key")
@click.argument("rating", type=int)
@click.option("--vault-dir", default=".", show_default=True)
def set_cmd(key: str, rating: int, vault_dir: str) -> None:
    """Set a quality rating (1-5) for KEY."""
    try:
        changed = set_rating(vault_dir, key, rating)
    except ValueError as exc:
        raise click.ClickException(str(exc))
    if changed:
        click.echo(f"Rating for '{key}' set to {rating}.")
    else:
        click.echo(f"Rating for '{key}' unchanged ({rating}).")


@rating_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def remove_cmd(key: str, vault_dir: str) -> None:
    """Remove the rating for KEY."""
    if remove_rating(vault_dir, key):
        click.echo(f"Rating for '{key}' removed.")
    else:
        click.echo(f"No rating found for '{key}'.")


@rating_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def get_cmd(key: str, vault_dir: str) -> None:
    """Get the rating for KEY."""
    value = get_rating(vault_dir, key)
    if value is None:
        raise click.ClickException(f"No rating set for '{key}'.")
    click.echo(str(value))


@rating_cmd.command("list")
@click.option("--vault-dir", default=".", show_default=True)
def list_cmd(vault_dir: str) -> None:
    """List all rated keys."""
    ratings = list_ratings(vault_dir)
    if not ratings:
        click.echo("No ratings recorded.")
        return
    for key, val in ratings.items():
        stars = "*" * val
        click.echo(f"{key}: {val}/5 {stars}")


@rating_cmd.command("average")
@click.option("--vault-dir", default=".", show_default=True)
def average_cmd(vault_dir: str) -> None:
    """Show the average rating across all rated keys."""
    avg = average_rating(vault_dir)
    if avg is None:
        click.echo("No ratings recorded.")
    else:
        click.echo(f"Average rating: {avg:.2f}/5")
