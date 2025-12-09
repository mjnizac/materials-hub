import subprocess

import click
from flask.cli import with_appcontext

from rosemary.commands.db_seed import db_seed


@click.command(
    "db:setup",
    help="Initial database setup: runs migrations and seeds the database with test data.",
)
@click.option("-y", "--yes", is_flag=True, help="Confirm the operation without prompting.")
@with_appcontext
def db_setup(yes):
    """
    Complete database setup for first-time installation.
    Runs migrations and populates the database with seed data.
    """
    if not yes and not click.confirm(
        "This will run migrations and seed the database. Continue?",
        default=True,
    ):
        click.echo(click.style("Database setup cancelled.", fg="yellow"))
        return

    click.echo(click.style("Starting database setup...", fg="cyan"))

    # Step 1: Run migrations
    click.echo(click.style("\n[1/2] Running database migrations...", fg="blue"))
    try:
        subprocess.run(["flask", "db", "upgrade"], check=True)
        click.echo(click.style("Migrations completed successfully.", fg="green"))
    except subprocess.CalledProcessError as e:
        click.echo(click.style(f"Error during migrations: {e}", fg="red"))
        click.echo(click.style("Please check your database configuration and try again.", fg="yellow"))
        return

    # Step 2: Seed the database
    click.echo(click.style("\n[2/2] Seeding database with test data...", fg="blue"))
    ctx = click.get_current_context()
    ctx.invoke(db_seed, reset=True, yes=True, module=None)

    click.echo(click.style("\nDatabase setup completed successfully!", fg="green", bold=True))
    click.echo(
        click.style(
            "You can now run the application with 'flask run' or 'rosemary run'.",
            fg="cyan",
        )
    )
