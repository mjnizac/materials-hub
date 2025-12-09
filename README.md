# Materials Hub

[![Tests](https://github.com/mjnizac/materials-hub/actions/workflows/CI_tests_unitarios.yml/badge.svg)](https://github.com/mjnizac/materials-hub/actions)
[![Lint](https://github.com/mjnizac/materials-hub/actions/workflows/CI_lint.yml/badge.svg)](https://github.com/mjnizac/materials-hub/actions)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=MaterialHub-Organization_materials-hub&metric=alert_status)](https://sonarcloud.io/dashboard?id=MaterialHub-Organization_materials-hub)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=MaterialHub-Organization_materials-hub&metric=coverage)](https://sonarcloud.io/dashboard?id=MaterialHub-Organization_materials-hub)
[![Release](https://img.shields.io/github/v/release/mjnizac/materials-hub)](https://github.com/mjnizac/materials-hub/releases)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/github/license/mjnizac/materials-hub)](LICENSE)

**Repositorio de datasets de materiales científicos** - Plataforma web para almacenar, compartir y gestionar datasets de propiedades de materiales siguiendo principios de Open Science.

Desarrollado por **DiversoLab** en la Universidad de Sevilla.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Comandos Principales](#-comandos-principales)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Documentación Adicional](#-documentación-adicional)
- [Contribuir](#-contribuir)

---

## ✨ Características

- 📊 **Gestión de Datasets de Materiales**: Almacena datasets con propiedades de materiales (CSV)
- 🔍 **Sistema de Recomendaciones**: Descubre datasets relacionados basados en tags, autores y propiedades
- 👥 **Gestión de Usuarios**: Sistema de autenticación y perfiles de usuario
- 🌐 **Integración Zenodo**: Publicación de datasets con DOI
- 🧪 **Testing Completo**: Suite de tests unitarios, integración y E2E
- 🎨 **UI Moderna**: Interfaz responsive con Bootstrap

---

## 🔧 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.9+**
- **PostgreSQL** (14+)
- **Node.js y npm** (para dependencias frontend)
- **Git**

### Herramientas Opcionales

- **Docker** (si prefieres usar contenedores)
- **pg_dump** (para backups automáticos de BD)

---

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/materials-hub.git
cd materials-hub
```

### 2. Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
# Dependencias Python
pip install -r requirements.txt

# Dependencias Node (si aplica)
npm install

# Instalar pre-commit hooks (calidad de código automática)
pre-commit install
pre-commit install --hook-type commit-msg
```

**Nota:** Los pre-commit hooks formatean y validan tu código automáticamente antes de cada commit. Ver [Guía de Pre-commit Hooks](docs/pre-commit-hooks-guide.md) para más detalles.

### 4. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con la siguiente configuración:

```bash
# Aplicación
FLASK_APP_NAME=MaterialsHub
FLASK_ENV=development
DOMAIN=localhost
SECRET_KEY=tu-clave-secreta-aqui

# Base de Datos
POSTGRES_HOSTNAME=localhost
POSTGRES_PORT=5432
POSTGRES_USER=materialhub_user
POSTGRES_PASSWORD=tu-password
POSTGRES_DATABASE=materialhub
POSTGRES_TEST_DATABASE=materialhub_test

# Directorio de trabajo
WORKING_DIR=

# Zenodo (opcional - para integración)
ZENODO_API_TOKEN=tu-token-aqui
```

**Importante:** Cambia `tu-password` y `SECRET_KEY` por valores seguros.

### 5. Configurar Base de Datos

Asegúrate de que PostgreSQL esté ejecutándose y crea la base de datos:

```bash
# Conectar a PostgreSQL
psql -U postgres
```

```sql
-- Crear usuario
CREATE USER materialhub_user WITH PASSWORD 'tu-password';

-- Crear base de datos principal
CREATE DATABASE materialhub ENCODING 'UTF8';

-- Crear base de datos de tests
CREATE DATABASE materialhub_test ENCODING 'UTF8';

-- Dar permisos
GRANT ALL PRIVILEGES ON DATABASE materialhub TO materialhub_user;
GRANT ALL PRIVILEGES ON DATABASE materialhub_test TO materialhub_user;

-- En PostgreSQL 15+, también necesitas dar permisos en el schema
\c materialhub
GRANT ALL ON SCHEMA public TO materialhub_user;
\c materialhub_test
GRANT ALL ON SCHEMA public TO materialhub_user;

\q
```

### 6. Inicializar Base de Datos con Datos de Prueba

Este comando creará todas las tablas y las poblará con datos de ejemplo:

```bash
rosemary db:setup
```

**Salida esperada:**
```
Starting database setup...

[1/2] Running database migrations...
Migrations completed successfully.

[2/2] Seeding database with test data...
UserSeeder performed.
DataSetSeeder performed.
MaterialsDatasetSeeder performed.
...

Database setup completed successfully!
```

### 7. Verificar Instalación

```bash
# Comprobar estado de la base de datos
rosemary db:status

# Deberías ver:
# Connection: ✓ Connected to 'materialhub'
# Migration: xxx (head)
# Tables: 20
# etc.
```

### 8. Ejecutar la Aplicación

```bash
# Iniciar servidor de desarrollo
flask run

# O alternativamente (cuando esté implementado):
# rosemary run
```

La aplicación estará disponible en: **http://localhost:5000**

### 9. Acceso Inicial

Usuarios de prueba creados por el seeder:

- **Email:** user@example.com
  **Password:** 1234

---

## 🎮 Comandos Principales

### Base de Datos

```bash
# Setup completo (migraciones + datos de prueba)
rosemary db:setup

# Ver estado de la base de datos
rosemary db:status

# Crear nueva migración después de cambiar modelos
rosemary db:migrate "descripción del cambio"

# Aplicar migraciones pendientes (con backup automático)
rosemary db:upgrade

# Poblar base de datos con datos de prueba
rosemary db:seed

# Resetear base de datos (¡cuidado!)
rosemary db:reset -y

# Abrir consola PostgreSQL
rosemary db:console
```

### Testing

```bash
# Ejecutar todos los tests (unit + integration)
pytest -v

# Solo tests unitarios
pytest -m unit -v

# Solo tests de integración
pytest -m integration -v

# Tests de un módulo específico
pytest app/modules/dataset/tests/ -v

# Tests con reporte de cobertura
pytest --cov=app --cov-report=html --cov-report=term

# Ver reporte HTML de cobertura (después de ejecutar el comando anterior)
# El reporte se genera en htmlcov/index.html
```

**Estructura de tests por módulo:**
- Cada módulo tiene su carpeta `tests/` con:
  - `test_unit.py` - Tests unitarios (servicios, modelos, repositorios)
  - `test_integration.py` - Tests de integración (rutas, API)
  - `locustfile.py` - Tests de carga con Locust

**Ejecutar tests de carga (Locust):**
```bash
# Todos los tests de carga
locust --host=http://localhost:5000

# Tests de un módulo específico
locust -f app/modules/dataset/tests/locustfile.py --host=http://localhost:5000

# Interfaz web disponible en: http://localhost:8089
```

### Desarrollo

```bash
# Crear nuevo módulo
rosemary make:module nombre_modulo

# Listar todos los módulos
rosemary module:list

# Listar rutas de la aplicación
rosemary route:list

# Listar rutas de un módulo específico
rosemary route:list dataset
```

### Calidad de Código

```bash
# Ejecutar linter (flake8)
rosemary linter

# Auto-formatear código (black + isort + autoflake)
rosemary linter:fix
```

### Utilidades

```bash
# Ver variables de entorno
rosemary env

# Actualizar dependencias
rosemary update          # pip + npm
rosemary update:pip      # solo pip
rosemary update:npm      # solo npm

# Limpiar cache y logs
rosemary clear:cache
rosemary clear:log
rosemary clear:uploads
```

---

## 📁 Estructura del Proyecto

```
materials-hub/
├── app/                          # Aplicación Flask
│   ├── modules/                  # Módulos de la aplicación
│   │   ├── auth/                 # Autenticación y usuarios
│   │   ├── dataset/              # Gestión de datasets
│   │   │   ├── models.py         # Modelos (UVLDataset, MaterialsDataset)
│   │   │   ├── routes.py         # Rutas y vistas
│   │   │   ├── services.py       # Lógica de negocio
│   │   │   ├── repositories.py   # Acceso a datos
│   │   │   └── templates/        # Plantillas HTML
│   │   └── ...
│   ├── __init__.py               # Factory de la app
│   └── static/                   # CSS, JS, imágenes
├── core/                         # Funcionalidad core
│   ├── configuration/            # Configuración
│   ├── managers/                 # Gestores (logging, módulos, etc.)
│   └── seeders/                  # Sistema de seeders
├── migrations/                   # Migraciones de base de datos
│   └── versions/                 # Archivos de migración
├── rosemary/                     # CLI de Rosemary
│   ├── commands/                 # Comandos CLI
│   │   ├── db_setup.py
│   │   ├── db_migrate.py
│   │   ├── db_upgrade.py
│   │   └── ...
│   └── cli.py                    # CLI principal
├── docs/                         # Documentación
│   ├── database_setup_guide.md
│   └── ...
├── backups/                      # Backups automáticos de BD
├── uploads/                      # Archivos subidos
├── .env                          # Variables de entorno (no en git)
├── requirements.txt              # Dependencias Python
├── pyproject.toml               # Configuración del proyecto
└── README.md                     # Este archivo
```

---

## 📚 Documentación Adicional

- **[Guía de Configuración de Base de Datos](docs/database_setup_guide.md)** - Comandos detallados de gestión de BD
- **[Guía de Pre-commit Hooks](docs/pre-commit-hooks-guide.md)** - Calidad de código automática
- **[Implementación de Materials Dataset](docs/materials_dataset_implementation_summary.md)** - Detalles técnicos
- **[Guía de Testing](docs/testing_guide.md)** - Cómo ejecutar y escribir tests
- **[Documentación API](docs/api_documentation.md)** - Endpoints de la API

---

## 🤝 Contribuir

### Flujo de Trabajo

1. Crea una rama para tu feature: `git checkout -b feature/mi-feature`
2. Haz tus cambios y commits: `git commit -m "feat: descripción"`
3. Ejecuta los tests: `pytest -v`
4. Ejecuta el linter: `rosemary linter:fix`
5. Push a tu rama: `git push origin feature/mi-feature`
6. Crea un Pull Request

### Estándares de Código

- **Python**: Seguimos PEP 8 (verificado con flake8)
- **Formato**: Auto-formateado con Black (120 caracteres por línea)
- **Commits**: Usamos [Conventional Commits](https://www.conventionalcommits.org/)
  ```bash
  feat: add new feature
  fix: resolve bug
  docs: update documentation
  ```
- **Tests**: Todo nuevo código debe incluir tests
- **Documentación**: Documenta funciones y clases complejas
- **Pre-commit Hooks**: Instalados automáticamente, formatean y validan antes de commit

### Crear un Nuevo Módulo

```bash
# Crear estructura completa del módulo
rosemary make:module mi_modulo

# Esto crea:
# - models.py, routes.py, services.py, repositories.py
# - templates/, assets/, tests/
# - Todo listo para empezar a desarrollar
```

---

## 🐛 Solución de Problemas

### Error de Conexión a Base de Datos

```bash
# Verificar que PostgreSQL esté ejecutándose
sudo systemctl status postgresql

# Verificar credenciales en .env
rosemary env

# Probar conexión
rosemary db:console
```

### Error en Migraciones

```bash
# Ver estado actual
rosemary db:status

# Si hay conflictos, resetear (¡cuidado con datos!)
rosemary db:reset --clear-migrations -y
rosemary db:setup -y
```

### Dependencias Faltantes

```bash
# Reinstalar todas las dependencias
pip install -r requirements.txt --force-reinstall
npm install
```

---

## 📝 Licencia

Este proyecto es parte de una iniciativa académica de la Universidad de Sevilla - DiversoLab.

---

## 👥 Equipo

Desarrollado por el equipo de **DiversoLab** en la Universidad de Sevilla.

- **Repositorio:** [GitHub](https://github.com/tu-usuario/materials-hub)
- **Issues:** [GitHub Issues](https://github.com/tu-usuario/materials-hub/issues)

---

## 🙏 Agradecimientos

- Universidad de Sevilla
- DiversoLab
- Todos los contribuidores del proyecto

---

**¿Necesitas ayuda?** Revisa la [documentación](docs/) o abre un [issue](https://github.com/tu-usuario/materials-hub/issues).
