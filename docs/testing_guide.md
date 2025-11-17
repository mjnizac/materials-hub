# 🧪 Guía de Testing - MaterialsDataset

## 📚 **Índice**

- [Visión General](#visión-general)
- [Requisitos](#requisitos)
- [Ejecutar Tests](#ejecutar-tests)
- [Estructura de Tests](#estructura-de-tests)
- [Cobertura de Tests](#cobertura-de-tests)
- [Escribir Nuevos Tests](#escribir-nuevos-tests)
- [Fixtures](#fixtures)
- [Troubleshooting](#troubleshooting)

---

## 🔍 **Visión General**

La suite de tests de MaterialsDataset incluye **48 tests unitarios** que cubren:

- ✅ **Modelos** - MaterialsDataset y MaterialRecord
- ✅ **Repositorios** - Queries y filtros de base de datos
- ✅ **Servicios** - Parser CSV y validación
- ✅ **API REST** - Todos los endpoints

**Framework usado:** pytest

---

## 📋 **Requisitos**

```bash
pip install pytest pytest-cov pytest-flask
```

**Dependencias del proyecto:**
- Flask
- SQLAlchemy
- pytest
- pytest-cov (opcional, para coverage)

---

## 🚀 **Ejecutar Tests**

### **Todos los Tests**

```bash
# Ejecutar todos los tests del módulo dataset
pytest app/modules/dataset/tests/test_unit.py -v

# Con output detallado
pytest app/modules/dataset/tests/test_unit.py -vv

# Con coverage
pytest app/modules/dataset/tests/test_unit.py --cov=app.modules.dataset --cov-report=html
```

### **Tests Específicos**

```bash
# Solo tests de modelos
pytest app/modules/dataset/tests/test_unit.py::TestMaterialsDatasetModel -v

# Solo tests de repositorios
pytest app/modules/dataset/tests/test_unit.py::TestMaterialRecordRepository -v

# Solo tests de servicios
pytest app/modules/dataset/tests/test_unit.py::TestMaterialsDatasetService -v

# Solo tests de API
pytest app/modules/dataset/tests/test_unit.py::TestMaterialsDatasetAPI -v

# Un test específico
pytest app/modules/dataset/tests/test_unit.py::TestMaterialsDatasetModel::test_create_materials_dataset -v
```

### **Tests con Filtros**

```bash
# Tests que contengan "upload" en el nombre
pytest app/modules/dataset/tests/test_unit.py -k upload -v

# Tests que contengan "validation"
pytest app/modules/dataset/tests/test_unit.py -k validat -v

# Tests que NO contengan "api"
pytest app/modules/dataset/tests/test_unit.py -k "not api" -v
```

---

## 📁 **Estructura de Tests**

```
app/modules/dataset/tests/test_unit.py
├── FIXTURES (líneas 10-78)
│   ├── test_user
│   ├── test_metadata
│   ├── test_materials_dataset
│   ├── test_material_record
│   └── sample_csv_content
│
├── MODEL TESTS (líneas 83-262)
│   ├── TestMaterialsDatasetModel (16 tests)
│   └── TestMaterialRecordModel (3 tests)
│
├── REPOSITORY TESTS (líneas 267-437)
│   ├── TestMaterialsDatasetRepository (2 tests)
│   └── TestMaterialRecordRepository (7 tests)
│
├── SERVICE TESTS (líneas 442-553)
│   └── TestMaterialsDatasetService (6 tests)
│
└── API TESTS (líneas 558-779)
    ├── TestMaterialsDatasetAPI (9 tests)
    └── TestMaterialRecordsAPI (4 tests)
```

**Total:** 48 tests

---

## 📊 **Cobertura de Tests**

### **Modelos (19 tests)**

| Clase | Tests | Cobertura |
|-------|-------|-----------|
| MaterialsDataset | 16 tests | 100% |
| MaterialRecord | 3 tests | 100% |

**Tests incluyen:**
- Creación de instancias
- Relaciones entre modelos
- Métodos de utilidad (get_materials_count, get_unique_materials, etc.)
- Validación (validate method)
- Serialización (to_dict)
- Enum DataSource

### **Repositorios (9 tests)**

| Repositorio | Tests | Métodos Cubiertos |
|-------------|-------|-------------------|
| MaterialsDatasetRepository | 2 tests | get_by_user, count_by_user |
| MaterialRecordRepository | 7 tests | get_by_dataset, get_by_material_name, get_by_property_name, search_materials, filter_by_temperature_range, count_by_dataset |

### **Servicios (6 tests)**

| Servicio | Tests | Funcionalidad |
|----------|-------|---------------|
| MaterialsDatasetService | 6 tests | Validación CSV, parsing, creación de records |

**Tests cubren:**
- Validación de columnas (válidas, faltantes, extras)
- Parsing exitoso de CSV
- Manejo de errores (archivo no encontrado, columnas inválidas)
- Creación de MaterialRecords desde CSV

### **API Endpoints (13 tests)**

| Endpoint | Tests | HTTP Methods |
|----------|-------|--------------|
| /api/v1/materials-datasets/ | 2 | GET, POST |
| /api/v1/materials-datasets/{id} | 3 | GET, DELETE |
| /api/v1/materials-datasets/{id}/statistics | 1 | GET |
| /api/v1/materials-datasets/{id}/upload | 3 | POST |
| /api/v1/materials-datasets/{dataset_id}/records | 2 | GET (+ paginación) |
| /api/v1/materials-datasets/{dataset_id}/records/search | 2 | GET |

---

## 🛠️ **Fixtures**

### **test_user**
```python
@pytest.fixture(scope='function')
def test_user(test_client):
    """Usuario de prueba: test@example.com"""
    return User.query.filter_by(email='test@example.com').first()
```

### **test_metadata**
```python
@pytest.fixture(scope='function')
def test_metadata(test_client):
    """Metadata de prueba para datasets"""
    return DSMetaData(title="Test Materials Dataset", ...)
```

### **test_materials_dataset**
```python
@pytest.fixture(scope='function')
def test_materials_dataset(test_client, test_user, test_metadata):
    """MaterialsDataset de prueba"""
    return MaterialsDataset(user_id=..., ds_meta_data_id=...)
```

### **test_material_record**
```python
@pytest.fixture(scope='function')
def test_material_record(test_client, test_materials_dataset):
    """MaterialRecord de prueba (Al2O3)"""
    return MaterialRecord(material_name='Al2O3', ...)
```

### **sample_csv_content**
```python
@pytest.fixture(scope='function')
def sample_csv_content():
    """CSV de ejemplo con 3 registros"""
    return """material_name,chemical_formula,...
Al2O3,Al2O3,...
SiO2,SiO2,...
TiO2,TiO2,..."""
```

---

## ✍️ **Escribir Nuevos Tests**

### **Ejemplo: Test de Modelo**

```python
def test_new_model_method(self, test_client, test_materials_dataset):
    """Test description"""
    # Arrange
    dataset = test_materials_dataset

    # Act
    result = dataset.new_method()

    # Assert
    assert result == expected_value
```

### **Ejemplo: Test de API**

```python
def test_new_endpoint(self, test_client, test_materials_dataset):
    """Test GET /api/v1/materials-datasets/{id}/new-endpoint"""
    # Act
    response = test_client.get(f'/api/v1/materials-datasets/{test_materials_dataset.id}/new-endpoint')

    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert 'expected_field' in data
```

### **Ejemplo: Test con CSV Temporal**

```python
def test_with_csv_file(self, test_client, test_materials_dataset):
    """Test with temporary CSV file"""
    csv_content = """material_name,property_name,property_value
Al2O3,density,3.95"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_path = f.name

    try:
        # Use temp_path for testing
        result = some_function(temp_path)
        assert result is True
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
```

---

## 📈 **Coverage Report**

Generar reporte de cobertura:

```bash
# Generar HTML report
pytest app/modules/dataset/tests/test_unit.py \
  --cov=app.modules.dataset \
  --cov-report=html

# Abrir reporte
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Objetivo de cobertura:** 80%+

---

## 🐛 **Troubleshooting**

### **Error: "No module named 'app'"**

```bash
# Asegúrate de estar en el directorio raíz
cd /home/manuel-jesus/materials-hub

# O ajusta PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/home/manuel-jesus/materials-hub"
```

### **Error: "Database not found"**

Los tests crean su propia base de datos en memoria. Si hay errores:

```python
# Verifica que el fixture test_client esté siendo usado
def test_something(self, test_client):  # ← test_client requerido
    ...
```

### **Error: "Fixture not found"**

Asegúrate de que el fixture esté importado:

```python
# En conftest.py o al inicio del archivo
@pytest.fixture(scope='function')
def my_fixture():
    ...
```

### **Tests Fallan con "IntegrityError"**

Problema de foreign keys. Solución:

```python
# Crear primero los objetos padre
user = test_user  # Fixture
metadata = test_metadata  # Fixture

# Luego el objeto hijo
dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
```

### **Tests Lentos**

```bash
# Ver los 10 tests más lentos
pytest app/modules/dataset/tests/test_unit.py --durations=10

# Ejecutar en paralelo (requiere pytest-xdist)
pip install pytest-xdist
pytest app/modules/dataset/tests/test_unit.py -n auto
```

---

## 📝 **Mejores Prácticas**

### **1. Nombres Descriptivos**
```python
# ✅ Bueno
def test_validate_csv_with_missing_required_columns()

# ❌ Malo
def test_csv_validation()
```

### **2. Arrange-Act-Assert**
```python
def test_something():
    # Arrange - Preparar datos
    dataset = create_dataset()

    # Act - Ejecutar función
    result = dataset.validate()

    # Assert - Verificar resultado
    assert result is True
```

### **3. Un Assert por Test (idealmente)**
```python
# ✅ Bueno - un concepto
def test_dataset_has_correct_id():
    assert dataset.id == 1

# ✅ También bueno - múltiples asserts relacionados
def test_dataset_serialization():
    data = dataset.to_dict()
    assert data['id'] == 1
    assert data['csv_file_path'] == '/path'
    assert 'materials_count' in data
```

### **4. Limpiar Recursos**
```python
# Usar try/finally para archivos temporales
try:
    result = test_with_file(temp_file)
finally:
    if os.path.exists(temp_file):
        os.remove(temp_file)
```

### **5. Fixtures con Scope Apropiado**
```python
# function - Se recrea para cada test (default)
@pytest.fixture(scope='function')

# module - Se crea una vez por archivo de test
@pytest.fixture(scope='module')

# session - Se crea una vez para toda la sesión
@pytest.fixture(scope='session')
```

---

## 🎯 **Checklist de Tests**

Antes de hacer commit, verifica:

- [ ] Todos los tests pasan (`pytest app/modules/dataset/tests/test_unit.py`)
- [ ] Cobertura >= 80% (`pytest --cov`)
- [ ] No hay warnings
- [ ] Tests son independientes (pueden correr en cualquier orden)
- [ ] Se limpian recursos temporales
- [ ] Nombres de tests son descriptivos
- [ ] Documentación actualizada

---

## 📞 **Recursos Adicionales**

- [Pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/latest/testing/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

**Versión:** 1.0
**Última actualización:** 2025-01-13
**Tests totales:** 48
**Cobertura objetivo:** 80%+
