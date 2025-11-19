import subprocess
from datetime import datetime

import click
from flask.cli import with_appcontext
from sqlalchemy import inspect, text

from app import create_app, db


@click.command("db:status", help="Displays database connection status and migration information.")
@with_appcontext
def db_status():
    """
    Shows comprehensive database status including:
    - Database connection status
    - Current migration revision
    - Pending migrations
    - Number of tables
    - Database size (if available)
    """
    app = create_app()
    with app.app_context():
        click.echo(click.style("\n=== Database Status ===\n", fg="cyan", bold=True))

        # 1. Check database connection
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            db_name = db.engine.url.database
            click.echo(
                click.style("  Connection: ", fg="white")
                + click.style(f"✓ Connected to '{db_name}'", fg="green", bold=True)
            )
        except Exception as e:
            click.echo(click.style("  Connection: ", fg="white") + click.style(f"✗ Failed - {e}", fg="red", bold=True))
            return

        # 2. Get current migration revision
        try:
            inspector = inspect(db.engine)
            if "alembic_version" in inspector.get_table_names():
                with db.engine.connect() as conn:
                    result = conn.execute(text("SELECT version_num FROM alembic_version"))
                    current_revision = result.scalar()
                    if current_revision:
                        click.echo(
                            click.style("  Migration: ", fg="white")
                            + click.style(f"{current_revision[:12]}", fg="yellow")
                            + click.style(" (current)", fg="white")
                        )
                    else:
                        click.echo(
                            click.style("  Migration: ", fg="white") + click.style("No migrations applied", fg="yellow")
                        )
            else:
                click.echo(
                    click.style("  Migration: ", fg="white")
                    + click.style("Database not initialized (run 'db:setup')", fg="red")
                )
        except Exception as e:
            click.echo(
                click.style("  Migration: ", fg="white") + click.style(f"Unable to read - {e}", fg="yellow")
            )

        # 3. Check for pending migrations
        try:
            result = subprocess.run(
                ["flask", "db", "current"], capture_output=True, text=True, timeout=10
            )

            # Check if there are pending migrations
            heads_result = subprocess.run(
                ["flask", "db", "heads"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0 and heads_result.returncode == 0:
                current_output = result.stdout.strip()
                heads_output = heads_result.stdout.strip()

                if "(head)" in current_output:
                    click.echo(
                        click.style("  Pending:   ", fg="white")
                        + click.style("✓ No pending migrations", fg="green")
                    )
                else:
                    click.echo(
                        click.style("  Pending:   ", fg="white")
                        + click.style("⚠ Migrations need to be applied (run 'flask db upgrade')", fg="yellow")
                    )
        except Exception as e:
            click.echo(
                click.style("  Pending:   ", fg="white")
                + click.style(f"Unable to check - {e}", fg="yellow")
            )

        # 4. Count tables
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            # Exclude alembic_version from count
            table_count = len([t for t in tables if t != "alembic_version"])
            click.echo(
                click.style("  Tables:    ", fg="white") + click.style(f"{table_count}", fg="cyan")
            )
        except Exception as e:
            click.echo(
                click.style("  Tables:    ", fg="white") + click.style(f"Unable to count - {e}", fg="yellow")
            )

        # 5. Get database size (MariaDB/MySQL specific)
        try:
            with db.engine.connect() as conn:
                query = text(
                    """
                    SELECT
                        ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as size_mb
                    FROM information_schema.TABLES
                    WHERE table_schema = :db_name
                    """
                )
                result = conn.execute(query, {"db_name": db_name})
                size_mb = result.scalar()
                if size_mb:
                    click.echo(
                        click.style("  Size:      ", fg="white") + click.style(f"{size_mb} MB", fg="cyan")
                    )
        except Exception:
            # Size information not critical, skip if fails
            pass

        # 6. Database engine info
        try:
            dialect = db.engine.dialect.name
            driver = db.engine.driver if hasattr(db.engine, "driver") else "unknown"
            click.echo(
                click.style("  Engine:    ", fg="white")
                + click.style(f"{dialect}", fg="cyan")
                + click.style(f" ({driver})", fg="white")
            )
        except Exception:
            pass

        # 7. Show last check timestamp
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        click.echo(click.style(f"\n  Last checked: {now}\n", fg="white", dim=True))
