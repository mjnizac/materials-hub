import os
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
    1. Clean the database (drop all tables and ENUMs)
    2. Initialize migrations if needed
    3. Run migrations to create tables
    4. Seed the database with test data

    Works for both fresh installs and existing databases.
    WARNING: This will delete ALL existing data!
    """
    # Always show warning unless -y is provided
    if not yes:
        warning_msg = "⚠️  WARNING: This will DELETE ALL DATA, clear uploads, run migrations and seed. Continue?"
        if not click.confirm(warning_msg, default=False):
            click.echo(click.style("Database setup cancelled.", fg="yellow"))
            return

    click.echo(click.style("Starting complete database setup...", fg="cyan"))

    # Step 0: Clean database completely (tables + ENUMs)
    click.echo(click.style("\n[1/4] Cleaning database...", fg="red"))
    try:
        from sqlalchemy import text

        from app import create_app, db

        app = create_app()
        with app.app_context():
            # Drop all tables
            result = db.session.execute(
                text(
                    """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public';
            """
                )
            )
            tables = [row[0] for row in result]

            if tables:
                click.echo(click.style(f"  Dropping {len(tables)} tables...", fg="yellow"))
                for table in tables:
                    db.session.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE;'))
                db.session.commit()

            # Drop all ENUM types
            result = db.session.execute(
                text(
                    """
                SELECT t.typname
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                WHERE t.typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
                GROUP BY t.typname;
            """
                )
            )
            enum_types = [row[0] for row in result]

            if enum_types:
                click.echo(click.style(f"  Dropping {len(enum_types)} ENUM types...", fg="yellow"))
                for enum_type in enum_types:
                    db.session.execute(text(f'DROP TYPE IF EXISTS "{enum_type}" CASCADE;'))
                db.session.commit()

            click.echo(click.style("  Database cleaned successfully.", fg="green"))
    except Exception as e:
        click.echo(click.style(f"Error cleaning database: {e}", fg="red"))
        return

    # Clear uploads
    from rosemary.commands.clear_uploads import clear_uploads

    ctx = click.get_current_context()
    ctx.invoke(clear_uploads)

    # Step 1: Check and initialize migrations if needed
    click.echo(click.style("\n[2/4] Checking migrations...", fg="blue"))
    migrations_dir = "migrations"
    versions_dir = os.path.join(migrations_dir, "versions")

    # Check if migrations folder exists
    if not os.path.exists(migrations_dir):
        click.echo(click.style("  Migrations folder not found. Initializing...", fg="yellow"))
        try:
            subprocess.run(["flask", "db", "init"], check=True)
            click.echo(click.style("  Migrations initialized.", fg="green"))
        except subprocess.CalledProcessError as e:
            click.echo(click.style(f"Error initializing migrations: {e}", fg="red"))
            return

    # Check if there are migration files
    has_migrations = False
    if os.path.exists(versions_dir):
        migration_files = [f for f in os.listdir(versions_dir) if f.endswith(".py") and f != "__init__.py"]
        has_migrations = len(migration_files) > 0

    if not has_migrations:
        click.echo(click.style("  No migrations found. Generating initial migration...", fg="yellow"))
        try:
            subprocess.run(["flask", "db", "migrate", "-m", "Initial migration"], check=True)
            click.echo(click.style("  Initial migration created.", fg="green"))
        except subprocess.CalledProcessError as e:
            click.echo(click.style(f"Error creating migration: {e}", fg="red"))
            return
    else:
        click.echo(click.style("  Migrations found.", fg="green"))

    # Step 2: Run migrations
    click.echo(click.style("\n[3/4] Running database migrations...", fg="blue"))
    try:
        subprocess.run(["flask", "db", "upgrade"], check=True)
        click.echo(click.style("  Migrations completed successfully.", fg="green"))
    except subprocess.CalledProcessError as e:
        click.echo(click.style(f"Error during migrations: {e}", fg="red"))
        click.echo(click.style("Please check your database configuration and try again.", fg="yellow"))
        return

    # Step 3: Seed the database
    click.echo(click.style("\n[4/4] Seeding database with test data...", fg="blue"))
    ctx = click.get_current_context()
    # Don't reset in seed since we already reset the whole database
    ctx.invoke(db_seed, reset=False, yes=True, module=None)

    click.echo(click.style("\n✅ Database setup completed successfully!", fg="green", bold=True))
    click.echo(
        click.style(
            "You can now run the application with 'flask run' or 'rosemary run'.",
            fg="cyan",
        )
    )
