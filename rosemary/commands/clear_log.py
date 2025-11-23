import glob
import os
from datetime import datetime, timedelta

import click


@click.command("clear:log", help="Clears log files from the 'logs/' directory.")
@click.option("--days", default=None, type=int, help="Delete logs older than N days (keeps current log)")
@click.option("--all", is_flag=True, help="Delete all log files including the current one")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompt")
def clear_log(days, all, yes):
    """
    Clears log files with different strategies:
    - Default: Deletes all rotated logs (app.log.1, app.log.2, etc.) but keeps app.log
    - --days N: Deletes only logs older than N days
    - --all: Deletes all logs including the current app.log
    """
    logs_dir = os.path.join(os.getcwd(), "logs")

    # Check if logs directory exists
    if not os.path.exists(logs_dir):
        click.echo(click.style("The 'logs/' directory does not exist.", fg="yellow"))
        return

    # Get all log files
    all_logs = glob.glob(os.path.join(logs_dir, "app.log*"))

    # Filter based on options
    if all:
        logs_to_delete = all_logs
        operation_desc = "todos los archivos de log"
    elif days:
        cutoff_time = datetime.now() - timedelta(days=days)
        logs_to_delete = [
            log for log in all_logs if os.path.getmtime(log) < cutoff_time.timestamp() and not log.endswith("app.log")
        ]
        operation_desc = f"logs más antiguos de {days} días"
    else:
        # Default: delete rotated logs but keep current app.log
        logs_to_delete = [log for log in all_logs if not log.endswith("app.log")]
        operation_desc = "archivos de log rotados (mantiene app.log actual)"

    if not logs_to_delete:
        click.echo(click.style("No hay archivos de log para eliminar.", fg="yellow"))
        return

    # Show files to be deleted
    click.echo(click.style(f"\n📋 Archivos a eliminar ({operation_desc}):\n", fg="cyan", bold=True))
    total_size = 0
    for log_file in sorted(logs_to_delete):
        size = os.path.getsize(log_file)
        total_size += size
        size_kb = size / 1024
        filename = os.path.basename(log_file)
        mod_time = datetime.fromtimestamp(os.path.getmtime(log_file)).strftime("%Y-%m-%d %H:%M")
        click.echo(f"  • {filename:20s} ({size_kb:6.2f} KB) - {mod_time}")

    click.echo(click.style(f"\n📊 Total: {len(logs_to_delete)} archivos, {total_size/1024:.2f} KB\n", fg="white"))

    # Confirm deletion
    if not yes:
        if not click.confirm(click.style("¿Deseas continuar?", fg="yellow")):
            click.echo(click.style("Operación cancelada.", fg="yellow"))
            return

    # Delete files
    deleted_count = 0
    errors = []

    for log_file in logs_to_delete:
        try:
            os.remove(log_file)
            deleted_count += 1
        except Exception as e:
            errors.append((os.path.basename(log_file), str(e)))

    # Show results
    if deleted_count > 0:
        click.echo(
            click.style(f"✓ {deleted_count} archivo(s) de log eliminado(s) correctamente.", fg="green", bold=True)
        )

    if errors:
        click.echo(click.style(f"\n⚠ Errores al eliminar {len(errors)} archivo(s):", fg="red"))
        for filename, error in errors:
            click.echo(click.style(f"  • {filename}: {error}", fg="red"))
