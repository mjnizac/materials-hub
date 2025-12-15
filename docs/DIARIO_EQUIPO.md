# Diario del Equipo

## Materials Hub

**Grupo:** G1 (Jesús Moreno)
**Curso Escolar:** 2025/2026
**Asignatura:** Evolución y Gestión de la Configuración

---

## Miembros del grupo

1. **Niza Cobo, Manuel Jesús**
2. **Ruiz Vázquez, María**

---

## Resumen de Total de Reuniones Empleadas en el Equipo

- **Total de reuniones:** 9
- **Total de reuniones presenciales:** 5
- **Total de reuniones virtuales:** 4
- **Total de tiempo empleado en reuniones presenciales:** 8.5 horas
- **Total de tiempo empleado en reuniones virtuales:** 5 horas
- **Tiempo total de reuniones:** 13.5 horas

---

## Actas de Acuerdos de las Reuniones

### ACTA 2025-01

**Fecha:** 2025-09-20
**Hora:** 10:00 - 11:30 (1.5 horas)
**Tipo:** Presencial
**Lugar:** Sala de estudios de la ETSII

**Asistentes:**
- Juan Antonio González Lucena
- Manuel Jesús Niza
- María Ruiz Vázquez
- Manuel Triguero Espejo
- Alvaro Sevilla Cabrera
- Javier Ulecia Garcia

#### Acuerdos Tomados:

**Acuerdo 2025-01-01:** Se forma el equipo de 6 integrantes y se acuerda el nombre del proyecto como "syssoft-hub", un repositorio de documentación de proyectos de software siguiendo buenas prácticas de documentación técnica. Juan Antonio González Lucena asume el rol de coordinador del equipo.

**Acuerdo 2025-01-02:** Se establece que el proyecto será desarrollado con Python 3.12 y Flask como framework web, utilizando MariaDB como base de datos.

**Acuerdo 2025-01-03:** Se acuerda utilizar Git Flow como estrategia de branching con las ramas principales: `main` (producción), `develop` (desarrollo), y ramas `feature/`, `fix/`, `docs/` para cambios específicos.

**Acuerdo 2025-01-04:** Se establece la política de commits siguiendo Conventional Commits con los tipos: `feat`, `fix`, `docs`.

**Acuerdo 2025-01-05:** Se utilizará GitHub Projects para gestión de tareas con columnas: Backlog, In Progress, In Review, Done.

---

### ACTA 2025-02

**Fecha:** 2025-09-28
**Hora:** 16:00 - 17:30 (1.5 horas)
**Tipo:** Virtual (Discord)

**Asistentes:**
- Juan Antonio González Lucena
- Manuel Jesús Niza
- María Ruiz Vázquez
- Manuel Triguero Espejo
- Alvaro Sevilla Cabrera
- Javier Ulecia Garcia

#### Acuerdos Tomados:

**Acuerdo 2025-02-01:** Se decide implementar una arquitectura modular para el sistema de documentación.

**Acuerdo 2025-02-02:** Se creará un pipeline de CI/CD con GitHub Actions para automatizar tests básicos.

**Acuerdo 2025-02-03:** Se implementará un CLI personalizado llamado "Rosemary" usando Click para comandos de gestión.

**Acuerdo 2025-02-04:** Se implementarán pre-commit hooks para garantizar calidad de código: Black, isort, flake8.

---

### ACTA 2025-03

**Fecha:** 2025-10-12
**Hora:** 10:00 - 12:00 (2 horas)
**Tipo:** Presencial
**Lugar:** Sala de estudios de la ETSII

**Asistentes:**
- Juan Antonio González Lucena
- Manuel Jesús Niza
- María Ruiz Vázquez
- Manuel Triguero Espejo
- Alvaro Sevilla Cabrera
- Javier Ulecia Garcia

#### Acuerdos Tomados:

