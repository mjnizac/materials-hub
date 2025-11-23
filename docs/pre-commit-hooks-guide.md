# Pre-commit Hooks Guide

Esta guía explica el sistema de pre-commit hooks implementado en Materials Hub para mantener la calidad del código automáticamente.

## ¿Qué son los Pre-commit Hooks?

Los pre-commit hooks son **scripts que se ejecutan automáticamente antes de cada commit** para:
- ✅ Formatear código automáticamente
- ✅ Validar sintaxis y estilo
- ✅ Prevenir commits con errores
- ✅ Asegurar mensajes de commit consistentes

**Resultado:** Código de mayor calidad sin esfuerzo manual.

---

## Instalación

### Nuevos Desarrolladores

Si clonaste el repositorio por primera vez:

```bash
# 1. Activar entorno virtual
source venv/bin/activate

# 2. Instalar pre-commit (ya está en requirements.txt)
pip install -r requirements.txt

# 3. Instalar los hooks en git
pre-commit install
pre-commit install --hook-type commit-msg
```

**Listo!** Ahora los hooks se ejecutarán automáticamente en cada commit.

---

## ¿Qué Hace Automáticamente?

### Antes de Cada Commit

Cuando hagas `git commit`, se ejecutan automáticamente estos checks:

#### 1. **Limpieza de Archivos**
- ✂️ Elimina espacios en blanco al final de líneas
- ✂️ Asegura que archivos terminen con nueva línea
- ✂️ Detecta claves privadas accidentalmente agregadas
- ✂️ Previene archivos muy grandes (>1MB)

#### 2. **Formato de Código Python**
- 🎨 **Black**: Formatea código con estilo consistente
- 📦 **isort**: Ordena imports alfabéticamente
- 🧹 **autoflake**: Elimina imports y variables sin usar

#### 3. **Validación de Código**
- 🔍 **flake8**: Verifica errores de sintaxis y estilo PEP 8

#### 4. **Validación de Archivos**
- ✓ Sintaxis YAML correcta
- ✓ Sintaxis JSON correcta
- ✓ No hay marcadores de merge conflict

### Al Escribir el Mensaje de Commit

El hook `commit-msg` valida que tu mensaje siga **Conventional Commits**:

```
✅ VÁLIDO:
feat: add user authentication
fix: resolve database connection error
docs: update README with setup instructions

❌ INVÁLIDO:
added some stuff
fixed bug
update
refactor: improve dataset service   (refactor no está permitido)
test: add unit tests                (test no está permitido)
```

---

## Conventional Commits

### Formato Requerido

```
<tipo>: <descripción>

[cuerpo opcional]

[footer opcional]
```

### Tipos Permitidos

Este proyecto usa un conjunto simplificado de tipos de commit:

| Tipo | Uso | Ejemplo |
|------|-----|---------|
| `feat` | Nueva funcionalidad | `feat: add materials dataset export` |
| `fix` | Corrección de bug | `fix: resolve CSV parsing error` |
| `docs` | Documentación | `docs: add API documentation` |

**Nota:** Solo estos tres tipos están permitidos. Cualquier otro tipo será rechazado por el hook de commit.

### Ejemplos Completos

```bash
# Nueva funcionalidad
git commit -m "feat: add CSV export functionality"

# Corrección de bug
git commit -m "fix: resolve database connection timeout"

# Documentación
git commit -m "docs: update API documentation"

# Con descripción más larga
git commit -m "fix: resolve database connection timeout

The connection timeout was too short for large datasets.
Increased timeout from 5s to 30s and added retry logic.

Fixes #123"

# Con breaking change
git commit -m "feat!: change API response format

BREAKING CHANGE: The API now returns data in a new format.
Clients need to update their parsers."
```

---

## Flujo de Trabajo

### 1. Hacer Cambios

```bash
# Editas código normalmente
vim app/modules/dataset/models.py
```

### 2. Preparar Commit

```bash
# Añadir archivos
git add .
```

### 3. Commit (Hooks se Ejecutan Automáticamente)

```bash
git commit -m "feat: add new dataset field"
```

