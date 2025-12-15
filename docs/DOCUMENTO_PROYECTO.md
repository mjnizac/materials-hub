# Documento del Proyecto - Materials Hub

---

## Información del Equipo

**Proyecto:** Materials Hub
**Curso Académico:** 2025/2026
**Asignatura:** Evolución y Gestión de la Configuración
**Grupo:** G1 (Jesús Moreno) - Mañana

### Miembros del Equipo

- **Niza Cobo, Manuel Jesús**
- **Ruiz Vázquez, María José**

---

## Tabla de Contenidos

1. [Indicadores del Proyecto](#indicadores-del-proyecto)
2. [Integración con Otros Equipos](#integración-con-otros-equipos)
3. [Resumen Ejecutivo](#resumen-ejecutivo)
4. [Descripción del Sistema](#descripción-del-sistema)
5. [Visión Global del Proceso de Desarrollo](#visión-global-del-proceso-de-desarrollo)
6. [Entorno de Desarrollo](#entorno-de-desarrollo)
7. [Ejercicio de Propuesta de Cambio](#ejercicio-de-propuesta-de-cambio)
8. [Conclusiones y Trabajo Futuro](#conclusiones-y-trabajo-futuro)

---

## 1. Indicadores del Proyecto

### Métricas del Equipo

| Miembro del Equipo | Horas | Commits | LoC | Test | Issues | Work Item | Dificultad |
|-------------------|-------|---------|-----|------|--------|-----------|------------|
| Niza Cobo, Manuel Jesús | 12 | 18 | 1,800 | 18 | 4 | WI-001: Sistema de versionado de datasets | H |
| Niza Cobo, Manuel Jesús | 10 | 15 | 1,500 | 8 | 3 | WI-002: Implementación de Fakenodo | H |
| Niza Cobo, Manuel Jesús | 8 | 12 | 1,200 | 6 | 3 | WI-003: Sistema de recomendaciones | H |
| Niza Cobo, Manuel Jesús | 15 | 20 | 2,000 | 15 | 5 | WI-004: Comparación entre versiones | H |
| Niza Cobo, Manuel Jesús | 10 | 14 | 1,500 | 10 | 3 | WI-005: Endpoint de estadísticas | M |
| Niza Cobo, Manuel Jesús | 8 | 10 | 800 | 0 | 2 | WI-006: Creación de workflows CI/CD | H |
| Niza Cobo, Manuel Jesús | 7 | 11 | 900 | 0 | 2 | WI-007: API REST con Swagger | M |
| Niza Cobo, Manuel Jesús | 9 | 12 | 700 | 0 | 1 | WI-009: Configuración de pre-commit hooks | L |
| Ruiz Vázquez, María José | 12 | 10 | 1,500 | 12 | 4 | WI-010: Formulario de creación de datasets (NewDataset) | M |
| Ruiz Vázquez, María José | 10 | 8 | 1,200 | 92 | 3 | WI-011: Testing unitarios e integración | H |
| Ruiz Vázquez, María José | 14 | 12 | 1,800 | 0 | 4 | WI-012: Configuración Docker | H |
| Ruiz Vázquez, María José | 8 | 10 | 1,000 | 0 | 3 | WI-013: Despliegue en Render | M |
| Ruiz Vázquez, María José | 6 | 6 | 500 | 0 | 2 | WI-014: Configuración Vagrant | L |
| Ruiz Vázquez, María José | 9 | 7 | 900 | 0 | 2 | WI-015: Interfaz de usuario y templates | M |
| Ruiz Vázquez, María José | 6 | 3 | 418 | 0 | 0 | WI-016: Documentación del proyecto | L |
| **TOTAL** | **168** | **203** | **20,018** | **161** | **49** | - | **H(7)/M(8)/L(3)** |

### Enlaces a Evidencias

No se ha podido realizar un seguimiento exacto de horas durante el proyecto

---

## 2. Integración con Otros Equipos

**No aplica** - El proyecto no ha realizado integraciones con otros equipos durante este periodo.

---

## 3. Resumen Ejecutivo

**Materials Hub** es una plataforma web desarrollada para la gestión, almacenamiento y compartición de datasets de propiedades de materiales científicos. El proyecto representa una solución integral para investigadores que necesitan almacenar, versionar, compartir y descubrir datasets de materiales de manera eficiente y organizada.

### Evolución del Proyecto

El proyecto experimentó una transformación significativa a lo largo de su desarrollo. Inició como "syssoft-hub" con 6 miembros enfocado en documentación de proyectos de software. Tras el primer milestone, el equipo decidió cambiar completamente el enfoque hacia "Materials Hub", un repositorio especializado de datasets de materiales científicos. Esta transición permitió al equipo concentrarse en un dominio específico con necesidades reales y bien definidas dentro de la comunidad científica de ciencia de materiales.

El cambio de enfoque supuso un rediseño completo del sistema, desde la arquitectura de datos hasta la funcionalidad principal. Se identificó la necesidad crítica de proporcionar una plataforma que no solo almacene datos de materiales, sino que también facilite su versionado, descubrimiento y reutilización. Esta visión guió el desarrollo del sistema hacia su forma actual.

### Objetivos Alcanzados

Materials Hub implementa un conjunto robusto de funcionalidades diseñadas para satisfacer las necesidades de la comunidad científica de materiales:

**1. Gestión Integral de Datasets**

El sistema permite a los investigadores crear, almacenar y gestionar datasets de materiales en formato CSV con validación automática. Cada dataset puede contener múltiples propiedades físicas, químicas y estructurales, incluyendo información sobre nombre del material, fórmula química, estructura cristalina, propiedades medidas (con sus valores y unidades), condiciones experimentales (temperatura, presión), fuente de los datos y niveles de incertidumbre. Esta flexibilidad permite modelar una amplia variedad de datos experimentales y computacionales.

**2. Versionado Automático**

Uno de los componentes más innovadores del sistema es su capacidad de versionado automático. Cada vez que se modifica un dataset, ya sea actualizando metadatos o editando registros individuales, el sistema genera automáticamente una nueva versión. Se implementó un algoritmo híbrido de matching que combina identificación por ID y comparación por contenido, permitiendo rastrear cambios incluso cuando los datos no tienen identificadores únicos. Los usuarios pueden comparar visualmente diferentes versiones, ver qué registros se añadieron, eliminaron o modificaron, y recuperar versiones anteriores cuando sea necesario.

**3. Sistema de Recomendaciones**

Para facilitar el descubrimiento de datasets relacionados, se implementó un sistema de recomendaciones basado en similitud de contenido y metadatos. El sistema analiza tags compartidos, autores comunes y propiedades similares para sugerir datasets que puedan ser de interés para el investigador. Esto fomenta la reutilización de datos y facilita la identificación de trabajos complementarios.

**4. Búsqueda y Exploración**

Los usuarios pueden buscar materiales por nombre o fórmula química, con resultados paginados para facilitar la navegación en colecciones grandes. El sistema incluye páginas de landing públicas para cada dataset, permitiendo que la información sea accesible y descubrible.

**5. Gestión de Usuarios y Perfiles**

Se implementó un sistema completo de autenticación y gestión de usuarios, con soporte para perfiles que incluyen identificadores ORCID, permitiendo la integración con el ecosistema académico. Los usuarios mantienen control de acceso sobre sus propios datasets.

### Arquitectura y Tecnologías

La plataforma está construida sobre una arquitectura web moderna y escalable. El backend utiliza **Flask** (Python 3.12) como framework web, aprovechando su flexibilidad y ecosistema maduro de extensiones. La persistencia de datos se realiza mediante **PostgreSQL**, una base de datos relacional robusta que garantiza integridad de datos y soporta consultas complejas.

La arquitectura modular del sistema separa claramente las responsabilidades en módulos funcionales: autenticación, gestión de datasets, perfiles de usuario, webhooks para CI/CD, y Fakenodo (simulador local de Zenodo para desarrollo y testing). Esta separación facilita el mantenimiento, testing y evolución futura del sistema.

El código base supera las **20,000 líneas**, distribuidas en componentes bien estructurados. El desarrollo ha generado más de **200 commits**, reflejando un proceso iterativo y cuidadoso. El sistema cuenta con una suite de **436 tests** automatizados (246 unitarios, 183 de integración, 7 de interfaz) que cubren tanto funcionalidad unitaria como integración entre componentes.

### Pipeline de Integración y Despliegue Continuo

Se ha implementado un pipeline profesional de CI/CD utilizando **GitHub Actions**, que automatiza todo el proceso desde la validación del código hasta el despliegue en producción:

- **Validación de Commits**: Se verifica automáticamente que todos los commits sigan el estándar Conventional Commits, facilitando la generación de changelogs y la trazabilidad del proyecto.
- **Testing Automatizado**: Pytest ejecuta la suite completa de tests en cada push y pull request, garantizando que no se introduzcan regresiones.
- **Análisis de Calidad**: Flake8 valida el estilo de código según PEP 8, mientras que SonarCloud realiza análisis estático profundo para detectar code smells, bugs potenciales y vulnerabilidades de seguridad.
- **Pre-commit Hooks**: Se configuraron hooks que ejecutan Black (formateo), isort (ordenamiento de imports), flake8 y autoflake antes de cada commit, garantizando calidad desde el momento del desarrollo.
- **Despliegue Automático**: El sistema se despliega automáticamente a producción mediante webhooks cuando se hacen cambios en la rama principal, reduciendo el tiempo entre desarrollo y despliegue.

### Documentación y API REST

El sistema expone una API REST completa con más de **12 endpoints** que permiten operaciones CRUD sobre datasets, carga de archivos CSV, consulta de estadísticas, paginación de registros, búsqueda, y gestión de versiones. Se ha implementado la integración con **Swagger/OpenAPI** para documentación automática de la API, incluyendo ejemplos de uso, schemas de request/response, y una interfaz interactiva. Sin embargo, **aunque la implementación de Swagger está presente en el código, aún no es completamente funcional debido a limitaciones de tiempo**, quedando pendiente para futuras iteraciones del proyecto.

### Impacto y Valor

Materials Hub proporciona una herramienta robusta y escalable para la comunidad científica de ciencia de materiales. El sistema facilita la reproducibilidad de investigaciones al mantener un registro versionado completo de todos los datasets. Fomenta la colaboración entre investigadores mediante la compartición abierta de datos y el sistema de recomendaciones. La arquitectura modular y el código bien estructurado facilitan el mantenimiento y permiten la adición de nuevas funcionalidades en el futuro.

---

## 4. Descripción del Sistema

### 4.1 Visión Funcional

Materials Hub es una aplicación web que funciona como repositorio centralizado de datasets de materiales científicos. El sistema permite el ciclo completo de vida de un dataset:

#### Funcionalidades Principales

**1. Gestión de Datasets**
- Creación de datasets con metadatos completos (título, descripción, autores, tipo de publicación)
- Carga de archivos CSV con validación automática de formato y columnas
- Edición de metadatos y records individuales
- Eliminación con confirmación de seguridad

**2. Sistema de Versionado**
- Generación automática de versiones al modificar metadatos o records
- Comparación visual entre versiones (añadidos, eliminados, modificados)
- Sistema híbrido de matching: ID-based + content-based
- Descripción automática de cambios
- Recuperación de versiones anteriores

**3. Modelo de Datos de Materiales**
El sistema soporta las siguientes propiedades para cada material:
- **Identificación:** material_name, chemical_formula
- **Estructura:** structure_type, composition_method
- **Propiedades:** property_name, property_value, property_unit
- **Condiciones:** temperature, pressure
- **Metadata:** data_source, uncertainty, description

**4. Descubrimiento y Búsqueda**
- Sistema de recomendaciones basado en:
  - Tags compartidos
  - Autores comunes
  - Propiedades similares
- Búsqueda de materiales por nombre o fórmula química
- Paginación de resultados

**5. Gestión de Usuarios**
- Registro y autenticación
- Perfiles de usuario con ORCID
- Control de acceso a datasets propios

### 4.2 Arquitectura Técnica

#### Componentes del Sistema

**Backend (Flask Application)**

```
materials-hub/
├── app/                          # Aplicación Flask principal
│   ├── __init__.py              # Factory pattern con configuración Swagger
│   ├── modules/                 # Módulos funcionales
│   │   ├── auth/               # Autenticación (login, signup, logout)
│   │   ├── dataset/            # Gestión de datasets y materials
│   │   │   ├── models.py       # MaterialsDataset, MaterialRecord, DatasetVersion
│   │   │   ├── services.py     # Lógica de negocio y versionado
│   │   │   ├── routes.py       # Endpoints web
│   │   │   └── api.py          # REST API con Swagger
│   │   ├── profile/            # Gestión de perfiles de usuario
│   │   ├── webhook/            # CD/CI webhook para despliegue
│   │   └── fakenodo/           # Simulador local de Zenodo
│   ├── static/                 # Assets estáticos
│   └── templates/              # Templates Jinja2
├── core/                        # Funcionalidad compartida
│   ├── configuration/          # Gestión de configuración
│   ├── managers/               # Managers (logging, errors, modules)
│   ├── resources/              # Recursos genéricos (CRUD API)
│   └── services/               # Servicios base
├── migrations/                  # Alembic migrations
└── rosemary/                   # CLI personalizado
    └── commands/               # Comandos (db:setup, db:seed, linter, etc.)
```

**Base de Datos (PostgreSQL)**

Modelo relacional con las siguientes tablas principales:

- `user`: Usuarios del sistema
- `materials_dataset`: Datasets de materiales
- `material_record`: Records individuales de materiales
- `dataset_version`: Versiones de datasets
- `dataset_version_record`: Records específicos de cada versión

**API REST**

12 endpoints documentados con Swagger:
- `GET/POST /api/v1/materials-datasets/` - CRUD de datasets
- `GET/PUT/DELETE /api/v1/materials-datasets/<id>` - Operaciones por ID
- `POST /api/v1/materials-datasets/<id>/upload` - Subida de CSV
- `GET /api/v1/materials-datasets/<id>/statistics` - Estadísticas
- `GET /api/v1/materials-datasets/<dataset_id>/records` - Paginación de records
- `GET /api/v1/materials-datasets/<dataset_id>/records/search` - Búsqueda

### 4.3 Cambios Desarrollados para el Proyecto

#### Nuevas Funcionalidades Implementadas

**1. Sistema Completo de Versionado**
- Algoritmo híbrido de matching (ID + contenido)
- Comparación visual de versiones
- Gestión de CSV con/sin record_id
- Snapshots automáticos al editar

**2. API REST con Documentación Swagger**
- Especificaciones OpenAPI completas
- 12 endpoints documentados
- Ejemplos y schemas de request/response
- UI interactiva en `/apidocs/`

**3. Modelo de Datos de Materiales**
- Schema completo para propiedades de materiales
- Validación de datos en CSV
- Soporte para incertidumbre y metadatos
- Parser robusto de CSV con normalización

**4. Pipeline CI/CD Completo**
- 6 workflows de GitHub Actions
- Validación de commits (Conventional Commits)
- Tests automatizados (unitarios + integración)
- Linting y análisis de calidad (flake8, SonarCloud)
- Despliegue automático vía webhook

**5. CLI Rosemary**
- Comandos personalizados para gestión de base de datos
- Setup automático (migraciones + seeders)
- Linter y formateo de código
- Gestión de status de base de datos

**6. Sistema de Hooks**
- Pre-commit hooks (black, isort, flake8, autoflake)
- prepare-commit-msg (emojis automáticos)
- Validación de Conventional Commits

**7. Integración con Servicios Externos**
- SonarCloud (análisis de calidad)
- Docker (contenedorización)

**8. Mejoras de UX**
- Sistema de recomendaciones
- Búsqueda y paginación
- Landing pages públicas
- Flash messages informativos

### 4.4 Subsistemas y Relaciones

#### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                         Web Browser                              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Flask Application                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Auth       │  │   Dataset    │  │   Profile    │          │
│  │   Module     │  │   Module     │  │   Module     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐                              │
│  │   Webhook    │  │   Fakenodo   │                              │
│  │   Module     │  │   Module     │                              │
│  └──────────────┘  └──────────────┘                              │
└──────────┬──────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  users   │  │ datasets │  │ records  │  │ versions │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘

           │
           ▼
┌──────────────────────┐
│  GitHub Actions      │
│  (CI/CD Pipeline)    │
└──────────────────────┘
```

---

## 5. Visión Global del Proceso de Desarrollo

### 5.1 Metodología de Desarrollo

El proyecto sigue una metodología ágil adaptada con integración continua y despliegue continuo (CI/CD). El flujo de trabajo está basado en **Git Flow** con adaptaciones para equipos pequeños.

### 5.2 Flujo de Trabajo

#### Branching Strategy

```
main (producción)
  │
  ├── develop (desarrollo)
  │     │
  │     ├── feature/nueva-funcionalidad
  │     ├── fix/corregir-bug
  │     └── docs/documentacion
  │
  └── hotfix/arreglo-urgente
```

#### Ciclo de Vida de un Cambio

**Ejemplo: Implementar Sistema de Búsqueda de Materiales**

**1. Planificación**
```bash
# Crear issue en GitHub
# Título: "Implementar búsqueda de materiales por nombre/fórmula"
# Labels: enhancement, high-priority
# Asignar a miembro del equipo
```

**2. Desarrollo Local**
```bash
# Checkout desde develop
git checkout develop
git pull origin develop

# Crear rama feature
git checkout -b feature/material-search

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias (si es necesario)
pip install -r requirements.txt

# Ejecutar base de datos local
rosemary db:setup
```

**3. Implementación del Cambio**

Modificar archivos necesarios:
- `app/modules/dataset/repositories.py` - Añadir método `search_materials()`
- `app/modules/dataset/services.py` - Lógica de búsqueda
- `app/modules/dataset/routes.py` - Endpoint web
- `app/modules/dataset/api.py` - Endpoint API REST

**4. Testing Local**
```bash
# Escribir tests
# app/modules/dataset/tests/test_search.py

# Ejecutar tests
pytest -v

# Tests específicos
pytest app/modules/dataset/tests/test_search.py -v

# Cobertura
pytest --cov=app
```

**5. Validación de Calidad**
```bash
# Formateo automático
rosemary linter:fix

# Validación
rosemary linter

# Los pre-commit hooks se ejecutan automáticamente al hacer commit
```

**6. Commit y Push**
```bash
# Add cambios
git add .

# Commit (pre-commit hooks se ejecutan automáticamente)
git commit -m "feat: implementar búsqueda de materiales por nombre/fórmula"
# El hook prepare-commit-msg añade emoji: ✨ feat: ...

# Push a rama feature
git push origin feature/material-search
```

**7. CI/CD Pipeline (Automático)**

GitHub Actions ejecuta:
```yaml
1. ✅ Conventional Commits Validation
2. ✅ Pytest (tests unitarios + integración)
3. ✅ Flake8 (linting)
4. ✅ SonarCloud (análisis de calidad)
5. ✅ Swagger Validation
```

**9. Merge a Develop**
```bash
# Desde GitHub UI o CLI
gh pr merge --merge
```

**11. Deploy a Staging (Automático)**
- Al hacer merge a `develop`, GitHub Actions ejecuta deploy a entorno de staging

**12. Merge a Main (Producción)**
```bash
# Crear PR de develop a main
git checkout develop
git pull origin develop
git checkout main
git pull origin main
git merge develop
git push origin main
```

**13. Deploy a Producción (Automático)**

Cuando se hace push a `main`:
```yaml
1. ✅ Pytest ejecuta
2. ✅ Si tests pasan → Trigger webhook deployment
3. ✅ Webhook recibe POST en /webhook/deploy
4. ✅ Ejecuta en contenedor Docker:
   - git pull origin main
   - pip install -r requirements.txt
   - flask db upgrade
   - Reinicia contenedor
```

### 5.3 Herramientas del Proceso

| Fase | Herramienta | Propósito |
|------|-------------|-----------|
| **Gestión de Proyecto** | GitHub Projects | Kanban board, issues, milestones |
| **Control de Versiones** | Git + GitHub | Versionado de código |
| **Desarrollo** | VSCode + PyCharm | IDEs con soporte Python |
| **Testing** | Pytest | Tests automatizados |
| **Calidad de Código** | Flake8, Black, isort | Linting y formateo |
| **Análisis Estático** | SonarCloud | Detección de code smells, bugs |
| **CI/CD** | GitHub Actions | Pipeline automatizado |
| **Documentación** | Swagger/Flasgger | API documentation |
| **Base de Datos** | PostgreSQL + Alembic | Persistencia y migraciones |
| **CLI** | Rosemary (Click) | Comandos personalizados |
| **Contenedores** | Docker | Despliegue y producción |
| **Monitoreo** | GitHub Actions logs | Tracking de builds |

### 5.4 Políticas de Calidad

**Conventional Commits**
- Formato: `<tipo>(<scope>): <descripción>`
- Tipos permitidos: `feat`, `fix`, `docs`
- Validación automática en pre-commit y CI/CD

**Code Coverage**
- Objetivo: >50% de cobertura
- Monitoreado en SonarCloud

**Code Style**
- PEP 8 (Python)
- Black formatter (120 chars/línea)
- Import ordering con isort

---

## 6. Entorno de Desarrollo

### 6.1 Requisitos del Sistema

#### Software Base
- **Sistema Operativo:** Linux (Ubuntu 24.04 LTS recomendado), macOS, Windows 10/11
- **Python:** 3.12 o superior
- **PostgreSQL:** 14 o superior
- **Git:** 2.30 o superior
- **Node.js:** 18+ (solo para validación de Swagger en CI/CD)

#### Recursos de Hardware Recomendados
- **RAM:** 8GB mínimo, 16GB recomendado
- **Almacenamiento:** 10GB espacio libre
- **Procesador:** 4 cores recomendado

### 6.2 Configuración del Entorno de Desarrollo

#### Paso 1: Clonar el Repositorio

```bash
# HTTPS
git clone https://github.com/mjnizac/materials-hub.git
cd materials-hub

# SSH (recomendado)
git clone git@github.com:mjnizac/materials-hub.git
cd materials-hub
```

#### Paso 2: Entorno Virtual de Python

```bash
# Crear entorno virtual
python3.12 -m venv venv

# Activar entorno virtual
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Verificar versión de Python
python --version  # Debe mostrar Python 3.12.x
```

#### Paso 3: Instalar Dependencias

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias del proyecto
pip install -r requirements.txt

# Verificar instalación
pip list | grep Flask  # Debe mostrar Flask y extensiones
```

**Dependencias Principales** (ver `requirements.txt`):
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-Migrate 4.0.5
- Flask-Login 0.6.3
- Flask-RESTful 0.3.10
- Flasgger 0.9.7.1
- psycopg2-binary 2.9.9
- pytest 7.4.3
- black 23.12.1
- flake8 7.0.0
- isort 5.13.2

#### Paso 4: Configurar PostgreSQL

```bash
# Conectar a PostgreSQL como superusuario
sudo -u postgres psql

# Crear usuario
CREATE USER materialhub_user WITH PASSWORD 'development_password';

# Crear base de datos
CREATE DATABASE materialhub ENCODING 'UTF8';

# Otorgar privilegios
GRANT ALL PRIVILEGES ON DATABASE materialhub TO materialhub_user;

# En PostgreSQL 15+, otorgar permisos en schema
\c materialhub
GRANT ALL ON SCHEMA public TO materialhub_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO materialhub_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO materialhub_user;

# Salir
\q
```

#### Paso 5: Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# Copiar desde ejemplo
cp .env.local.example .env

# Editar con tus configuraciones
nano .env
```

**Contenido de `.env`:**
```bash
# Flask Configuration
FLASK_APP_NAME=MaterialsHub
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
DOMAIN=localhost:5000

# Database Configuration
POSTGRES_HOSTNAME=localhost
POSTGRES_PORT=5432
POSTGRES_USER=materialhub_user
POSTGRES_PASSWORD=development_password
POSTGRES_DATABASE=materialhub

# Working Directory
WORKING_DIR=/home/usuario/materials-hub

# Webhook (solo para producción)
DISABLE_WEBHOOK=true
WEBHOOK_TOKEN=
```

#### Paso 6: Inicializar Base de Datos

```bash
# Setup completo (drop tables + migrations + seed data)
rosemary db:setup

# O paso por paso:
flask db init      # Inicializar migrations (solo primera vez)
flask db migrate -m "Initial migration"  # Crear migración
flask db upgrade   # Aplicar migración
rosemary db:seed   # Cargar datos de prueba
```

#### Paso 7: Instalar Pre-commit Hooks (Opcional pero Recomendado)

```bash
# Instalar pre-commit
pip install pre-commit

# Instalar hooks
pre-commit install
pre-commit install --hook-type commit-msg

# Ejecutar manualmente (opcional)
pre-commit run --all-files
```

#### Paso 8: Verificar Instalación

```bash
# Ejecutar tests
pytest -v

# Ejecutar aplicación
flask run

# La aplicación debe estar disponible en:
# http://localhost:5000
```

**Credenciales de prueba:**
- Email: `user@example.com`
- Password: `1234`

### 6.3 Comandos Útiles de Desarrollo

#### Gestión de Base de Datos
```bash
rosemary db:setup              # Setup completo (limpia, migra, seeda)
rosemary db:status             # Ver estado de BD
rosemary db:migrate "mensaje"  # Crear nueva migración
rosemary db:upgrade            # Aplicar migraciones pendientes
rosemary db:seed               # Cargar datos de prueba
flask db downgrade             # Revertir última migración
```

#### Testing
```bash
pytest -v                      # Todos los tests con verbose
pytest -m unit                 # Solo tests unitarios
pytest -m integration          # Solo tests de integración
pytest --cov=app               # Tests con cobertura
pytest --cov=app --cov-report=html  # Reporte HTML de cobertura
pytest app/modules/dataset/tests/  # Tests de un módulo específico
```

#### Linting y Formateo
```bash
rosemary linter                # Ejecutar flake8
rosemary linter:fix            # Auto-formatear con black + isort
black app rosemary core        # Formatear código
isort app rosemary core        # Ordenar imports
flake8 app rosemary core       # Validar estilo
```

#### Ejecución
```bash
flask run                      # Desarrollo (debug mode)
flask run --host=0.0.0.0      # Accesible desde red local
gunicorn -w 4 -b 0.0.0.0:5000 app:app  # Producción con gunicorn
```

### 6.4 IDEs y Configuración

#### VSCode (Recomendado)

**Extensiones recomendadas** (`.vscode/extensions.json`):
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "ms-python.flake8",
    "tamasfe.even-better-toml",
    "redhat.vscode-yaml"
  ]
}
```

**Configuración** (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "120"],
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true
}
```

### 6.5 Entornos de los Miembros del Equipo

| Miembro | Sistema Operativo | IDE | Python Version | PostgreSQL |
|---------|------------------|-----|----------------|------------|
| Manuel Jesús Niza | Ubuntu 24.04 LTS | VSCode | 3.12.3 | 14.11 |
| María José Ruiz Vázquez | Ubuntu 24.04 LTS | VSCode | 3.12.3 | 14.11 |

### 6.6 Docker (Opcional para Desarrollo)

```bash
# Build imagen
docker build -t materials-hub .

# Ejecutar con docker-compose
docker-compose -f docker/docker-compose.dev.yml up

# La aplicación estará en http://localhost:5000
```

---

## 7. Ejercicio de Propuesta de Cambio

### Caso de Uso: Añadir Filtro de Búsqueda por Rango de Temperatura en la Vista de Materiales

**Contexto:** Los investigadores que visualizan un dataset de materiales necesitan filtrar los registros por rango de temperatura para encontrar datos relevantes a sus condiciones experimentales (por ejemplo, materiales medidos entre 200K y 400K).

**Requerimiento:** Implementar un sistema completo de filtrado por temperatura que incluya:
- Interfaz de usuario (formulario en la vista)
- Lógica de backend (rutas, servicios, repositorio)
- Validación y manejo de casos edge
- Integración con el sistema de paginación existente

### Paso 1: Crear Issue en GitHub

```bash
# Navegar a GitHub Issues
# https://github.com/mjnizac/materials-hub/issues/new

Título: feat: añadir filtro por rango de temperatura en vista de materiales
Labels: enhancement, feature, high-priority
Asignado a: [miembro del equipo]

Descripción:
Como investigador que visualiza un dataset, quiero filtrar los registros
por rango de temperatura para encontrar datos relevantes a mis condiciones
experimentales.

Criterios de aceptación:
- [ ] Formulario en la vista con campos temp_min y temp_max
- [ ] Ruta recibe parámetros GET y aplica filtro
- [ ] Método en repositorio filtra por temperatura (con validaciones)
- [ ] Paginación funciona correctamente con el filtro
- [ ] Validación automática de rangos invertidos
- [ ] Tests unitarios para el método de filtrado
```

### Paso 2: Configurar Entorno Local

```bash
# Asegurarse de estar en develop actualizado
git checkout develop
git pull origin develop

# Crear rama feature
git checkout -b feature/temperature-filter

# Activar entorno virtual
source venv/bin/activate

# Verificar que la base de datos está actualizada
rosemary db:status

# Si hay migraciones pendientes
flask db upgrade

# Ejecutar tests para verificar que todo funciona
pytest -v
```

### Paso 3: Implementar el Cambio

#### 3.1 Mejorar el Método de Filtrado en el Repositorio

**Archivo:** `app/modules/dataset/repositories.py`

Buscar el método `filter_by_temperature_range` existente (alrededor de la línea 216) y modificarlo:

```python
# ANTES (método existente):
def filter_by_temperature_range(self, dataset_id: int, min_temp: int = None, max_temp: int = None):
    """Filter records by temperature range"""
    query = self.model.query.filter_by(materials_dataset_id=dataset_id)

    if min_temp is not None:
        query = query.filter(self.model.temperature >= min_temp)
    if max_temp is not None:
        query = query.filter(self.model.temperature <= max_temp)

    return query.all()

# DESPUÉS (método mejorado):
def filter_by_temperature_range(self, dataset_id, temp_min=None, temp_max=None):
    query = self.model.query.filter_by(materials_dataset_id=dataset_id)
    query = query.filter(self.model.temperature.isnot(None))

    if temp_min is not None and temp_max is not None and temp_min > temp_max:
        temp_min, temp_max = temp_max, temp_min

    if temp_min is not None:
        query = query.filter(self.model.temperature >= float(temp_min))

    if temp_max is not None:
        query = query.filter(self.model.temperature <= float(temp_max))

    return query.order_by(self.model.temperature.asc()).all()
```

**Cambios realizados:**
1. **Cambio de nombres de parámetros**: `min_temp`/`max_temp` → `temp_min`/`temp_max` (convención más consistente)
2. **Filtrar NULL**: `query.filter(self.model.temperature.isnot(None))` excluye registros sin temperatura
3. **Validación automática**: Si `temp_min > temp_max`, se intercambian automáticamente
4. **Conversión a float**: `float(temp_min)` y `float(temp_max)` para asegurar tipos correctos
5. **Ordenamiento**: `order_by(self.model.temperature.asc())` ordena resultados ascendentemente
6. **Retorno explícito**: `.all()` al final para ejecutar la query

#### 3.2 Añadir Lógica en Routes

**Archivo:** `app/modules/dataset/routes.py`

En la ruta `view_materials_dataset` (alrededor de la línea 492), añadir la lógica para recibir y procesar los parámetros de temperatura:

```python
# AÑADIR después de los parámetros de paginación (línea ~544):

# -----------------------------
# Temperature range filter
# -----------------------------
temp_min = request.args.get("temp_min", default=None, type=float)
temp_max = request.args.get("temp_max", default=None, type=float)

# Si vienen invertidos, los corregimos
if temp_min is not None and temp_max is not None and temp_min > temp_max:
    temp_min, temp_max = temp_max, temp_min

# -----------------------------
# Records query (aplicar filtro si corresponde)
# -----------------------------
if temp_min is not None or temp_max is not None:
    records_query = material_record_repository.filter_by_temperature_range(
        dataset_id=dataset_id,
        temp_min=temp_min,
        temp_max=temp_max,
    )
else:
    records_query = material_record_repository.model.query.filter_by(
        materials_dataset_id=dataset_id
    )

# Orden por defecto
records_query = records_query.order_by(material_record_repository.model.id.asc())

# Paginar el Query (esto arregla el problema de len(Query))
pagination = records_query.paginate(page=page, per_page=per_page, error_out=False)
records = pagination.items
total = pagination.total
total_pages = pagination.pages or 1
```

**MODIFICAR** el `render_template` para pasar las variables de temperatura:

```python
response = make_response(
    render_template(
        "dataset/view_materials_dataset.html",
        dataset=dataset,
        records=records,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        recommended_datasets=recommended_datasets,
        temp_min=temp_min,  # ← AÑADIR
        temp_max=temp_max,  # ← AÑADIR
    )
)
```

#### 3.3 Añadir Método Auxiliar en Services (Opcional)

**Archivo:** `app/modules/dataset/services.py`

Al final de la clase `MaterialsDatasetService` (alrededor de la línea 896), añadir un método auxiliar:

```python
def get_records_query(
    self,
    dataset_id: int,
    temp_min: float | None = None,
    temp_max: float | None = None,
):
    """
    Devuelve un Query de MaterialRecord del dataset, con filtro opcional por temperatura.
    """
    if temp_min is not None or temp_max is not None:
        return self.material_record_repository.filter_by_temperature_range(
            dataset_id=dataset_id,
            temp_min=temp_min,
            temp_max=temp_max,
        )
    return self.material_record_repository.model.query.filter_by(materials_dataset_id=dataset_id)
```

> **Nota:** Este método en services.py es opcional en este caso, ya que la lógica se implementó directamente en routes.py. Se incluye para mostrar una alternativa más modular.

#### 3.4 Añadir Formulario de Filtro en la Vista

**Archivo:** `app/modules/dataset/templates/dataset/view_materials_dataset.html`

Buscar la sección donde se muestran los "Material Records" (alrededor de la línea 489) y **AÑADIR** el formulario de filtro después del buscador y antes de la lista de registros:

```html
<!-- AÑADIR después del buscador de materiales -->
<div class="list-group-item">
    <form method="GET" class="row g-2 align-items-end">
        <div class="col-6">
            <label class="form-label mb-1" for="tempMin">Temp min (K)</label>
            <input type="number" step="any" class="form-control" id="tempMin" name="temp_min"
                   value="{{ request.args.get('temp_min','') }}" placeholder="e.g. 200">
        </div>
        <div class="col-6">
            <label class="form-label mb-1" for="tempMax">Temp max (K)</label>
            <input type="number" step="any" class="form-control" id="tempMax" name="temp_max"
                   value="{{ request.args.get('temp_max','') }}" placeholder="e.g. 400">
        </div>

        <!-- mantener paginación si ya se usa -->
        <input type="hidden" name="page" value="{{ request.args.get('page', page|default(1)) }}">
        <input type="hidden" name="per_page" value="{{ request.args.get('per_page', per_page|default(20)) }}">

        <div class="col-12 d-flex gap-2">
            <button type="submit" class="btn btn-outline-primary btn-sm w-100">
                <i data-feather="filter"></i> Apply temperature filter
            </button>

            <a class="btn btn-outline-secondary btn-sm"
               href="{{ url_for('dataset.view_materials_dataset', dataset_id=dataset.id, page=page|default(1), per_page=per_page|default(20)) }}">
                <i data-feather="rotate-ccw"></i> Reset
            </a>
        </div>

        <small class="text-muted mt-2 d-block">
            Tip: leave one field empty to filter only by min or max.
        </small>
    </form>
</div>
```

**MODIFICAR** los enlaces de paginación para mantener el filtro:

```html
<!-- En la paginación (alrededor de línea 600), CAMBIAR los url_for para incluir temp_min y temp_max -->

<!-- Ejemplo en el botón Previous: -->
<a class="page-link"
   href="{{ url_for('dataset.view_materials_dataset',
                    dataset_id=dataset.id,
                    page=page-1,
                    per_page=per_page,
                    temp_min=temp_min,
                    temp_max=temp_max) }}">
    Previous
</a>

<!-- Repetir para todos los enlaces de paginación (Next, números de página, etc.) -->
```

#### 3.5 Actualizar Tests Unitarios

**Archivo:** `app/modules/dataset/tests/test_unit.py`

Buscar el test `test_material_record_repository_filter_by_temperature_range` (alrededor de la línea 256) y actualizar los nombres de parámetros:

```python
# ANTES:
repo = MaterialRecordRepository()

# Test min temperature filter
results = repo.filter_by_temperature_range(dataset.id, min_temp=300)
assert len(results) == 3

# Test max temperature filter
results = repo.filter_by_temperature_range(dataset.id, max_temp=300)
assert len(results) == 3

# Test range filter
results = repo.filter_by_temperature_range(dataset.id, min_temp=200, max_temp=400)
assert len(results) == 3

# DESPUÉS:
repo = MaterialRecordRepository()

# Test min temperature filter
results = repo.filter_by_temperature_range(dataset.id, temp_min=300)
assert len(results) == 3

# Test max temperature filter
results = repo.filter_by_temperature_range(dataset.id, temp_max=300)
assert len(results) == 3

# Test range filter
results = repo.filter_by_temperature_range(dataset.id, temp_min=200, temp_max=400)
assert len(results) == 3
```

**Cambios en tests:**
- Todos los parámetros `min_temp` → `temp_min`
- Todos los parámetros `max_temp` → `temp_max`

### Paso 4: Ejecutar Tests

```bash
# Ejecutar test específico
pytest app/modules/dataset/tests/test_unit.py::test_material_record_repository_filter_by_temperature_range -v

# Ejecutar todos los tests unitarios
pytest -m unit -v

# Ejecutar todos los tests
pytest -v

# Verificar cobertura
pytest --cov=app --cov-report=term-missing
```

**Salida esperada:**
```
test_material_record_repository_filter_by_temperature_range PASSED [100%]

====== 1 passed in 0.42s ======
```

### Paso 5: Validar Código

```bash
# Formatear código automáticamente
rosemary linter:fix

# Verificar estilo
rosemary linter

# Si hay errores de flake8, corregirlos manualmente
```

**Salida esperada:**
```
✓ black formatting: OK
✓ isort imports: OK
✓ flake8 linting: OK
```

### Paso 6: Verificar Funcionamiento Local (Opcional)

```bash
# Activar shell de Python
flask shell

# Probar el método mejorado
>>> from app.modules.dataset.repositories import MaterialRecordRepository
>>> repo = MaterialRecordRepository()
>>> results = repo.filter_by_temperature_range(dataset_id=1, temp_min=200, temp_max=400)
>>> len(results)
3
>>> results[0].temperature  # Verificar que está ordenado
200.0
```

### Paso 7: Commit

```bash
# Revisar cambios
git status
git diff

# Añadir archivos modificados
git add app/modules/dataset/repositories.py
git add app/modules/dataset/routes.py
git add app/modules/dataset/services.py
git add app/modules/dataset/templates/dataset/view_materials_dataset.html
git add app/modules/dataset/tests/test_unit.py

# Commit (pre-commit hooks ejecutan automáticamente)
git commit -m "feat: añadir filtro por rango de temperatura en vista de materiales"

# El hook prepare-commit-msg añade:
# ✨ feat: añadir filtro por rango de temperatura en vista de materiales

# El hook pre-commit ejecuta:
# - black (formateo)
# - isort (imports)
# - flake8 (linting)
# - autoflake (unused imports)
# - conventional-pre-commit (formato de mensaje)

# Si todo está OK, el commit se crea
```

### Paso 8: Push

```bash
# Push a rama feature
git push origin feature/temperature-filter
```

### Paso 9: Crear Pull Request

```bash
# Crear PR desde GitHub CLI
gh pr create \
  --base develop \
  --head feature/temperature-filter \
  --title "feat: añadir filtro por rango de temperatura en vista de materiales" \
  --body "## Cambios
- Mejora método filter_by_temperature_range en MaterialRecordRepository
  - Validación automática de rangos invertidos
  - Filtrado de registros con temperatura NULL
  - Ordenamiento de resultados por temperatura ascendente
- Añade lógica de filtrado en routes.py
  - Recibe parámetros temp_min/temp_max desde GET
  - Aplica filtro condicionalmente
  - Integración con paginación
- Añade método auxiliar en services.py
- Añade formulario de filtro en la vista HTML
  - Inputs para temperatura mínima y máxima
  - Botón para aplicar filtro
  - Botón para resetear filtro
  - Paginación mantiene el filtro activo
- Actualiza tests unitarios con nuevos nombres de parámetros

## Archivos modificados
- app/modules/dataset/repositories.py
- app/modules/dataset/routes.py
- app/modules/dataset/services.py
- app/modules/dataset/templates/dataset/view_materials_dataset.html
- app/modules/dataset/tests/test_unit.py

Closes #XXX"

# O crear PR desde GitHub UI
```

### Paso 10: CI/CD Automático

Una vez creado el PR, GitHub Actions ejecuta automáticamente:

```yaml
1. Conventional Commits Validation
   ✅ Verifica formato del commit: "feat: ..."

2. Pytest
   ✅ Ejecuta todos los tests
   ✅ Verifica que test_unit.py pasa

3. Flake8
   ✅ Verifica estilo de código (repositories, routes, services)

4. SonarCloud
   ✅ Análisis de calidad
   ✅ Detecta code smells, bugs, vulnerabilidades
```

**Ver logs:**
```
GitHub PR → Checks tab → Ver detalles de cada workflow
```

### Paso 11: Code Review

```bash
# Equipo revisa el código en GitHub
# Comentarios y sugerencias
# Ejemplo de comentario:

"Excelente implementación end-to-end. La integración con la paginación está bien resuelta."

# Si hay cambios solicitados
git checkout feature/temperature-filter
# ... hacer cambios ...
git add .
git commit -m "fix: aplicar sugerencias de code review"
git push origin feature/temperature-filter

# El PR se actualiza automáticamente
# CI/CD se ejecuta de nuevo
```

### Paso 12: Merge a Develop

```bash
# Una vez aprobado el PR
gh pr merge --merge

# O desde GitHub UI: "Merge pull request"

# Automáticamente:
# 1. Se hace merge a develop
# 2. Se cierra el PR
# 3. Se cierra el issue relacionado (si se usó "Closes #X")
# 4. Se elimina la rama feature (opcional)
```

### Paso 13: Verificar en Develop

```bash
# Checkout develop
git checkout develop
git pull origin develop

# Ejecutar tests
pytest -v

# Verificar que el cambio está incluido
git log --oneline -5

# Debe mostrar:
# abc1234 ✨ feat: añadir filtro por rango de temperatura en vista de materiales
```

### Resumen del Flujo Completo

```
[1] Issue creado →
[2] Rama feature desde develop →
[3] Implementar cambios en 4 capas:
    - Repositorio (repositories.py) - Método mejorado
    - Ruta (routes.py) - Lógica de filtrado
    - Servicio (services.py) - Método auxiliar
    - Vista (view_materials_dataset.html) - Formulario de filtro
    - Tests (test_unit.py) - Actualización de parámetros
[4] Ejecutar tests localmente →
[5] Validar código con linter →
[6] Commit con hooks →
[7] Push →
[8] Crear PR →
[9] CI/CD automático →
[10] Code review →
[11] Merge a develop →
[12] Verificación en develop
```

**Archivos modificados:**
- `app/modules/dataset/repositories.py` - Método `filter_by_temperature_range` mejorado con validaciones
- `app/modules/dataset/routes.py` - Lógica para recibir y aplicar filtros de temperatura
- `app/modules/dataset/services.py` - Método auxiliar `get_records_query` (opcional)
- `app/modules/dataset/templates/dataset/view_materials_dataset.html` - Formulario de filtro y paginación actualizada
- `app/modules/dataset/tests/test_unit.py` - Parámetros actualizados en tests existentes

**Funcionalidad implementada:**

**Backend:**
1. Método de repositorio con validación de rangos invertidos
2. Filtrado de registros con temperatura NULL
3. Ordenamiento por temperatura ascendente
4. Conversión explícita a float
5. Integración con sistema de paginación

**Frontend:**
1. Formulario con inputs para temp_min y temp_max
2. Botón para aplicar filtro
3. Botón para resetear filtro
4. Paginación mantiene parámetros de filtro activos
5. UX mejorada con placeholders y tips

**Tiempo estimado total:** 2-3 horas

---

## 8. Conclusiones y Trabajo Futuro

### 8.1 Conclusiones

El desarrollo de **Materials Hub** ha representado un ejercicio completo de aplicación de metodologías modernas de ingeniería de software y gestión de la configuración. A lo largo del proyecto, se han alcanzado los siguientes logros:

#### Logros Técnicos

1. **Sistema Completo y Funcional**
   - Implementación exitosa de un repositorio web de datasets de materiales con más de 17,000 líneas de código
   - Arquitectura modular basada en Flask que facilita el mantenimiento y la escalabilidad
   - Sistema robusto de versionado de datasets con algoritmos híbridos de matching

2. **Pipeline CI/CD Profesional**
   - 6 workflows de GitHub Actions que automatizan validación, testing y despliegue
   - Integración con SonarCloud para análisis continuo de calidad
   - Despliegue automático a producción mediante webhooks
   - Pre-commit hooks que garantizan calidad de código antes de cada commit

3. **Cobertura de Tests y Calidad**
   - Suite de 436 tests automatizados (246 unitarios, 183 de integración, 7 de interfaz)
   - Validación automática de estilo de código (flake8, black, isort)
   - Documentación completa de API con Swagger/OpenAPI

4. **Integración con Ecosistema Científico**
   - Modelo de datos compatible con estándares de datos de materiales

#### Uso de Herramientas de Inteligencia Artificial

Durante el desarrollo del proyecto se ha hecho uso de herramientas de inteligencia artificial como asistente técnico en diversas fases del desarrollo. A continuación se detalla el uso realizado:

**1. Generación de Datos de Prueba (Seeders)**
   - Se utilizó IA para generar datos realistas de materiales científicos para los seeders de la base de datos
   - La IA ayudó a crear registros de ejemplo con propiedades físicas coherentes (densidad, punto de fusión, conductividad, etc.)
   - Los datos generados se revisaron y ajustaron manualmente para asegurar su validez científica

**2. Creación y Configuración de Workflows de CI/CD**
   - Consultas sobre sintaxis y mejores prácticas para GitHub Actions
   - Asistencia en la configuración de workflows complejos (validación de commits, análisis de código, despliegue)
   - Revisión y optimización de los archivos YAML de los workflows

**3. Desarrollo de Tests Unitarios e Integración**
   - Generación de casos de prueba para funcionalidades complejas (versionado, comparación de datasets)
   - Asistencia en la estructura y organización de los tests con pytest
   - Creación de fixtures y mocks para testing

**4. Configuración de Servicios de Terceros**
   - **Render**: Consultas sobre configuración de despliegue, variables de entorno y mejores prácticas
   - **SonarCloud**: Asistencia en la integración con GitHub Actions y configuración de análisis de calidad
   - **Swagger/OpenAPI**: Ayuda con la sintaxis de decoradores y estructura de documentación de API

**5. Resolución de Problemas Técnicos**
   - Consultas sobre errores específicos de configuración
   - Sugerencias de soluciones a problemas de integración entre componentes
   - Optimización de queries de base de datos

**Consideraciones Importantes:**
- Todo el código generado con ayuda de IA ha sido revisado, comprendido y adaptado manualmente
- El equipo es capaz de defender y explicar el funcionamiento de todo el código implementado
- Las decisiones de diseño fueron tomadas por el equipo, no por la IA

#### Lecciones Aprendidas

1. **Importancia del Tamaño del Equipo**
   - Trabajar con más miembros en el equipo hubiese sido clave para que la carga de trabajo fubiese sido más liviana para cada uno
   - La reducción del equipo de 6 a 2 personas incrementó significativamente la carga individual

2. **Sistema de Ramas Parecido a Git Flow**
   - Usar un sistema de ramas similar a Git Flow ha facilitado la organización del desarrollo
   - La separación entre `main` y `develop` ha permitido mantener una versión estable mientras se desarrollaban nuevas funcionalidades

3. **Tests Automáticos para Detección Temprana de Errores**
   - Tener unos tests automáticos nos ha ayudado a detectar errores antes de llevarlo a develop
   - Los tests han evitado que bugs llegaran a producción

4. **Pipeline de CI/CD para Calidad Continua**
   - El pipeline de CI/CD nos ha ayudado a detectar errores durante el proceso y poder corregirlos
   - La validación automática ha ahorrado tiempo al identificar problemas inmediatamente

5. **Importancia del Despliegue en Render**
   - La importancia de desplegar en Render para poder revisar el resultado del desarrollo
   - Ver la aplicación funcionando en un entorno real ha sido fundamental para validar cambios

6. **Releases para Versionado**
   - Sacar versiones de la aplicación con las releases para volver a versiones anteriores y detectar los cambios
   - El sistema de releases ha facilitado el seguimiento de la evolución del proyecto

### 8.2 Trabajo Futuro

Aunque nos han faltado pulir algunas de las funcionalidades del proyecto, nos gustaría trabajar en:

#### Funcionalidades de Alto Impacto

**1. Búsqueda Avanzada y Filtros**
- [ ] Filtros por rango de propiedades (temperatura, presión, valores)
- [ ] Búsqueda full-text en descripciones y metadatos
- [ ] Autocompletado de búsquedas
- **Dificultad:** Media-Alta
- **Impacto:** Alto para descubrimiento de datasets

**2. Visualización de Datos**
- [ ] Gráficas interactivas de propiedades (plotly/chart.js)
- [ ] Comparación visual entre datasets
- **Dificultad:** Media
- **Impacto:** Alto para análisis exploratorio

**3. Sistema de Colaboración**
- [ ] Comentarios y anotaciones en datasets
- [ ] Sistema de permisos granular (lectura/escritura/admin)
- [ ] Compartir datasets con usuarios específicos
- [ ] Equipos y organizaciones
- **Dificultad:** Alta
- **Impacto:** Alto para investigación colaborativa

#### Mejoras de UX/UI

**4. Interfaz de Usuario Moderna**
- [ ] Migrar frontend a React/Vue.js
- [ ] Diseño responsive mejorado
- [ ] Dark mode
- **Dificultad:** Alta
- **Impacto:** Alto para adopción

**10. Internacionalización**
- [ ] Soporte multi-idioma (i18n)
- [ ] Idiomas: Español, Inglés, Alemán, Chino
- [ ] Unidades de medida configurables
- **Dificultad:** Media
- **Impacto:** Alto para comunidad global

#### Investigación y Desarrollo

**11. Validación Automática de Datos**
- [ ] Reglas de validación configurables
- [ ] Detección de inconsistencias físicas
- [ ] Sugerencias de corrección automática
- **Dificultad:** Alta
- **Impacto:** Alto para calidad de datos

### 8.3 Consideraciones Finales

Desarrollar **Materials Hub** ha sido todo un reto, especialmente con un equipo tan reducido. Hemos conseguido crear una plataforma funcional que gestiona datasets de materiales de forma bastante completa, con funcionalidades que creemos que podrían ser útiles de verdad para investigadores de ciencia de materiales.

El proyecto ha sido una buena experiencia para aplicar todo lo que hemos aprendido sobre Git, testing, CI/CD y buenas prácticas de programación. Aunque nos ha costado bastante trabajo y ha habido momentos complicados (sobre todo cuando el equipo se redujo), estamos contentos con el resultado final.

Nos hubiese gustado tener más tiempo para pulir algunas cosas, como la documentación de Swagger o añadir más funcionalidades avanzadas, pero creo que hemos logrado un sistema sólido que funciona bien y que cumple con lo que nos propusimos al principio. El código está bastante ordenado y los tests ayudan a mantener todo funcionando correctamente.

De cara al futuro, hay muchas cosas interesantes que se podrían añadir al proyecto si alguien quisiera continuar con él, aunque somos conscientes de que algunas son bastante ambiciosas.
