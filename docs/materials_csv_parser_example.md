# MaterialsDataset CSV Parser - Ejemplo de Uso

## 📋 Estructura del CSV Esperada

### Columnas Requeridas (obligatorias)
- `material_name` - Nombre del material
- `property_name` - Nombre de la propiedad medida
- `property_value` - Valor de la propiedad

### Columnas Opcionales
- `chemical_formula` - Fórmula química
- `structure_type` - Tipo de estructura cristalina
- `composition_method` - Método de composición
- `property_unit` - Unidad de medida
- `temperature` - Temperatura (Integer)
- `pressure` - Presión (Integer)
- `data_source` - Fuente de datos (Enum: EXPERIMENTAL, COMPUTATIONAL, LITERATURE, DATABASE, OTHER)
- `uncertainty` - Incertidumbre (Integer)
- `description` - Descripción adicional

## 📝 Ejemplo de CSV

```csv
material_name,chemical_formula,structure_type,composition_method,property_name,property_value,property_unit,temperature,pressure,data_source,uncertainty,description
Al2O3,Al2O3,Corundum,Sol-gel,density,3.95,g/cm3,298,101325,EXPERIMENTAL,5,High purity alumina
SiO2,SiO2,Quartz,Hydrothermal,hardness,7,Mohs,,101325,LITERATURE,,From Mohs scale reference
TiO2,TiO2,Rutile,Chemical vapor deposition,refractive_index,2.61,,298,,COMPUTATIONAL,2,DFT calculation
ZrO2,ZrO2,Cubic,Precipitation,thermal_conductivity,2.5,W/mK,1273,101325,EXPERIMENTAL,10,At high temperature
```

## 🔧 Uso del Parser

### 1. Validar Columnas del CSV

```python
from app.modules.dataset.services import MaterialsDatasetService

service = MaterialsDatasetService()

# Leer el header del CSV y validar
csv_columns = ['material_name', 'property_name', 'property_value', 'temperature']
validation_result = service.validate_csv_columns(csv_columns)

print(validation_result)
# {
#     'valid': True,
#     'missing_required': [],
#     'extra_columns': [],
#     'message': 'CSV structure is valid'
# }
```

### 2. Parsear el CSV Completo

```python
from app.modules.dataset.services import MaterialsDatasetService

service = MaterialsDatasetService()

# Parsear el archivo CSV
csv_path = '/path/to/materials.csv'
parse_result = service.parse_csv_file(csv_path)

if parse_result['success']:
    print(f"✓ Parseadas {parse_result['rows_parsed']} filas")
    print(f"Datos: {parse_result['data']}")
else:
    print(f"✗ Error: {parse_result['error']}")
```

### 3. Crear MaterialRecords desde CSV

```python
from app import db
from app.modules.dataset.models import MaterialsDataset, DSMetaData
from app.modules.dataset.services import MaterialsDatasetService

# Crear el MaterialsDataset
metadata = DSMetaData(
    title="Ceramic Materials Properties",
    description="Database of ceramic material properties",
    publication_type=PublicationType.DATA_MANAGEMENT_PLAN
)
db.session.add(metadata)
db.session.commit()

materials_dataset = MaterialsDataset(
    user_id=current_user.id,
    ds_meta_data_id=metadata.id,
    csv_file_path='/uploads/materials.csv'
)
db.session.add(materials_dataset)
db.session.commit()

# Parsear CSV y crear registros
service = MaterialsDatasetService()
result = service.create_material_records_from_csv(
    materials_dataset,
    '/uploads/materials.csv'
)

if result['success']:
    print(f"✓ Creados {result['records_created']} registros de materiales")
else:
    print(f"✗ Error: {result['error']}")
```

### 4. Consultar MaterialRecords

```python
# Obtener todos los materiales únicos
unique_materials = materials_dataset.get_unique_materials()
print(f"Materiales: {unique_materials}")
# ['Al2O3', 'SiO2', 'TiO2', 'ZrO2']

# Obtener propiedades únicas medidas
unique_properties = materials_dataset.get_unique_properties()
print(f"Propiedades: {unique_properties}")
# ['density', 'hardness', 'refractive_index', 'thermal_conductivity']

# Contar registros
count = materials_dataset.get_materials_count()
print(f"Total de registros: {count}")
# 4

# Filtrar por material específico
al2o3_records = [r for r in materials_dataset.material_records if r.material_name == 'Al2O3']
print(f"Registros de Al2O3: {len(al2o3_records)}")
```

## ⚠️ Manejo de Errores

### CSV con columnas faltantes

```python
result = service.parse_csv_file('invalid.csv')
# {
#     'success': False,
#     'error': 'Missing required columns: material_name, property_value',
#     'data': [],
#     'rows_parsed': 0
# }
```

### Valores inválidos en filas

El parser maneja automáticamente:
- **Campos vacíos en columnas opcionales** → Se convierten a `None`
- **Temperatura/presión/uncertainty no numéricos** → Se loguea warning y se pone `None`
- **data_source inválido** → Se loguea warning y se pone `None`
- **Filas sin campos obligatorios** → Se salta la fila y se loguea warning

### Encoding incorrecto

```python
# Por defecto usa UTF-8, pero puedes especificar otro
result = service.parse_csv_file('materials.csv', encoding='latin-1')
```

## 🎯 Validación Automática

El modelo `MaterialsDataset` tiene validación integrada:

```python
try:
    materials_dataset.validate()
    print("✓ Dataset válido")
except ValueError as e:
    print(f"✗ Validación fallida: {str(e)}")
```

Verifica:
- Que exista `csv_file_path`
- Que haya al menos 1 `MaterialRecord`
- Que cada record tenga `material_name`, `property_name`, `property_value`

## 📊 Serialización a JSON

```python
dataset_dict = materials_dataset.to_dict()

# Incluye:
{
    "id": 123,
    "title": "Ceramic Materials Properties",
    "csv_file_path": "/uploads/materials.csv",
    "materials_count": 4,
    "unique_materials": ["Al2O3", "SiO2", "TiO2", "ZrO2"],
    "unique_properties": ["density", "hardness", "refractive_index", "thermal_conductivity"],
    "material_records": [
        {
            "id": 1,
            "material_name": "Al2O3",
            "chemical_formula": "Al2O3",
            "property_name": "density",
            "property_value": "3.95",
            "property_unit": "g/cm3",
            "temperature": 298,
            "pressure": 101325,
            "data_source": "experimental",
            ...
        },
        ...
    ],
    "dataset_type": "materials",
    ...
}
```
