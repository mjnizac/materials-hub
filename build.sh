#!/usr/bin/env bash
# Salir si hay error
set -o errexit

# Instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# Esperar a que la base de datos esté lista
until pg_isready -h "$POSTGRES_HOSTNAME" -p "$POSTGRES_PORT"; do
  echo "Esperando a que la base de datos esté lista..."
  sleep 2
done

# Setup de la base de datos y seeders
rosemary db:setup