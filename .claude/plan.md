# Plan: Eliminación de funcionalidad UVL del proyecto

## Análisis de la situación actual

### 1. Componentes UVL identificados

#### Modelos (`app/modules/dataset/models.py`)
- **UVLDataset** (línea 151-197): Clase que representa datasets de tipo UVL
  - Usa la tabla `data_set`
  - Tiene relación con `FeatureModel`
  - Alias: `DataSet = UVLDataset` (línea 332) para retrocompatibilidad

- **DSDownloadRecord** y **DSViewRecord**: Actualmente apuntan a `materials_dataset` (línea 338), NO a `data_set`

#### Módulos relacionados
- `app/modules/featuremodel/`: Módulo completo de feature models (UVL)
  - `models.py`: FeatureModel, FMMetaData
  - `services.py`: FeatureModelService
  - `repositories.py`: FeatureModelRepository
  - `forms.py`: Formularios para UVL

- `app/modules/hubfile/`: Módulo para archivos UVL (.uvl files)

#### Seeders (`app/modules/dataset/seeders.py`)
- **Líneas 73-138**: Crea 4 datasets UVL con archivos .uvl y FeatureModels
- **Líneas 140-1485**: Crea 20 MaterialsDatasets

#### Rutas
- **NO** se encontraron rutas activas para UVL en `/dataset` routes
- Todas las rutas activas usan MaterialsDataset

#### Repositorios y Servicios
- `DataSetRepository` (línea 69-175 de repositories.py): Usa `DataSet` (UVLDataset)
  - Modificado recientemente para incluir MaterialsDataset en counts
- `DataSetService` usa DataSetRepository

### 2. Estado del sistema

✅ **Lo que funciona:**
- Todos los tests de integración pasan (38/38)
- MaterialsDataset es la funcionalidad activa
- Las rutas web solo usan MaterialsDataset
- Los downloads/views apuntan solo a MaterialsDataset

⚠️ **Problema:**
- El código UVL existe pero no se usa en las rutas
- Los seeders crean datos UVL que no se usan
- Hay inconsistencia arquitectónica

## Pregunta crítica para el usuario

**¿Existe algún plan futuro para usar UVL datasets?**
- Si NO: Proceder con eliminación completa
- Si SÍ: Mantener el código pero desactivar seeders

## Plan de eliminación (si usuario confirma)

### Fase 1: Eliminar seeders UVL
1. Remover creación de DataSet/UVLDataset del seeder (líneas 73-138)
2. Remover imports de FeatureModel, FMMetaData del seeder
3. Dejar solo la creación de MaterialsDatasets

### Fase 2: Eliminar modelos UVL
1. Eliminar clase `UVLDataset` de `app/modules/dataset/models.py`
2. Eliminar alias `DataSet = UVLDataset`
3. **IMPORTANTE**: Esto romperá código que use `DataSet`

### Fase 3: Eliminar módulos completos
1. Eliminar `app/modules/featuremodel/` completo
2. Eliminar `app/modules/hubfile/` si solo se usa para UVL
3. Eliminar `app/modules/flamapy/` si existe y está relacionado

### Fase 4: Limpiar servicios y repositorios
1. `DataSetRepository`:
   - Eliminar referencias a DataSet/UVLDataset
   - Revertir cambios recientes en count methods
2. `DataSetService`:
   - Renombrar a `MaterialsDatasetService` o eliminar si duplica funcionalidad
3. `DataSetForm`:
   - Verificar si se debe eliminar o renombrar

### Fase 5: Migración de base de datos
1. Crear migración para:
   - Drop tabla `data_set` si existe
   - Drop tabla `feature_model` si existe
   - Drop tabla `fm_meta_data` si existe
   - Drop tabla `hubfile` si existe

### Fase 6: Limpieza de tests
1. Verificar que tests no usen UVLDataset
2. Actualizar imports si es necesario

### Fase 7: Documentación
1. Actualizar README
2. Actualizar diagramas UML
3. Actualizar guías de migración

## Riesgos

### Alto riesgo:
- **Datos en producción**: Si hay datos UVL en producción, se perderán
- **Código dependiente**: Cualquier código externo que use DataSet romperá

### Medio riesgo:
- **Tests**: Pueden fallar si hay tests unit que usen UVL
- **API**: Si hay endpoints API documentados externamente

### Bajo riesgo:
- Seeders: Fácil de modificar
- Rutas: Ya no hay rutas activas UVL

## Alternativa: Desactivación sin eliminación

Si hay incertidumbre, propongo:
1. **Mantener el código** UVL pero comentado/desactivado
2. **Eliminar del seeder** la creación de datos UVL
3. **Documentar** que UVL está "deprecated" pero disponible
4. **Plan futuro**: Eliminar en versión mayor (v2.0)

## Recomendación

Necesito que el usuario confirme:
1. **¿Hay datos UVL en producción actualmente?**
2. **¿Hay algún plan futuro para usar UVL?**
3. **¿Prefieres eliminación completa o desactivación?**

Una vez confirmado, puedo proceder con el plan apropiado.
