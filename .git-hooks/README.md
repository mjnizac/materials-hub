# Git Hooks - Emojis en Commits

Este directorio contiene git hooks personalizados para mejorar los mensajes de commit.

## 🚀 Instalación

Para instalar los hooks en tu repositorio local:

```bash
./.git-hooks/install.sh
```

## 📝 Emojis Automáticos

El hook `prepare-commit-msg` añade automáticamente emojis a tus commits según el tipo:

| Tipo | Emoji | Descripción |
|------|-------|-------------|
| `fix:` | 🐛 | Corrección de bugs |
| `feat:` | ✨ | Nueva funcionalidad |
| `docs:` | 📝 | Documentación |

## 💡 Uso

Simplemente haz commits normales con Conventional Commits:

```bash
git commit -m "fix: corregir error en validación"
```

El hook automáticamente lo convertirá en:

```bash
🐛 fix: corregir error en validación
```

## 🔄 Actualizar Hooks

Si se actualiza algún hook, vuelve a ejecutar:

```bash
./.git-hooks/install.sh
```

## ⚠️ Nota para el Equipo

Cada desarrollador debe ejecutar el script de instalación en su repositorio local. Los hooks de Git **no se propagan automáticamente** al hacer clone/pull del repositorio.
