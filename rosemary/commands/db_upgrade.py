import os
import subprocess
import time
from datetime import datetime

import click
from flask.cli import with_appcontext
from sqlalchemy import text

from app import create_app, db


@click.command("db:upgrade", help="Applies pending database migrations with automatic backup.")
@click.option(
    "--no-backup",
    is_flag=True,
    help="Skip automatic backup before upgrading (not recommended).",
)
@with_appcontext
def db_upgrade(no_backup):
    """
    Enhanced wrapper for 'flask db upgrade' with:
    - Connection verification
    - Pending migrations check
    - Automatic backup (unless --no-backup)
    - Progress tracking
    - Post-upgrade verification
    - Better error handling
    """
    app = create_app()
    with app.app_context():
        click.echo(click.style("\n=== Upgrading Database ===\n", fg="cyan", bold=True))

        # Step 1: Check database connection
        click.echo(click.style("[1/5] ", fg="white") + "Checking database connection...", nl=False)
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_name = db.engine.url.database
            click.echo(click.style(" ✓", fg="green"))
        except Exception as e:
            click.echo(click.style(" ✗", fg="red"))
            click.echo(click.style("\nError: Unable to connect to database", fg="red"))
            click.echo(click.style(f"Details: {e}", fg="yellow"))
            return

        # Step 2: Check for pending migrations
        click.echo(click.style("[2/5] ", fg="white") + "Checking for pending migrations...")
        try:
            current_result = subprocess.run(["flask", "db", "current"], capture_output=True, text=True, timeout=10)

            # Check if already at head
            if "(head)" in current_result.stdout:
                click.echo(click.style("\n  ✓ Database is already up to date!", fg="green"))
                click.echo(click.style("  No pending migrations to apply.\n", fg="white"))
                return

            click.echo(click.style("  Found pending migrations", fg="yellow"))

        except Exception as e:
            click.echo(click.style(f"  Warning: Unable to check pending migrations - {e}", fg="yellow"))
            if not click.confirm("  Continue anyway?", default=False):
                return

        # Step 3: Create backup (unless --no-backup)
        backup_file = None
        if not no_backup:
            click.echo(click.style("[3/5] ", fg="white") + "Creating backup...", nl=False)
            try:
                # Create backups directory if it doesn't exist
                working_dir = os.getenv("WORKING_DIR", "")
                backups_dir = os.path.join(working_dir, "backups")
                os.makedirs(backups_dir, exist_ok=True)

                # Generate backup filename with timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                backup_file = os.path.join(backups_dir, f"pre-upgrade_{timestamp}.sql")

                # Get database credentials from environment
                db_host = os.getenv("POSTGRES_HOSTNAME", "localhost")
                db_port = os.getenv("POSTGRES_PORT", "5432")
                db_user = os.getenv("POSTGRES_USER", "postgres")
                db_password = os.getenv("POSTGRES_PASSWORD", "")

                # Try to find pg_dump compatible with server version
                # Common paths for different PostgreSQL versions
                pg_dump_paths = [
                    "pg_dump",  # System default
                    "/usr/lib/postgresql/17/bin/pg_dump",  # PostgreSQL 17
                    "/usr/lib/postgresql/16/bin/pg_dump",  # PostgreSQL 16
                ]

                pg_dump_cmd = "pg_dump"
                for path in pg_dump_paths:
                    if os.path.exists(path) or path == "pg_dump":
                        pg_dump_cmd = path
                        break

                # Create pg_dump command
                dump_cmd = [
                    pg_dump_cmd,
                    f"--host={db_host}",
                    f"--port={db_port}",
                    f"--username={db_user}",
                    "--no-password",
                    "--format=plain",
                    "--clean",
                    "--if-exists",
                    db_name,
                ]

                # Set PGPASSWORD environment variable for pg_dump
                env = os.environ.copy()
                env["PGPASSWORD"] = db_password

                with open(backup_file, "w") as f:
                    result = subprocess.run(dump_cmd, stdout=f, stderr=subprocess.PIPE, timeout=120, env=env)

                if result.returncode == 0:
                    # Get file size
                    size_mb = os.path.getsize(backup_file) / (1024 * 1024)
                    click.echo(click.style(" ✓", fg="green"))
                    click.echo(
                        click.style("  Backup saved: ", fg="white")
                        + click.style(f"{backup_file}", fg="cyan")
                        + click.style(f" ({size_mb:.2f} MB)", fg="white")
                    )
                else:
                    error_msg = result.stderr.decode()
                    click.echo(click.style(" ⚠", fg="yellow"))
                    click.echo(click.style(f"  Warning: Backup failed - {error_msg}", fg="yellow"))

                    # Check if it's a version mismatch and provide helpful message
                    if "server version mismatch" in error_msg:
                        click.echo(click.style("\n  Tip: Install matching PostgreSQL client tools:", fg="cyan"))
                        click.echo(click.style("    sudo apt install postgresql-client-17", fg="cyan"))

                    if not click.confirm("  Continue without backup?", default=False):
                        return
                    backup_file = None

            except FileNotFoundError:
                click.echo(click.style(" ⚠", fg="yellow"))
                click.echo(click.style("  Warning: pg_dump not found. Skipping backup.", fg="yellow"))
                if not click.confirm("  Continue without backup?", default=False):
                    return
                backup_file = None
            except Exception as e:
                click.echo(click.style(" ⚠", fg="yellow"))
                click.echo(click.style(f"  Warning: Backup failed - {e}", fg="yellow"))
                if not click.confirm("  Continue without backup?", default=False):
                    return
                backup_file = None
        else:
            click.echo(click.style("[3/5] ", fg="white") + "Skipping backup (--no-backup flag)")

        # Step 4: Apply migrations
        click.echo(click.style("[4/5] ", fg="white") + "Applying migrations...")
        try:
            start_time = time.time()

            result = subprocess.run(
                ["flask", "db", "upgrade"], capture_output=True, text=True, timeout=300  # 5 minutes timeout
            )

            elapsed_time = time.time() - start_time

            if result.returncode == 0:
                # Parse output to show which migrations were applied
                if result.stdout:
                    lines = result.stdout.split("\n")
                    for line in lines:
                        if "Running upgrade" in line:
                            # Extract migration info
                            parts = line.split("Running upgrade")[1].strip() if "Running upgrade" in line else ""
                            if parts:
                                click.echo(click.style("  → ", fg="green") + parts)

                click.echo(click.style(f"  Completed in {elapsed_time:.2f}s", fg="white"))
            else:
                click.echo(click.style("\n  ✗ Migration failed!", fg="red", bold=True))
                if result.stderr:
                    click.echo(click.style(f"\n  Error details:\n{result.stderr}", fg="red"))

                # Offer to restore backup
                if backup_file and os.path.exists(backup_file):
                    click.echo(click.style("\n  A backup was created before the upgrade.", fg="yellow"))
                    if click.confirm("  Would you like to restore the backup?", default=True):
                        click.echo(click.style("\n  Restoring backup...", fg="yellow"), nl=False)
                        try:
                            env_restore = os.environ.copy()
                            env_restore["PGPASSWORD"] = db_password
                            restore_cmd = [
                                "psql",
                                f"--host={db_host}",
                                f"--port={db_port}",
                                f"--username={db_user}",
                                "--no-password",
                                db_name,
                            ]
                            with open(backup_file, "r") as f:
                                restore_result = subprocess.run(
                                    restore_cmd, stdin=f, capture_output=True, timeout=120, env=env_restore
                                )
                            if restore_result.returncode == 0:
                                click.echo(click.style(" ✓", fg="green"))
                                click.echo(click.style("  Backup restored successfully", fg="green"))
                            else:
                                click.echo(click.style(" ✗", fg="red"))
                                click.echo(click.style(f"  Restore failed: {restore_result.stderr.decode()}", fg="red"))
                        except Exception as e:
                            click.echo(click.style(" ✗", fg="red"))
                            click.echo(click.style(f"  Restore failed: {e}", fg="red"))
                return

        except subprocess.TimeoutExpired:
            click.echo(click.style("\n  ✗ Migration timed out!", fg="red", bold=True))
            click.echo(click.style("  The migration took longer than expected (>5 minutes)", fg="yellow"))
            return
        except Exception as e:
            click.echo(click.style(f"\n  ✗ Migration failed: {e}", fg="red", bold=True))
            return

        # Step 5: Verify migration state
        click.echo(click.style("[5/5] ", fg="white") + "Verifying migration state...", nl=False)
        try:
            result = subprocess.run(["flask", "db", "current"], capture_output=True, text=True, timeout=10)

            if result.returncode == 0 and "(head)" in result.stdout:
                click.echo(click.style(" ✓", fg="green"))
                # Extract current revision
                for line in result.stdout.split("\n"):
                    if line.strip() and "->" not in line:
                        revision = line.split()[0] if line.split() else "unknown"
                        click.echo(
                            click.style("  Current revision: ", fg="white")
                            + click.style(f"{revision[:12]}", fg="cyan")
                            + click.style(" (head)", fg="green")
                        )
                        break
            else:
                click.echo(click.style(" ⚠", fg="yellow"))

        except Exception:
            click.echo(click.style(" ⚠", fg="yellow"))

        # Success message
        click.echo(click.style("\nDatabase upgraded successfully!", fg="green", bold=True))
        click.echo(
            click.style("\nRun ", fg="white")
            + click.style("rosemary db:status", fg="cyan")
            + click.style(" to verify the current state.\n", fg="white")
        )