**Acuerdo 2025-03-01:** Se continúa con el desarrollo del sistema base para cumplir con M1 (21 de octubre).

**Acuerdo 2025-03-02:** Se establece una longitud máxima de línea de 120 caracteres para el código Python.

**Acuerdo 2025-03-03:** El workflow de tests básico se ejecutará en cada push y pull request, bloqueando el merge si los tests fallan.

**Acuerdo 2025-03-04:** Manuel Jesús limpiará el historial de commits para eliminar información sensible y reorganizar el historial del proyecto antes del M1.

**Acuerdo 2025-03-05:** Se acuerda realizar reuniones semanales, alternando entre presenciales y virtuales.

---

### ACTA 2025-04

**Fecha:** 2025-10-26
**Hora:** 10:00 - 12:00 (2 horas)
**Tipo:** Presencial
**Lugar:** Sala de estudios de la ETSII

**Asistentes:**
- Manuel Jesús Niza
- María Ruiz Vázquez
- Manuel Triguero Espejo

#### Acuerdos Tomados:

**Acuerdo 2025-04-01:** Tras completar el M1 (21 de octubre), Juan Antonio González Lucena, Alvaro Sevilla Cabrera y Javier Ulecia Garcia han aprobado la asignatura y se separan definitivamente del equipo. El equipo se reduce de 6 a 3 miembros. Manuel Jesús Niza asume oficialmente el rol de coordinador del proyecto.

**Acuerdo 2025-04-02:** Se decide cambiar completamente el enfoque del proyecto de "syssoft-hub" (repositorio de documentos de software) a "Materials Hub" (repositorio de datasets de propiedades de materiales científicos con principios de Open Science). Este cambio responde a una mejor alineación con los intereses del nuevo equipo reducido.

**Acuerdo 2025-04-03:** El nuevo proyecto "Materials Hub" será un repositorio de datasets de propiedades de materiales con versionado automático y asignación de DOIs persistentes vía Zenodo.

**Acuerdo 2025-04-04:** Se mantiene la estructura técnica ya establecida: Python 3.12, Flask, MariaDB, y las herramientas de CI/CD básicas ya configuradas.

**Acuerdo 2025-04-05:** El modelo de datos para materiales incluirá propiedades obligatorias (material_name, property_name, property_value) y opcionales (chemical_formula, temperature, pressure, uncertainty, etc.).

---

### ACTA 2025-05

**Fecha:** 2025-11-02
**Hora:** 16:00 - 17:30 (1.5 horas)
**Tipo:** Virtual (Discord)

**Asistentes:**
- Manuel Jesús Niza
- María Ruiz Vázquez
- Manuel Triguero Espejo

#### Acuerdos Tomados:

**Acuerdo 2025-05-01:** Se decide implementar un sistema completo de versionado de datasets con tracking automático de cambios para el M2.

**Acuerdo 2025-05-02:** Las versiones se generarán automáticamente cuando se modifiquen metadatos o records de un dataset.

**Acuerdo 2025-05-03:** Se implementará integración con Zenodo para asignación de DOIs persistentes a los datasets.

**Acuerdo 2025-05-04:** Se creará un módulo "Fakenodo" que simule la API de Zenodo para desarrollo local y testing.

**Acuerdo 2025-05-05:** Los datasets se almacenarán en formato CSV con validación automática de columnas al momento de la carga.

**Acuerdo 2025-05-06:** Se configurará Docker para contenedorización del proyecto y DockerHub para publicación de imágenes. María implementará el despliegue con Docker.

**Acuerdo 2025-05-07:** Se configurará Render.com como plataforma de hosting para despliegue en producción. Manuel Jesús implementará el despliegue con Render.

**Acuerdo 2025-05-08:** Se implementará Vagrant para crear entornos de desarrollo reproducibles. María se encargará de la configuración de Vagrant.

**Acuerdo 2025-05-09:** Se automatizarán las pruebas mediante workflows de CI con GitHub Actions. Manuel Jesús implementará la automatización de pruebas.

