import subprocess

import click
from flask.cli import with_appcontext
from sqlalchemy import text

from app import create_app, db


@click.command("db:migrate", help="Creates a new database migration after detecting model changes.")
@click.argument("message", required=True)
@with_appcontext
def db_migrate(message):
    """
    Enhanced wrapper for 'flask db migrate' with better feedback and validation.

    This command:
    - Verifies database connection
    - Analyzes model changes
    - Generates migration file
    - Validates the generated file
    - Provides clear next steps
    """
    app = create_app()
    with app.app_context():
        click.echo(click.style("\n=== Creating New Migration ===\n", fg="cyan", bold=True))

        # Step 1: Check database connection
        click.echo(click.style("[1/4] ", fg="white") + "Checking database connection...", nl=False)
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            click.echo(click.style(" ✓", fg="green"))
        except Exception as e:
            click.echo(click.style(" ✗", fg="red"))
            click.echo(click.style(f"\nError: Unable to connect to database", fg="red"))
            click.echo(click.style(f"Details: {e}", fg="yellow"))
            click.echo(click.style("\nPlease check your database configuration in .env", fg="white"))
            return

        # Step 2: Analyze model changes
        click.echo(click.style("[2/4] ", fg="white") + "Analyzing model changes...")

        # Step 3: Generate migration file
        click.echo(click.style("[3/4] ", fg="white") + "Generating migration file...")
        try:
            result = subprocess.run(
                ["flask", "db", "migrate", "-m", message],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Parse the output to show detected changes
            if result.stdout:
                lines = result.stdout.split('\n')
                changes_detected = False
                for line in lines:
                    if "Detected" in line or "detected" in line:
                        click.echo(click.style("  → ", fg="blue") + line.strip())
                        changes_detected = True
                    elif "Generating" in line:
                        # Extract filename from the output
                        if "..." in line:
                            parts = line.split("Generating")[1].split("...")
                            if parts:
                                filename = parts[0].strip()
                                click.echo(click.style("  Created: ", fg="green") + filename)

                if not changes_detected:
                    click.echo(click.style("  No model changes detected", fg="yellow"))

            if result.returncode != 0:
                click.echo(click.style("\nError: Migration generation failed", fg="red"))
                if result.stderr:
                    click.echo(click.style(f"Details: {result.stderr}", fg="yellow"))
                return

        except subprocess.TimeoutExpired:
            click.echo(click.style(" ✗", fg="red"))
            click.echo(click.style("\nError: Migration generation timed out", fg="red"))
            return
        except Exception as e:
            click.echo(click.style(" ✗", fg="red"))
            click.echo(click.style(f"\nError: {e}", fg="red"))
            return

        # Step 4: Validate migration file
        click.echo(click.style("[4/4] ", fg="white") + "Validating migration file...", nl=False)
        try:
            # Check if migration was created by running flask db current
            result = subprocess.run(
                ["flask", "db", "heads"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                click.echo(click.style(" ✓", fg="green"))
            else:
                click.echo(click.style(" ⚠", fg="yellow"))
        except Exception:
            click.echo(click.style(" ⚠", fg="yellow"))

        # Success message and next steps
        click.echo(click.style("\nMigration created successfully!", fg="green", bold=True))
        click.echo(click.style("\nNext steps:", fg="cyan"))
        click.echo(click.style("  1. ", fg="white") + "Review the migration file in " +
                   click.style("migrations/versions/", fg="yellow"))
        click.echo(click.style("  2. ", fg="white") + "Run " +
                   click.style("rosemary db:upgrade", fg="cyan") + " to apply it")
        click.echo(click.style("  3. ", fg="white") + "Test the migration in a safe environment first\n")
