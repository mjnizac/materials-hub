# 🧪 Guía de Testing - Materials Hub

## 📚 **Índice**

- [Visión General](#visión-general)
- [Requisitos](#requisitos)
- [Ejecutar Tests](#ejecutar-tests)
- [Estructura de Tests](#estructura-de-tests)
- [Cobertura de Tests](#cobertura-de-tests)
- [Tests por Módulo](#tests-por-módulo)
- [Fixtures Globales](#fixtures-globales)
- [Escribir Nuevos Tests](#escribir-nuevos-tests)
- [Tests de Carga (Locust)](#tests-de-carga-locust)
- [Troubleshooting](#troubleshooting)

---

## 🔍 **Visión General**

La suite de tests de Materials Hub incluye **87 tests** distribuidos por módulos:

- ✅ **67 Tests Unitarios** - Modelos, servicios, repositorios
- ✅ **20 Tests de Integración** - Rutas, API endpoints
- ✅ **Tests de Carga** - Locust para performance

**Framework usado:** pytest + pytest-cov

**Cobertura actual:** 40.38% (objetivo: 25%+)

---

## 📋 **Requisitos**

```bash
pip install pytest pytest-cov
```

**Dependencias incluidas en requirements.txt:**
- Flask + Flask-SQLAlchemy
- pytest (8.4.1)
- pytest-cov (6.2.1)
- Faker (para datos de prueba)

---

## 🚀 **Ejecutar Tests**

### **Todos los Tests**

```bash
# Ejecutar todos los tests (unit + integration)
pytest -v

# Con reporte de cobertura
pytest --cov=app --cov-report=html --cov-report=term

# Ejecutar en modo silencioso
pytest -q
```

### **Por Tipo de Test**

```bash
# Solo tests unitarios
pytest -m unit -v

# Solo tests de integración
pytest -m integration -v
```

### **Por Módulo Específico**

```bash
# Tests del módulo dataset
pytest app/modules/dataset/tests/ -v

# Tests del módulo auth
pytest app/modules/auth/tests/ -v

# Tests del módulo explore
pytest app/modules/explore/tests/ -v
```

### **Tests Específicos**

```bash
# Un archivo específico
pytest app/modules/dataset/tests/test_unit.py -v

# Una función específica
pytest app/modules/dataset/tests/test_unit.py::test_materials_dataset_name_method -v

# Tests que contengan "repository" en el nombre
pytest -k repository -v

# Tests que NO contengan "integration"
pytest -k "not integration" -v
```

### **Opciones Útiles**

```bash
# Ver los 10 tests más lentos
pytest --durations=10

# Detener en el primer fallo
pytest -x

# Mostrar variables locales en fallos
pytest -l

# Modo verbose con traceback corto
pytest -v --tb=short

# Ejecutar último fallo
pytest --lf

# Ejecutar tests fallidos primero
pytest --ff
```

---

## 📁 **Estructura de Tests**

Cada módulo tiene su propia carpeta `tests/` con esta estructura:

```
app/modules/{module}/
├── tests/
│   ├── test_unit.py          # Tests unitarios
│   ├── test_integration.py   # Tests de integración (opcional)
│   └── locustfile.py         # Tests de carga (opcional)
├── models.py
├── services.py
├── routes.py
└── repositories.py
```

### **Distribución de Tests por Módulo**

```
app/modules/
├── auth/tests/
│   ├── test_unit.py (9 tests unitarios)
│   └── locustfile.py
├── dataset/tests/
│   ├── test_unit.py (38 tests unitarios)
│   ├── test_integration.py (10 tests integración)
│   └── locustfile.py
├── explore/tests/
│   ├── test_integration.py (10 tests integración)
│   └── locustfile.py (opcional)
├── profile/tests/
│   └── test_unit.py (3 tests unitarios)
├── public/tests/
│   ├── test_unit.py (2 tests unitarios)
│   └── locustfile.py
├── team/tests/
│   └── test_unit.py (2 tests unitarios)
├── webhook/tests/
│   ├── test_unit.py (11 tests unitarios)
│   └── locustfile.py (opcional)
├── featuremodel/tests/
│   └── locustfile.py
├── flamapy/tests/
│   └── locustfile.py
└── hubfile/tests/
    └── locustfile.py
```

**Total:** 67 unitarios + 20 integración = **87 tests**

---

## 📊 **Cobertura de Tests**

### **Cobertura por Módulo**

| Módulo | Tests | Cobertura |
|--------|-------|-----------|
| auth | 9 unitarios | Modelos, servicios, autenticación |
| dataset | 38 unitarios + 10 integración | Repositorios, modelos, servicios, API |
| explore | 10 integración | Búsqueda, filtros, API |
| profile | 3 unitarios | Servicios, rutas |
| public | 2 unitarios | Homepage, repositorios |
| team | 2 unitarios | Página team |
| webhook | 11 unitarios | Servicios, modelos, Docker integration |

### **Cobertura Global**

```bash
# Generar reporte de cobertura
pytest --cov=app --cov-report=html --cov-report=term

# Abrir reporte HTML
# El archivo se genera en: htmlcov/index.html
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html      # macOS
```

**Cobertura actual:** 40.38%
**Cobertura requerida:** 25%+

---

## 🧩 **Tests por Módulo**

### **Auth Module (9 tests)**

Tests de autenticación y registro:
- Login exitoso/fallido
- Signup con validación
- Servicios de autenticación

```bash
pytest app/modules/auth/tests/ -v
```

### **Dataset Module (48 tests)**

**Unitarios (38):**
- Repositorios: MaterialsDatasetRepository, MaterialRecordRepository
- Modelos: MaterialsDataset validation, MaterialRecord.to_dict()
- Servicios: BaseService, SizeService, DOIMappingService

**Integración (10):**
- Rutas de descarga, DOI redirect
- API endpoints (list, get, recommendations)
- DSViewRecord cookies

```bash
# Solo unitarios
pytest app/modules/dataset/tests/test_unit.py -v

# Solo integración
pytest app/modules/dataset/tests/test_integration.py -v
```

### **Explore Module (10 tests)**

Tests de búsqueda y filtrado:
- Búsqueda por query, autor, afiliación
- Filtros por tipo de publicación y tags
- Ordenación (newest/oldest)
- API endpoint

```bash
pytest app/modules/explore/tests/ -v
```

### **Profile Module (3 tests)**

- Acceso a página de edición
- UserProfileService initialization
- Actualización de perfil

### **Webhook Module (11 tests)**

Tests de integración con Docker:
- Modelo, repositorio, servicio
- get_volume_name, execute_container_command
- Log deployment, restart container

```bash
pytest app/modules/webhook/tests/ -v
```

---

## 🛠️ **Fixtures Globales**

Definidas en `app/modules/conftest.py`:

### **test_app** (scope: session)
```python
@pytest.fixture(scope="session")
def test_app():
    """Crea app Flask para testing"""
    test_app = create_app("testing")
    with test_app.app_context():
        yield test_app
```

### **test_client** (scope: module)
```python
@pytest.fixture(scope="module")
def test_client(test_app):
    """
    Cliente de test con:
    - Base de datos limpia
    - Usuario de prueba: test@example.com / test1234
    - Profile de prueba: Test User
    """
    # Maneja foreign key constraints de MySQL
    # Crea/destruye tablas automáticamente
```

### **clean_database** (scope: function)
```python
@pytest.fixture(scope="function")
def clean_database():
    """Limpia la BD antes y después de cada test"""
```

### **Funciones de utilidad**

```python
# Login helper
login(test_client, email="test@example.com", password="test1234")

# Logout helper
logout(test_client)
```

---

## ✍️ **Escribir Nuevos Tests**

### **1. Test Unitario Básico**

```python
import pytest

@pytest.mark.unit
def test_model_creation(test_client):
    """Test creación de modelo"""
    from app.modules.dataset.models import MaterialsDataset
    from app import db

    dataset = MaterialsDataset(user_id=1, ds_meta_data_id=1)
    db.session.add(dataset)
    db.session.commit()

    assert dataset.id is not None
```

### **2. Test de Servicio**

```python
@pytest.mark.unit
def test_service_method(test_client):
    """Test método de servicio"""
    from app.modules.dataset.services import SizeService

    service = SizeService()
    result = service.get_human_readable_size(1024)

    assert result == "1.00 KB"
```

### **3. Test de Integración (API)**

```python
@pytest.mark.integration
def test_api_endpoint(test_client):
    """Test GET /api/v1/datasets"""
    from app.modules.conftest import login

    # Login primero
    login(test_client, "test@example.com", "test1234")

    # Request
    response = test_client.get("/api/v1/datasets")

    # Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
```

### **4. Test con Datos de Prueba**

```python
@pytest.mark.unit
def test_with_faker(test_client):
    """Test usando Faker para datos"""
    from faker import Faker
    from app.modules.auth.models import User
    from app import db

    fake = Faker()

    user = User(
        email=fake.email(),
        password=fake.password()
    )
    db.session.add(user)
    db.session.commit()

    assert user.id is not None
```

### **Mejores Prácticas**

1. **Usar markers**: `@pytest.mark.unit` o `@pytest.mark.integration`
2. **Nombres descriptivos**: `test_materials_dataset_validation_fails_without_csv`
3. **Arrange-Act-Assert**: Separar preparación, acción y verificación
4. **Un concepto por test**: Tests pequeños y focalizados
5. **Limpiar recursos**: Usar fixtures con cleanup automático

---

## 🔥 **Tests de Carga (Locust)**

### **Ejecutar Tests de Carga**

```bash
# Todos los tests de carga (desde raíz)
locust --host=http://localhost:5000

# Módulo específico
locust -f app/modules/dataset/tests/locustfile.py --host=http://localhost:5000

# Modo headless (sin UI)
locust --host=http://localhost:5000 --users 100 --spawn-rate 10 --run-time 1m --headless

# Con reporte HTML
locust --host=http://localhost:5000 --users 100 --spawn-rate 10 --run-time 2m --headless \
       --html reports/locust_report.html
```

**Interfaz web:** http://localhost:8089

### **Módulos con Tests de Carga**

- **auth**: Login, signup, authenticated users
- **dataset**: Upload, API, dataset viewing
- **public**: Homepage, public pages
- **hubfile**: File view/download
- **featuremodel**: Feature model endpoints
- **flamapy**: Flamapy validation endpoints

### **Locustfile Principal**

El archivo `locustfile.py` en la raíz agrega todos los tests de módulos:

```python
from app.modules.auth.tests.locustfile import AuthenticatedUser, AuthUser
from app.modules.dataset.tests.locustfile import DatasetUploader, APIUser
from app.modules.public.tests.locustfile import PublicUser
# ... etc
```

---

## 🐛 **Troubleshooting**

### **Error: Foreign Key Constraint**

```
IntegrityError: Cannot delete or update a parent row
```

**Solución:** Ya está solucionado en `conftest.py` con:
```python
db.session.execute(db.text("SET FOREIGN_KEY_CHECKS=0;"))
db.session.commit()
db.drop_all()
```

### **Error: No module named 'app'**

```bash
# Ejecutar desde el directorio raíz
cd /home/manuel-jesus/materials-hub
pytest -v

# O configurar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### **Error: test_client not found**

Asegúrate de importar el fixture:
```python
def test_something(test_client):  # ← fixture requerido
    pass
```

### **Tests Lentos**

```bash
# Ver tests más lentos
pytest --durations=10

# Ejecutar en paralelo (requiere pytest-xdist)
pip install pytest-xdist
pytest -n auto
```

### **Coverage Bajo**

```bash
# Ver qué falta cubrir
pytest --cov=app --cov-report=term-missing

# Ver por módulo
pytest --cov=app.modules.dataset --cov-report=term
```

---

## 📝 **Checklist antes de Commit**

- [ ] Todos los tests pasan: `pytest -v`
- [ ] Coverage >= 25%: `pytest --cov=app`
- [ ] No hay warnings
- [ ] Tests unitarios marcados con `@pytest.mark.unit`
- [ ] Tests integración marcados con `@pytest.mark.integration`
- [ ] Nombres de tests descriptivos
- [ ] Fixtures usados correctamente
- [ ] Documentación actualizada si es necesario

---

## 📞 **Recursos Adicionales**

- [Pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/latest/testing/)
- [Locust Documentation](https://docs.locust.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

## 📈 **Estadísticas**

**Versión:** 2.0
**Última actualización:** 2025-12-02
**Tests totales:** 87 (67 unit + 20 integration)
**Cobertura actual:** 40.38%
**Cobertura objetivo:** 25%+
**Tiempo ejecución:** ~1.5 minutos

---

**¿Necesitas ayuda?** Consulta esta guía o abre un issue en GitHub.