**Acuerdo 2025-05-10:** Se crearán tests unitarios, de integración, de carga y de interfaz para validar todas las funcionalidades del sistema. Ambos miembros participarán en la creación de tests.

---

### ACTA 2025-06

**Fecha:** 2025-11-09
**Hora:** 10:00 - 11:00 (1 hora)
**Tipo:** Presencial
**Lugar:** Sala de estudios de la ETSII

**Asistentes:**
- Manuel Jesús Niza
- María Ruiz Vázquez

#### Acuerdos Tomados:

**Acuerdo 2025-06-01:** Manuel Triguero Espejo abandona el grupo durante el desarrollo del M2. El equipo se reduce de 3 a 2 miembros. Manuel Jesús y María acuerdan continuar el proyecto como equipo de 2 personas, redistribuyendo todas las responsabilidades.

**Acuerdo 2025-06-02:** Manuel Jesús asumirá también las tareas de desarrollo de API REST que hacía Manuel Triguero.

**Acuerdo 2025-06-03:** María asumirá también tareas de testing y documentación técnica.

**Acuerdo 2025-06-04:** Se prioriza la funcionalidad core del sistema para completar M2: CRUD de datasets, versionado, y API REST básica.

---

### ACTA 2025-07

**Fecha:** 2025-11-23
**Hora:** 16:00 - 17:30 (1.5 horas)
**Tipo:** Virtual (Discord)

**Asistentes:**
- Manuel Jesús Niza
- María Ruiz Vázquez

#### Acuerdos Tomados:

**Acuerdo 2025-07-01:** Se decide implementar un sistema robusto de validación de CSV con mensajes de error descriptivos.

**Acuerdo 2025-07-02:** El parser de CSV normalizará automáticamente valores numéricos.

**Acuerdo 2025-07-03:** Se validará que los valores de `data_source` sean uno de: EXPERIMENTAL, COMPUTATIONAL, LITERATURE, DATABASE, OTHER.

**Acuerdo 2025-07-04:** Se implementará funcionalidad para calcular y mostrar diferencias entre versiones de datasets. Manuel Jesús desarrollará un algoritmo híbrido de matching: matching por ID cuando esté disponible, y matching por contenido como fallback.

**Acuerdo 2025-07-05:** Se implementarán los siguientes endpoints principales para la API REST:
- GET/POST `/api/v1/materials-datasets/` (CRUD)
- POST `/api/v1/materials-datasets/<id>/upload` (subida CSV)
- GET `/api/v1/materials-datasets/<id>/statistics` (estadísticas)
- GET `/api/v1/materials-datasets/<id>/records` (paginación)
- GET `/api/v1/materials-datasets/<id>/versions` (historial de versiones)

**Acuerdo 2025-07-06:** Se implementará un sistema de recomendaciones automáticas de datasets basado en similitud de contenido y metadatos. Manuel Jesús desarrollará el algoritmo de recomendaciones.

**Acuerdo 2025-07-07:** Se creará funcionalidad de "Trending datasets" para mostrar los datasets más populares o descargados. María implementará esta característica.

**Acuerdo 2025-07-08:** Se añadirán opciones de personalización de la aplicación para mejorar la experiencia de usuario. María trabajará en la personalización de la interfaz.

---

### ACTA 2025-08

**Fecha:** 2025-12-07
**Hora:** 10:00 - 11:30 (1.5 horas)
**Tipo:** Presencial
**Lugar:** Sala de estudios de la ETSII

**Asistentes:**
- Manuel Jesús Niza
- María Ruiz Vázquez

#### Acuerdos Tomados:

**Acuerdo 2025-08-01:** Para el M3 se decide crear tests tanto unitarios como de integración para alcanzar >=50% de cobertura. María se encargará de implementar pruebas funcionales y de interfaz por cada Work Item.

