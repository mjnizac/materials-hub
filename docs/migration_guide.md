# Guía de Migración de Base de Datos - MaterialsDataset

## 📚 Resumen de Cambios

Se han creado dos nuevas tablas para soportar datasets de materiales:

1. **`materials_dataset`** - Tabla principal para datasets de materiales
2. **`material_record`** - Registros individuales de materiales (filas del CSV)
3. **`uvl_dataset`** - Nueva tabla separada para datasets UVL (migración futura)

## 🔧 Requisitos Previos

Asegúrate de tener instaladas las dependencias necesarias:

```bash
pip install python-dotenv flask-migrate alembic
```

## 📝 Archivos de Migración

### Migración 002: Add Materials Dataset

**Archivo:** `migrations/versions/002_add_materials_dataset.py`

**Cambios:**
- Crea tabla `materials_dataset`
- Crea tabla `material_record` con foreign key a `materials_dataset`
- Crea tabla `uvl_dataset` (para futura migración de datos)
- Crea enum `DataSource` con valores: EXPERIMENTAL, COMPUTATIONAL, LITERATURE, DATABASE, OTHER

## 🚀 Ejecutar la Migración

### 1. Verificar estado actual de la base de datos

```bash
flask db current
```

Deberías ver:
```
001 (head)
```

### 2. Ejecutar la migración (Upgrade)

```bash
flask db upgrade
```

Esto ejecutará la migración 002 y creará las nuevas tablas.

### 3. Verificar que la migración se aplicó correctamente

```bash
flask db current
```

Deberías ver:
```
002 (head)
```

### 4. Verificar las tablas creadas

```bash
# Si usas SQLite
sqlite3 instance/materials_hub.db ".tables"

# Si usas PostgreSQL
psql -d materials_hub -c "\dt"
```

Deberías ver las nuevas tablas:
- `materials_dataset`
- `material_record`
- `uvl_dataset`

## 🔄 Revertir la Migración (Downgrade)

Si necesitas revertir los cambios:

```bash
flask db downgrade
```

Esto eliminará las tablas creadas y volverá a la revisión 001.

**⚠️ ADVERTENCIA:** El downgrade eliminará TODOS los datos de materials_dataset y material_record.

## 📊 Estructura de las Tablas Creadas

### Tabla: `materials_dataset`

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| id | Integer | PRIMARY KEY | ID único |
| user_id | Integer | NOT NULL, FK(user.id) | Usuario propietario |
| ds_meta_data_id | Integer | NOT NULL, FK(ds_meta_data.id) | Metadatos del dataset |
| created_at | DateTime | NOT NULL | Fecha de creación |
| csv_file_path | String(512) | | Ruta al archivo CSV |

### Tabla: `material_record`

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| id | Integer | PRIMARY KEY | ID único |
| materials_dataset_id | Integer | NOT NULL, FK(materials_dataset.id) | Dataset padre |
| material_name | String(256) | NOT NULL | Nombre del material |
| chemical_formula | String(256) | | Fórmula química |
| structure_type | String(256) | | Tipo de estructura |
| composition_method | String(256) | | Método de composición |
| property_name | String(256) | NOT NULL | Nombre de la propiedad |
| property_value | String(256) | NOT NULL | Valor de la propiedad |
| property_unit | String(128) | | Unidad de medida |
| temperature | Integer | | Temperatura (K) |
| pressure | Integer | | Presión (Pa) |
| data_source | Enum(DataSource) | | Fuente de los datos |
| uncertainty | Integer | | Incertidumbre |
| description | Text | | Descripción adicional |

### Enum: `DataSource`

Valores posibles:
- `EXPERIMENTAL` - Datos de experimentos
- `COMPUTATIONAL` - Cálculos computacionales (DFT, MD, etc.)
- `LITERATURE` - Datos de literatura científica
- `DATABASE` - Datos de bases de datos existentes
- `OTHER` - Otra fuente

## 🧪 Probar las Tablas Creadas

### Usando Flask Shell

```python
flask shell

from app import db
from app.modules.dataset.models import MaterialsDataset, MaterialRecord, DataSource, DSMetaData, PublicationType
from app.modules.auth.models import User

# Obtener un usuario de prueba
user = User.query.first()

# Crear metadata para el dataset
metadata = DSMetaData(
    title="Test Materials Dataset",
    description="Dataset de prueba para materiales cerámicos",
    publication_type=PublicationType.OTHER
)
db.session.add(metadata)
db.session.commit()

# Crear un MaterialsDataset
materials_ds = MaterialsDataset(
    user_id=user.id,
    ds_meta_data_id=metadata.id,
    csv_file_path="/uploads/test_materials.csv"
)
db.session.add(materials_ds)
db.session.commit()

# Crear un MaterialRecord
record = MaterialRecord(
    materials_dataset_id=materials_ds.id,
    material_name="Al2O3",
    chemical_formula="Al2O3",
    structure_type="Corundum",
    property_name="density",
    property_value="3.95",
    property_unit="g/cm3",
    temperature=298,
    pressure=101325,
    data_source=DataSource.EXPERIMENTAL
)
db.session.add(record)
db.session.commit()

# Verificar
print(f"MaterialsDataset creado: ID {materials_ds.id}")
print(f"MaterialRecord creado: ID {record.id}")
print(f"Material: {record.material_name}")
print(f"Propiedad: {record.property_name} = {record.property_value} {record.property_unit}")
```

## 📋 Checklist Post-Migración

- [ ] Migración ejecutada correctamente
- [ ] Tablas creadas verificadas
- [ ] Prueba de creación de MaterialsDataset exitosa
- [ ] Prueba de creación de MaterialRecord exitosa
- [ ] Relaciones (foreign keys) funcionando correctamente
- [ ] Enum DataSource funcionando
- [ ] Validación de modelos funciona (`dataset.validate()`)

## ⚠️ Problemas Comunes

### Error: "No module named 'dotenv'"

```bash
pip install python-dotenv
```

### Error: "No such command 'db'"

```bash
pip install flask-migrate
```

### Error: "Unknown revision 001"

La base de datos no tiene el esquema inicial. Ejecuta:

```bash
flask db stamp head  # Marca la base de datos como actualizada
flask db upgrade     # Aplica las migraciones pendientes
```

### Error con PostgreSQL: "type datasource already exists"

El enum ya existe. Edita la migración 002 y comenta la línea de creación del enum, o elimínalo manualmente:

```sql
DROP TYPE IF EXISTS datasource;
```

## 📞 Soporte

Si encuentras problemas durante la migración, revisa:

1. Los logs de Flask: `flask run --debug`
2. Los logs de la base de datos
3. El contenido de `migrations/versions/002_add_materials_dataset.py`
