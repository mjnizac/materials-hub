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


echo "(testing) Hostname: $POSTGRES_HOSTNAME, Port: $POSTGRES_PORT, User: $POSTGRES_USER, Test DB: $POSTGRES_TEST_DATABASE"

echo "PostgreSQL is up - creating test database if it doesn't exist"

# Create the test database if it does not exist
PGPASSWORD="$POSTGRES_ROOT_PASSWORD" psql -h "$POSTGRES_HOSTNAME" -p "$POSTGRES_PORT" -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_TEST_DATABASE'" | grep -q 1 || PGPASSWORD="$POSTGRES_ROOT_PASSWORD" psql -h "$POSTGRES_HOSTNAME" -p "$POSTGRES_PORT" -U postgres -c "CREATE DATABASE \"$POSTGRES_TEST_DATABASE\" ENCODING 'UTF8';"

echo "Test database created"
