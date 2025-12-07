import os
import subprocess

import click
from dotenv import load_dotenv


@click.command("db:console", help="Opens a PostgreSQL console with credentials from .env.")
def db_console():
    load_dotenv()

    postgres_hostname = os.getenv("POSTGRES_HOSTNAME")
    postgres_user = os.getenv("POSTGRES_USER")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    postgres_database = os.getenv("POSTGRES_DATABASE")
    postgres_port = os.getenv("POSTGRES_PORT", "5432")

    # Build the command to connect to PostgreSQL
    postgres_connect_cmd = f"PGPASSWORD={postgres_password} psql -h {postgres_hostname} -p {postgres_port} -U {postgres_user} -d {postgres_database}"

    # Execute the command
    try:
        subprocess.run(postgres_connect_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(click.style(f"Error opening PostgreSQL console: {e}", fg="red"))
