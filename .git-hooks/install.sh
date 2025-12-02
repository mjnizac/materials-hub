#!/bin/bash
# Script para instalar los git hooks personalizados

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GIT_HOOKS_DIR="$(git rev-parse --git-dir)/hooks"

echo "📦 Instalando git hooks personalizados..."

# Copiar prepare-commit-msg hook
if [ -f "$SCRIPT_DIR/prepare-commit-msg" ]; then
    cp "$SCRIPT_DIR/prepare-commit-msg" "$GIT_HOOKS_DIR/prepare-commit-msg"
    chmod +x "$GIT_HOOKS_DIR/prepare-commit-msg"
    echo "✅ Hook prepare-commit-msg instalado"
else
    echo "❌ Error: No se encontró el archivo prepare-commit-msg"
    exit 1
fi

echo ""
echo "🎉 Hooks instalados correctamente!"
echo ""
echo "📝 Emojis de commits disponibles:"
echo "  🐛 fix:  - Corrección de bugs"
echo "  ✨ feat: - Nueva funcionalidad"
echo "  📝 docs: - Documentación"