**Lo que sucede:**
```
Trim trailing whitespace.................................................Passed
Fix end of files.........................................................Passed
Check YAML syntax........................................................Passed
Check for large files....................................................Passed
Format code with Black...................................................Passed
Sort imports with isort..................................................Passed
Remove unused imports/variables..........................................Passed
Lint with flake8.........................................................Passed
Validate commit message..................................................Passed
[feature/my-feature abc1234] feat: add new dataset field
```

### 4. Si Hay Errores

```bash
git commit -m "added stuff"  # ❌ Mensaje inválido

Validate commit message..................................................Failed
- hook id: conventional-pre-commit
- duration: 0.05s

[Commit message] "added stuff"
Your commit message does not follow Conventional Commits format
Expected: <type>: <description>
```

**Solución:** Escribe un mensaje válido:
```bash
git commit -m "feat: add stuff"  # ✅
```

---

## Comandos Útiles

### Ejecutar Todos los Hooks Manualmente

```bash
# En todos los archivos
pre-commit run --all-files

# Solo en archivos staged
pre-commit run
```

### Actualizar Hooks

```bash
# Actualizar a últimas versiones
pre-commit autoupdate
```

### Saltar Hooks (No Recomendado)

```bash
# Solo si es absolutamente necesario
git commit -m "feat: something" --no-verify
```

**Nota:** Úsalo solo en casos excepcionales. Los hooks están para ayudarte.

---

## Solución de Problemas

### Hook Falla: "Black would reformat file"

**Qué significa:** Black quiere reformatear tu código.

**Solución:** Black ya lo reformateó automáticamente, solo haz commit de nuevo:
```bash
git add .
git commit -m "feat: my feature"
```

### Hook Falla: "flake8"

**Qué significa:** Hay errores de sintaxis o estilo.

**Solución:** Lee el error y corrígelo:
```bash
# Ver errores específicos
flake8 app/

# O usa el linter
rosemary linter
rosemary linter:fix
```

### Mensaje de Commit Rechazado

**Qué significa:** Tu mensaje no sigue Conventional Commits.

**Solución:** Usa uno de los tipos permitidos:
```bash
git commit -m "feat: descripción clara"
```

### Desinstalar Hooks

```bash
# Si necesitas desinstalar temporalmente
pre-commit uninstall
pre-commit uninstall --hook-type commit-msg
```

---

## Configuración

La configuración está en `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        args: ['--line-length=120']
```

Para modificar comportamiento, edita este archivo.

---

## Ventajas

### Para Ti
- ✅ No necesitas recordar formatear código
- ✅ No necesitas ejecutar linter manualmente
- ✅ Commits siempre bien formateados
- ✅ Código consistente automáticamente

### Para el Equipo
- ✅ Todo el código sigue mismo estilo
- ✅ PRs más limpios
- ✅ Menos comentarios de review sobre estilo
- ✅ Historial de commits legible

### Para el Proyecto
- ✅ Mayor calidad de código
- ✅ Menos bugs
- ✅ Codebase más profesional
- ✅ Onboarding más fácil

---

## Integración con CI/CD

Los mismos checks se ejecutarán en GitHub Actions, pero los pre-commit hooks te permiten detectar problemas **localmente antes de push**.

**Flujo:**
1. Pre-commit hooks (local) → Detección inmediata
2. GitHub Actions (remoto) → Verificación adicional

---

## FAQ

### ¿Puedo agregar más hooks?

Sí, edita `.pre-commit-config.yaml` y ejecuta:
```bash
pre-commit install
```

### ¿Afecta el rendimiento?

Los hooks tardan ~2-5 segundos. Es mínimo comparado con el tiempo que ahorras.

### ¿Qué pasa si trabajo offline?

Los hooks funcionan offline después de la primera ejecución.

### ¿Funciona en Windows?

Sí, pre-commit funciona en Windows, Linux y macOS.

---

## Recursos

- **Documentación oficial:** https://pre-commit.com/
- **Conventional Commits:** https://www.conventionalcommits.org/
- **Black:** https://black.readthedocs.io/
- **flake8:** https://flake8.pycqa.org/

---

**¿Problemas?** Abre un issue o pregunta al equipo.
