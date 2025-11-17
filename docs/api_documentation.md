# API REST Documentation - MaterialsDataset

## 📚 **Índice**

- [Visión General](#visión-general)
- [Autenticación](#autenticación)
- [Endpoints Disponibles](#endpoints-disponibles)
- [MaterialsDataset CRUD](#materialsdataset-crud)
- [Upload y Parsing de CSV](#upload-y-parsing-de-csv)
- [Consulta de Registros](#consulta-de-registros)
- [Búsqueda y Filtros](#búsqueda-y-filtros)
- [Estadísticas](#estadísticas)
- [Códigos de Respuesta](#códigos-de-respuesta)
- [Ejemplos de Uso](#ejemplos-de-uso)

---

## 🔍 **Visión General**

La API REST de MaterialsDataset proporciona endpoints para:
- Gestionar datasets de materiales (CRUD)
- Subir y parsear archivos CSV
- Consultar registros de materiales
- Buscar materiales por nombre o fórmula
- Obtener estadísticas de datasets

**Base URL:** `http://localhost:5000/api/v1`

---

## 🔐 **Autenticación**

La mayoría de endpoints requieren autenticación. Usa Flask-Login para autenticar las requests.

```bash
# Login (obtener cookie de sesión)
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  -c cookies.txt

# Usar la cookie en requests subsiguientes
curl http://localhost:5000/api/v1/materials-datasets/ \
  -b cookies.txt
```

---

## 📋 **Endpoints Disponibles**

### **MaterialsDataset CRUD**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/materials-datasets/` | Listar todos los materials datasets |
| GET | `/api/v1/materials-datasets/{id}` | Obtener un dataset específico |
| POST | `/api/v1/materials-datasets/` | Crear nuevo dataset |
| PUT | `/api/v1/materials-datasets/{id}` | Actualizar dataset |
| DELETE | `/api/v1/materials-datasets/{id}` | Eliminar dataset |

### **Operaciones Especiales**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/materials-datasets/{id}/upload` | Subir y parsear CSV |
| GET | `/api/v1/materials-datasets/{id}/statistics` | Obtener estadísticas |

### **MaterialRecords**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/materials-datasets/{dataset_id}/records` | Listar registros con paginación |
| GET | `/api/v1/materials-datasets/{dataset_id}/records/search` | Buscar registros |

---

## 🗂️ **MaterialsDataset CRUD**

### **1. Listar Datasets**

```bash
GET /api/v1/materials-datasets/
```

**Respuesta:**
```json
{
  "items": [
    {
      "id": 1,
      "created_at": "2025-01-13T10:00:00",
      "csv_file_path": "/uploads/ceramics.csv",
      "materials_count": 150,
      "unique_materials": ["Al2O3", "SiO2", "TiO2"],
      "unique_properties": ["density", "hardness", "melting_point"]
    }
  ]
}
```

**Ejemplo con curl:**
```bash
curl -X GET http://localhost:5000/api/v1/materials-datasets/ \
  -H "Accept: application/json"
```

**Ejemplo con Python:**
```python
import requests

response = requests.get('http://localhost:5000/api/v1/materials-datasets/')
datasets = response.json()['items']
print(f"Total datasets: {len(datasets)}")
```

---

### **2. Obtener Dataset Específico**

```bash
GET /api/v1/materials-datasets/{id}
```

**Parámetros de URL:**
- `id` (integer, requerido) - ID del dataset

**Respuesta:**
```json
{
  "id": 1,
  "created_at": "2025-01-13T10:00:00",
  "csv_file_path": "/uploads/ceramics.csv",
  "materials_count": 150,
  "unique_materials": ["Al2O3", "SiO2", "TiO2", "ZrO2"],
  "unique_properties": ["density", "hardness", "melting_point"]
}
```

**Ejemplo con curl:**
```bash
curl -X GET http://localhost:5000/api/v1/materials-datasets/1
```

**Ejemplo con Python:**
```python
import requests

response = requests.get('http://localhost:5000/api/v1/materials-datasets/1')
dataset = response.json()
print(f"Dataset: {dataset['csv_file_path']}")
print(f"Total materials: {dataset['materials_count']}")
```

---

### **3. Crear Nuevo Dataset**

```bash
POST /api/v1/materials-datasets/
```

**Body (JSON):**
```json
{
  "user_id": 1,
  "ds_meta_data_id": 10,
  "csv_file_path": "/uploads/new_materials.csv"
}
```

**Respuesta:**
```json
{
  "message": "MaterialsDataset created successfully",
  "id": 2
}
```

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:5000/api/v1/materials-datasets/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "ds_meta_data_id": 10,
    "csv_file_path": "/uploads/new_materials.csv"
  }'
```

**Ejemplo con Python:**
```python
import requests

data = {
    "user_id": 1,
    "ds_meta_data_id": 10,
    "csv_file_path": "/uploads/new_materials.csv"
}

response = requests.post(
    'http://localhost:5000/api/v1/materials-datasets/',
    json=data
)
new_dataset = response.json()
print(f"Created dataset ID: {new_dataset['id']}")
```

---

### **4. Eliminar Dataset**

```bash
DELETE /api/v1/materials-datasets/{id}
```

**Parámetros de URL:**
- `id` (integer, requerido) - ID del dataset

**Respuesta:**
```json
{
  "message": "MaterialsDataset deleted successfully"
}
```

**Ejemplo con curl:**
```bash
curl -X DELETE http://localhost:5000/api/v1/materials-datasets/1
```

**Ejemplo con Python:**
```python
import requests

response = requests.delete('http://localhost:5000/api/v1/materials-datasets/1')
print(response.json()['message'])
```

---

## 📤 **Upload y Parsing de CSV**

### **Subir CSV a Dataset**

```bash
POST /api/v1/materials-datasets/{id}/upload
```

**Parámetros de URL:**
- `id` (integer, requerido) - ID del MaterialsDataset

**Body (Multipart Form):**
- `file` (file, requerido) - Archivo CSV

**Respuesta (éxito):**
```json
{
  "message": "CSV uploaded and parsed successfully",
  "records_created": 150,
  "dataset_id": 1
}
```

**Respuesta (error):**
```json
{
  "message": "CSV parsing failed",
  "error": "Missing required columns: material_name, property_value"
}
```

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:5000/api/v1/materials-datasets/1/upload \
  -F "file=@/path/to/materials.csv"
```

**Ejemplo con Python:**
```python
import requests

files = {'file': open('materials.csv', 'rb')}
response = requests.post(
    'http://localhost:5000/api/v1/materials-datasets/1/upload',
    files=files
)

result = response.json()
if response.status_code == 200:
    print(f"✓ {result['records_created']} registros creados")
else:
    print(f"✗ Error: {result['error']}")
```

**Validaciones realizadas:**
- ✅ Archivo debe ser CSV
- ✅ Columnas requeridas: `material_name`, `property_name`, `property_value`
- ✅ Tipos de datos correctos (Integer, Enum, String)
- ✅ Valores no vacíos en campos obligatorios

---

## 📊 **Consulta de Registros**

### **Listar Registros con Paginación**

```bash
GET /api/v1/materials-datasets/{dataset_id}/records
```

**Parámetros de URL:**
- `dataset_id` (integer, requerido) - ID del dataset

**Query Parameters:**
- `page` (integer, opcional, default=1) - Número de página
- `per_page` (integer, opcional, default=100) - Registros por página

**Respuesta:**
```json
{
  "records": [
    {
      "id": 1,
      "material_name": "Al2O3",
      "chemical_formula": "Al2O3",
      "structure_type": "Corundum",
      "composition_method": "Sol-gel",
      "property_name": "density",
      "property_value": "3.95",
      "property_unit": "g/cm3",
      "temperature": 298,
      "pressure": 101325,
      "data_source": "experimental",
      "uncertainty": 5,
      "description": "High purity alumina"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 100,
  "total_pages": 2
}
```

**Ejemplo con curl:**
```bash
# Primera página (100 registros)
curl "http://localhost:5000/api/v1/materials-datasets/1/records?page=1&per_page=100"

# Segunda página
curl "http://localhost:5000/api/v1/materials-datasets/1/records?page=2&per_page=100"
```

**Ejemplo con Python:**
```python
import requests

# Obtener todos los registros paginados
def get_all_records(dataset_id, per_page=100):
    page = 1
    all_records = []

    while True:
        response = requests.get(
            f'http://localhost:5000/api/v1/materials-datasets/{dataset_id}/records',
            params={'page': page, 'per_page': per_page}
        )
        data = response.json()
        all_records.extend(data['records'])

        if page >= data['total_pages']:
            break
        page += 1

    return all_records

records = get_all_records(dataset_id=1)
print(f"Total registros obtenidos: {len(records)}")
```

---

## 🔍 **Búsqueda y Filtros**

### **Buscar Materiales**

```bash
GET /api/v1/materials-datasets/{dataset_id}/records/search?q={search_term}
```

**Parámetros de URL:**
- `dataset_id` (integer, requerido) - ID del dataset

**Query Parameters:**
- `q` (string, requerido) - Término de búsqueda

**Búsqueda en:**
- `material_name` (nombre del material)
- `chemical_formula` (fórmula química)

**Respuesta:**
```json
{
  "records": [
    {
      "id": 1,
      "material_name": "Al2O3",
      "chemical_formula": "Al2O3",
      "property_name": "density",
      "property_value": "3.95",
      ...
    },
    {
      "id": 2,
      "material_name": "Al2O3",
      "chemical_formula": "Al2O3",
      "property_name": "hardness",
      "property_value": "9",
      ...
    }
  ],
  "total": 2,
  "search_term": "Al2O3"
}
```

**Ejemplo con curl:**
```bash
# Buscar por nombre de material
curl "http://localhost:5000/api/v1/materials-datasets/1/records/search?q=Al2O3"

# Buscar por fórmula química
curl "http://localhost:5000/api/v1/materials-datasets/1/records/search?q=TiO2"

# Búsqueda parcial
curl "http://localhost:5000/api/v1/materials-datasets/1/records/search?q=alumin"
```

**Ejemplo con Python:**
```python
import requests

def search_materials(dataset_id, search_term):
    response = requests.get(
        f'http://localhost:5000/api/v1/materials-datasets/{dataset_id}/records/search',
        params={'q': search_term}
    )
    return response.json()

# Buscar alumina
results = search_materials(dataset_id=1, search_term='Al2O3')
print(f"Encontrados {results['total']} registros para '{results['search_term']}'")

for record in results['records']:
    print(f"  - {record['property_name']}: {record['property_value']} {record['property_unit']}")
```

---

## 📈 **Estadísticas**

### **Obtener Estadísticas del Dataset**

```bash
GET /api/v1/materials-datasets/{id}/statistics
```

**Parámetros de URL:**
- `id` (integer, requerido) - ID del dataset

**Respuesta:**
```json
{
  "dataset_id": 1,
  "total_records": 150,
  "unique_materials": ["Al2O3", "SiO2", "TiO2", "ZrO2", "Y2O3"],
  "unique_properties": ["density", "hardness", "melting_point", "thermal_conductivity"],
  "materials_count": 5,
  "properties_count": 4,
  "csv_file_path": "/uploads/ceramics.csv"
}
```

**Ejemplo con curl:**
```bash
curl http://localhost:5000/api/v1/materials-datasets/1/statistics
```

**Ejemplo con Python:**
```python
import requests

response = requests.get('http://localhost:5000/api/v1/materials-datasets/1/statistics')
stats = response.json()

print(f"Dataset ID: {stats['dataset_id']}")
print(f"Total registros: {stats['total_records']}")
print(f"\nMateriales únicos ({stats['materials_count']}):")
for material in stats['unique_materials']:
    print(f"  - {material}")

print(f"\nPropiedades medidas ({stats['properties_count']}):")
for prop in stats['unique_properties']:
    print(f"  - {prop}")
```

---

## 🚦 **Códigos de Respuesta**

| Código | Significado | Descripción |
|--------|-------------|-------------|
| 200 | OK | Request exitoso |
| 201 | Created | Recurso creado exitosamente |
| 204 | No Content | Recurso eliminado exitosamente |
| 400 | Bad Request | Datos inválidos o faltantes |
| 404 | Not Found | Recurso no encontrado |
| 500 | Internal Server Error | Error del servidor |

---

## 💡 **Ejemplos de Uso Completo**

### **Flujo Completo: Crear Dataset y Subir CSV**

**Python:**
```python
import requests

BASE_URL = 'http://localhost:5000/api/v1'

# 1. Crear MaterialsDataset
dataset_data = {
    "user_id": 1,
    "ds_meta_data_id": 10,
    "csv_file_path": ""  # Se actualizará al subir el CSV
}

response = requests.post(f'{BASE_URL}/materials-datasets/', json=dataset_data)
dataset_id = response.json()['id']
print(f"✓ Dataset creado: ID {dataset_id}")

# 2. Subir y parsear CSV
files = {'file': open('materials.csv', 'rb')}
response = requests.post(
    f'{BASE_URL}/materials-datasets/{dataset_id}/upload',
    files=files
)
result = response.json()
print(f"✓ CSV parseado: {result['records_created']} registros creados")

# 3. Obtener estadísticas
response = requests.get(f'{BASE_URL}/materials-datasets/{dataset_id}/statistics')
stats = response.json()
print(f"✓ Materiales únicos: {stats['materials_count']}")
print(f"✓ Propiedades medidas: {stats['properties_count']}")

# 4. Buscar material específico
response = requests.get(
    f'{BASE_URL}/materials-datasets/{dataset_id}/records/search',
    params={'q': 'Al2O3'}
)
results = response.json()
print(f"✓ Encontrados {results['total']} registros de Al2O3")
```

---

### **Filtrar Registros por Propiedad**

**Python:**
```python
import requests

# Obtener todos los registros
response = requests.get('http://localhost:5000/api/v1/materials-datasets/1/records')
all_records = response.json()['records']

# Filtrar por propiedad (density)
density_records = [r for r in all_records if r['property_name'] == 'density']

print(f"Registros de densidad: {len(density_records)}")
for record in density_records:
    print(f"{record['material_name']}: {record['property_value']} {record['property_unit']}")
```

---

### **Exportar Datos a CSV**

**Python:**
```python
import requests
import csv

# Obtener registros
response = requests.get('http://localhost:5000/api/v1/materials-datasets/1/records?per_page=1000')
records = response.json()['records']

# Exportar a CSV
with open('export.csv', 'w', newline='') as csvfile:
    if records:
        writer = csv.DictWriter(csvfile, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

print(f"✓ Exportados {len(records)} registros a export.csv")
```

---

## 🔗 **Enlaces Útiles**

- [Documentación de Modelos](materials_dataset_implementation_summary.md)
- [Guía de Parsing CSV](materials_csv_parser_example.md)
- [Migración de Base de Datos](migration_guide.md)
- [Tests Automatizados](test_csv_parser.py)

---

**Versión:** 1.0
**Última actualización:** 2025-01-13