**Acuerdo 2025-08-02:** Se usará pytest con markers `@pytest.mark.unit` y `@pytest.mark.integration`.

**Acuerdo 2025-08-03:** Se decide migrar la base de datos de MariaDB a PostgreSQL para mejorar compatibilidad con Render.com y aprovechar características avanzadas de PostgreSQL para el M3.

**Acuerdo 2025-08-04:** Manuel Jesús implementará la funcionalidad de creación de nuevos datasets (Newdataset) con validación completa de datos.

**Acuerdo 2025-08-05:** Se configurarán pre-commit hooks adicionales para garantizar calidad de código antes de cada commit. Manuel Jesús implementará los pre-commits.

**Acuerdo 2025-08-06:** Manuel Jesús creará el workflow de validación de Conventional Commits para asegurar que todos los commits sigan el formato establecido.

**Acuerdo 2025-08-07:** Manuel Jesús creará el workflow de Lint para validación automática de estilo de código (Black, isort, flake8).

**Acuerdo 2025-08-08:** Manuel Jesús creará el workflow de SonarCloud para análisis continuo de calidad de código y detección de code smells.

**Acuerdo 2025-08-09:** Manuel Jesús creará el workflow de Swagger para generación automática de documentación de la API REST.

**Acuerdo 2025-08-10:** Manuel Jesús creará el workflow de despliegue automático en Render cuando se realicen cambios en la rama main.

**Acuerdo 2025-08-11:** María creará el workflow de creación de imagen Docker y despliegue automático en DockerHub.

**Acuerdo 2025-08-12:** Manuel Jesús creará el workflow de lanzamiento de aplicación (CD_release.yml) para gestionar releases automáticas.

**Acuerdo 2025-08-13:** María creará el workflow de autorelease para gestión automática de versiones y realizará limpieza de ramas.

**Acuerdo 2025-08-14:** Manuel Jesús creará el bot de auto-merge de develop a main para automatizar la integración continua.

**Acuerdo 2025-08-15:** Manuel Jesús creará workflows propios de CI/CD que combinen todos los checks de calidad (CI_all_passed, CI_run) para validación completa antes de merge.

**Acuerdo 2025-08-16:** María revisará el despliegue Docker para asegurar compatibilidad y documentará el entorno de despliegue.

**Acuerdo 2025-08-17:** Se creará documentación completa en formato Markdown en la carpeta `docs/`.

---

### ACTA 2025-09

**Fecha:** 2025-12-13
**Hora:** 10:00 - 11:30 (1.5 horas)
**Tipo:** Presencial
**Lugar:** Sala de estudios de la ETSII

**Asistentes:**
- Manuel Jesús Niza
- María Ruiz Vázquez

#### Acuerdos Tomados:

**Acuerdo 2025-09-01:** Se decide completar la documentación final del proyecto para el M3 (entrega 18 de diciembre). María se encargará del documento del proyecto.

**Acuerdo 2025-09-02:** María creará el diario del equipo con todas las actas de reuniones reflejando la evolución del equipo: desde 6 miembros con "syssoft-hub" hasta 2 miembros con "Materials Hub".

**Acuerdo 2025-09-03:** Se realizará revisión final de código para asegurar que cumple con los estándares de calidad y se eliminará cualquier credencial de acceso del código.

**Acuerdo 2025-09-04:** Se verificará que todos los tests pasen y que la cobertura sea >=50%.

**Acuerdo 2025-09-05:** Se actualizará el README.md con instrucciones completas de instalación y uso.

**Acuerdo 2025-09-06:** Se dejará una versión final con un tag en la rama main que refleje el sistema funcionando en su completitud y listo para producción.

**Acuerdo 2025-09-07:** Manuel Jesús preparará un video demostración del proyecto para la evaluación final.

**Acuerdo 2025-09-08:** Se revisará el despliegue local y se empaquetará el proyecto según los requisitos del M3.
