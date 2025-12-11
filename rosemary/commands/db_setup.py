import subprocess

import click
from flask.cli import with_appcontext

from rosemary.commands.db_seed import db_seed


@click.command(
    "db:setup",
    help="Complete database setup: resets database, runs migrations and seeds with test data.",
)
@click.option("-y", "--yes", is_flag=True, help="Confirm the operation without prompting.")
@with_appcontext
def db_setup(yes):
    """
    Complete database setup from scratch.

    This command will:
    1. Delete all existing data and clear uploads
    2. Run migrations to create tables
    3. Seed the database with test data

    WARNING: This will delete ALL existing data!
    """
    # Always show warning unless -y is provided
    if not yes:
        warning_msg = "⚠️  WARNING: This will DELETE ALL DATA, clear uploads, run migrations and seed. Continue?"
        if not click.confirm(warning_msg, default=False):
            click.echo(click.style("Database setup cancelled.", fg="yellow"))
            return

    click.echo(click.style("Starting complete database setup...", fg="cyan"))

    # Step 0: Reset database (always)
    from rosemary.commands.db_reset import db_reset

    click.echo(click.style("\n[1/3] Resetting database...", fg="red"))
    ctx = click.get_current_context()
    ctx.invoke(db_reset, clear_migrations=False, yes=True)

    # Step 1: Run migrations
    click.echo(click.style("\n[2/3] Running database migrations...", fg="blue"))
    try:
        # First, stamp to head to resolve any multiple heads issues
        click.echo(click.style("Checking migration status...", fg="cyan"))
        subprocess.run(["flask", "db", "stamp", "head"], check=True)

        # Then upgrade to latest
        subprocess.run(["flask", "db", "upgrade"], check=True)
        click.echo(click.style("Migrations completed successfully.", fg="green"))
    except subprocess.CalledProcessError as e:
        click.echo(click.style(f"Error during migrations: {e}", fg="red"))
        click.echo(click.style("Please check your database configuration and try again.", fg="yellow"))
        return

    # Step 2: Seed the database
    click.echo(click.style("\n[3/3] Seeding database with test data...", fg="blue"))
    ctx = click.get_current_context()
    # Don't reset in seed since we already reset the whole database
    ctx.invoke(db_seed, reset=False, yes=True, module=None)

    click.echo(click.style("\nDatabase setup completed successfully!", fg="green", bold=True))
    click.echo(
        click.style(
            "You can now run the application with 'flask run' or 'rosemary run'.",
            fg="cyan",
        )
    )
