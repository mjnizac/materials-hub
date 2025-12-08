#!/usr/bin/env bash
# Salir si hay error
set -o errexit

echo "✅ build.sh iniciado"

# Instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

echo "✅ build.sh finalizado - dependencias instaladas"