#!/bin/bash

# ---------------------------------------------------------------------------
# Creative Commons CC BY 4.0 - David Romero - Diverso Lab
# ---------------------------------------------------------------------------
# This script is licensed under the Creative Commons Attribution 4.0 
# International License. You are free to share and adapt the material 
# as long as appropriate credit is given, a link to the license is provided, 
# and you indicate if changes were made.
#
# For more details, visit:
# https://creativecommons.org/licenses/by/4.0/
# ---------------------------------------------------------------------------

echo "Starting wait-for-db.sh"
echo "Hostname: $POSTGRES_HOSTNAME, Port: $POSTGRES_PORT, User: $POSTGRES_USER"

while ! PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOSTNAME" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d postgres -c 'SELECT 1' > /dev/null 2>&1; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing command"
exec "$@"
