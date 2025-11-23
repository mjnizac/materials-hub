import pytest
import os
import tempfile
from datetime import datetime

from app import db
from app.modules.dataset.models import (
    MaterialsDataset,
    MaterialRecord,
    DataSource,
    DSMetaData,
    PublicationType
)
from app.modules.dataset.services import MaterialsDatasetService
from app.modules.dataset.repositories import MaterialsDatasetRepository, MaterialRecordRepository
from app.modules.auth.models import User


# ========== FIXTURES ==========

@pytest.fixture(scope='function')
def test_user(test_client):
    """Create a test user"""
    user = User.query.filter_by(email='test@example.com').first()
    if not user:
        user = User(email='test@example.com', password='test1234')
        db.session.add(user)
        db.session.commit()
    return user


@pytest.fixture(scope='function')
def test_metadata(test_client):
    """Create test metadata for datasets"""
    metadata = DSMetaData(
        title="Test Materials Dataset",
        description="A test dataset for materials",
        publication_type=PublicationType.OTHER
    )
    db.session.add(metadata)
    db.session.commit()
    return metadata


@pytest.fixture(scope='function')
def test_materials_dataset(test_client, test_user, test_metadata):
    """Create a test MaterialsDataset"""
    dataset = MaterialsDataset(
        user_id=test_user.id,
        ds_meta_data_id=test_metadata.id,
        csv_file_path='/test/path.csv'
    )
    db.session.add(dataset)
    db.session.commit()
    return dataset


@pytest.fixture(scope='function')
def test_material_record(test_client, test_materials_dataset):
    """Create a test MaterialRecord"""
    record = MaterialRecord(
        materials_dataset_id=test_materials_dataset.id,
        material_name='Al2O3',
        chemical_formula='Al2O3',
        structure_type='Corundum',
        composition_method='Sol-gel',
        property_name='density',
        property_value='3.95',
        property_unit='g/cm3',
        temperature=298,
        pressure=101325,
        data_source=DataSource.EXPERIMENTAL,
        uncertainty=5,
        description='Test alumina material'
    )
    db.session.add(record)
    db.session.commit()
    return record


@pytest.fixture(scope='function')
def sample_csv_content():
    """Sample CSV content for testing"""
    return """material_name,chemical_formula,structure_type,composition_method,property_name,property_value,property_unit,temperature,pressure,data_source,uncertainty,description
Al2O3,Al2O3,Corundum,Sol-gel,density,3.95,g/cm3,298,101325,EXPERIMENTAL,5,High purity alumina
SiO2,SiO2,Quartz,Hydrothermal,hardness,7,Mohs,298,101325,LITERATURE,,From reference tables
TiO2,TiO2,Rutile,CVD,refractive_index,2.61,,298,,COMPUTATIONAL,2,DFT calculation"""


# ========== MODEL TESTS ==========

class TestMaterialsDatasetModel:
    """Tests for MaterialsDataset model"""

    def test_create_materials_dataset(self, test_client, test_user, test_metadata):
        """Test creating a MaterialsDataset"""
        dataset = MaterialsDataset(
            user_id=test_user.id,
            ds_meta_data_id=test_metadata.id,
            csv_file_path='/test/materials.csv'
        )
        db.session.add(dataset)
        db.session.commit()

        assert dataset.id is not None
        assert dataset.user_id == test_user.id
        assert dataset.csv_file_path == '/test/materials.csv'
        assert dataset.created_at is not None

    def test_materials_dataset_relationships(self, test_client, test_materials_dataset, test_material_record):
        """Test MaterialsDataset relationships"""
        assert test_materials_dataset.ds_meta_data is not None
        assert test_materials_dataset.ds_meta_data.title == "Test Materials Dataset"
        assert len(test_materials_dataset.material_records) == 1
        assert test_materials_dataset.material_records[0].material_name == 'Al2O3'

    def test_get_materials_count(self, test_client, test_materials_dataset):
        """Test get_materials_count method"""
        # Initially empty
        assert test_materials_dataset.get_materials_count() == 0

        # Add records
        record1 = MaterialRecord(
            materials_dataset_id=test_materials_dataset.id,
            material_name='Al2O3',
            property_name='density',
            property_value='3.95'
        )
        record2 = MaterialRecord(
            materials_dataset_id=test_materials_dataset.id,
            material_name='SiO2',
            property_name='hardness',
            property_value='7'
        )
        db.session.add_all([record1, record2])
        db.session.commit()

        assert test_materials_dataset.get_materials_count() == 2

    def test_get_unique_materials(self, test_client, test_materials_dataset):
        """Test get_unique_materials method"""
        # Add multiple records with different materials
        materials = ['Al2O3', 'Al2O3', 'SiO2', 'TiO2']
        for mat in materials:
            record = MaterialRecord(
                materials_dataset_id=test_materials_dataset.id,
                material_name=mat,
                property_name='density',
                property_value='1.0'
            )
            db.session.add(record)
        db.session.commit()

        unique_materials = test_materials_dataset.get_unique_materials()
        assert len(unique_materials) == 3
        assert set(unique_materials) == {'Al2O3', 'SiO2', 'TiO2'}

    def test_get_unique_properties(self, test_client, test_materials_dataset):
        """Test get_unique_properties method"""
        # Add multiple records with different properties
        properties = ['density', 'hardness', 'density', 'melting_point']
        for prop in properties:
            record = MaterialRecord(
                materials_dataset_id=test_materials_dataset.id,
                material_name='Al2O3',
                property_name=prop,
                property_value='1.0'
            )
            db.session.add(record)
        db.session.commit()

        unique_properties = test_materials_dataset.get_unique_properties()
        assert len(unique_properties) == 3
        assert set(unique_properties) == {'density', 'hardness', 'melting_point'}

    def test_validate_success(self, test_client, test_materials_dataset, test_material_record):
        """Test validation passes with valid data"""
        result = test_materials_dataset.validate()
        assert result is True

    def test_validate_missing_csv_path(self, test_client, test_user, test_metadata):
        """Test validation fails without CSV path"""
        dataset = MaterialsDataset(
            user_id=test_user.id,
            ds_meta_data_id=test_metadata.id,
            csv_file_path=None
        )
        db.session.add(dataset)
        db.session.commit()

        # Add a record
        record = MaterialRecord(
            materials_dataset_id=dataset.id,
            material_name='Al2O3',
            property_name='density',
            property_value='3.95'
        )
        db.session.add(record)
        db.session.commit()

        with pytest.raises(ValueError, match="must have a CSV file path"):
            dataset.validate()

    def test_validate_no_records(self, test_client, test_materials_dataset):
        """Test validation fails without records"""
        with pytest.raises(ValueError, match="at least one material record"):
            test_materials_dataset.validate()

    def test_to_dict(self, test_client, test_materials_dataset, test_material_record):
        """Test to_dict serialization"""
        data = test_materials_dataset.to_dict()

        assert data['id'] == test_materials_dataset.id
        assert data['csv_file_path'] == '/test/path.csv'
        assert data['materials_count'] == 1
        assert data['dataset_type'] == 'materials'
        assert 'Al2O3' in data['unique_materials']
        assert 'density' in data['unique_properties']
        assert len(data['material_records']) == 1


class TestMaterialRecordModel:
    """Tests for MaterialRecord model"""

    def test_create_material_record(self, test_client, test_materials_dataset):
        """Test creating a MaterialRecord"""
        record = MaterialRecord(
            materials_dataset_id=test_materials_dataset.id,
            material_name='ZrO2',
            chemical_formula='ZrO2',
            property_name='thermal_conductivity',
            property_value='2.5',
            property_unit='W/mK',
            temperature=1273,
            data_source=DataSource.EXPERIMENTAL
        )
        db.session.add(record)
        db.session.commit()

        assert record.id is not None
        assert record.material_name == 'ZrO2'
        assert record.temperature == 1273
        assert record.data_source == DataSource.EXPERIMENTAL

    def test_material_record_to_dict(self, test_client, test_material_record):
        """Test MaterialRecord to_dict"""
        data = test_material_record.to_dict()

        assert data['id'] == test_material_record.id
        assert data['material_name'] == 'Al2O3'
        assert data['chemical_formula'] == 'Al2O3'
        assert data['property_name'] == 'density'
        assert data['property_value'] == '3.95'
        assert data['property_unit'] == 'g/cm3'
        assert data['temperature'] == 298
        assert data['pressure'] == 101325
        assert data['data_source'] == 'experimental'
        assert data['uncertainty'] == 5

    def test_data_source_enum(self, test_client, test_materials_dataset):
        """Test DataSource enum values"""
        sources = [
            DataSource.EXPERIMENTAL,
            DataSource.COMPUTATIONAL,
            DataSource.LITERATURE,
            DataSource.DATABASE,
            DataSource.OTHER
        ]

        for source in sources:
            record = MaterialRecord(
                materials_dataset_id=test_materials_dataset.id,
                material_name='Test',
                property_name='test_prop',
                property_value='1.0',
                data_source=source
            )
            db.session.add(record)
        db.session.commit()

        records = MaterialRecord.query.filter_by(materials_dataset_id=test_materials_dataset.id).all()
        assert len(records) == 5


# ========== REPOSITORY TESTS ==========

class TestMaterialsDatasetRepository:
    """Tests for MaterialsDatasetRepository"""

    def test_get_by_user(self, test_client, test_user, test_materials_dataset):
        """Test getting datasets by user"""
        repo = MaterialsDatasetRepository()
        datasets = repo.get_by_user(test_user.id)

        assert len(datasets) >= 1
        assert any(d.id == test_materials_dataset.id for d in datasets)

    def test_count_by_user(self, test_client, test_user, test_materials_dataset):
        """Test counting datasets by user"""
        repo = MaterialsDatasetRepository()
        count = repo.count_by_user(test_user.id)

        assert count >= 1


class TestMaterialRecordRepository:
    """Tests for MaterialRecordRepository"""

    def test_get_by_dataset(self, test_client, test_materials_dataset, test_material_record):
        """Test getting records by dataset"""
        repo = MaterialRecordRepository()
        records = repo.get_by_dataset(test_materials_dataset.id)

        assert len(records) == 1
        assert records[0].id == test_material_record.id

    def test_get_by_material_name(self, test_client, test_materials_dataset):
        """Test getting records by material name"""
        # Add multiple records
        materials = ['Al2O3', 'Al2O3', 'SiO2']
        for mat in materials:
            record = MaterialRecord(
                materials_dataset_id=test_materials_dataset.id,
                material_name=mat,
                property_name='density',
                property_value='1.0'
            )
            db.session.add(record)
        db.session.commit()

        repo = MaterialRecordRepository()
        al2o3_records = repo.get_by_material_name(test_materials_dataset.id, 'Al2O3')

        assert len(al2o3_records) == 2
        assert all(r.material_name == 'Al2O3' for r in al2o3_records)

    def test_get_by_property_name(self, test_client, test_materials_dataset):
        """Test getting records by property name"""
        properties = ['density', 'hardness', 'density']
        for prop in properties:
            record = MaterialRecord(
                materials_dataset_id=test_materials_dataset.id,
                material_name='Al2O3',
                property_name=prop,
                property_value='1.0'
            )
            db.session.add(record)
        db.session.commit()

        repo = MaterialRecordRepository()
        density_records = repo.get_by_property_name(test_materials_dataset.id, 'density')

        assert len(density_records) == 2
        assert all(r.property_name == 'density' for r in density_records)

    def test_search_materials(self, test_client, test_materials_dataset):
        """Test searching materials"""
        # Add test records
        records_data = [
            ('Al2O3', 'Al2O3'),
            ('Alumina', 'Al2O3'),
            ('SiO2', 'SiO2')
        ]
        for name, formula in records_data:
            record = MaterialRecord(
                materials_dataset_id=test_materials_dataset.id,
                material_name=name,
                chemical_formula=formula,
                property_name='density',
                property_value='1.0'
            )
            db.session.add(record)
        db.session.commit()

        repo = MaterialRecordRepository()

        # Search by name
        results = repo.search_materials(test_materials_dataset.id, 'Al2O3')
        assert len(results) == 2

        # Search by partial match
        results = repo.search_materials(test_materials_dataset.id, 'Alum')
        assert len(results) == 1
        assert results[0].material_name == 'Alumina'

    def test_filter_by_temperature_range(self, test_client, test_materials_dataset):
        """Test filtering by temperature range"""
        temperatures = [298, 500, 1000, 1500]
        for temp in temperatures:
            record = MaterialRecord(
                materials_dataset_id=test_materials_dataset.id,
                material_name='Al2O3',
                property_name='density',
                property_value='1.0',
                temperature=temp
            )
            db.session.add(record)
        db.session.commit()

        repo = MaterialRecordRepository()

        # Test min and max
        results = repo.filter_by_temperature_range(test_materials_dataset.id, min_temp=500, max_temp=1000)
        assert len(results) == 2
        assert all(500 <= r.temperature <= 1000 for r in results)

        # Test only min
        results = repo.filter_by_temperature_range(test_materials_dataset.id, min_temp=1000)
        assert len(results) == 2

        # Test only max
        results = repo.filter_by_temperature_range(test_materials_dataset.id, max_temp=500)
        assert len(results) == 2

    def test_count_by_dataset(self, test_client, test_materials_dataset):
        """Test counting records by dataset"""
        # Add records
        for i in range(5):
            record = MaterialRecord(
                materials_dataset_id=test_materials_dataset.id,
                material_name=f'Material{i}',
                property_name='density',
                property_value='1.0'
            )
            db.session.add(record)
        db.session.commit()

        repo = MaterialRecordRepository()
        count = repo.count_by_dataset(test_materials_dataset.id)

        assert count == 5


# ========== SERVICE TESTS ==========

class TestMaterialsDatasetService:
    """Tests for MaterialsDatasetService - CSV Parser"""

    def test_validate_csv_columns_valid(self, test_client):
        """Test CSV column validation with valid columns"""
        service = MaterialsDatasetService()

        columns = ['material_name', 'property_name', 'property_value', 'temperature']
        result = service.validate_csv_columns(columns)

        assert result['valid'] is True
        assert len(result['missing_required']) == 0

    def test_validate_csv_columns_missing_required(self, test_client):
        """Test CSV column validation with missing required columns"""
        service = MaterialsDatasetService()

        columns = ['material_name', 'temperature']  # Missing property_name and property_value
        result = service.validate_csv_columns(columns)

        assert result['valid'] is False
        assert 'property_name' in result['missing_required']
        assert 'property_value' in result['missing_required']

    def test_validate_csv_columns_extra(self, test_client):
        """Test CSV column validation with extra columns"""
        service = MaterialsDatasetService()

        columns = ['material_name', 'property_name', 'property_value', 'unknown_field']
        result = service.validate_csv_columns(columns)

        assert result['valid'] is True
        assert 'unknown_field' in result['extra_columns']

    def test_parse_csv_file_success(self, test_client, sample_csv_content):
        """Test successful CSV parsing"""
        service = MaterialsDatasetService()

        # Create temp CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_content)
            temp_path = f.name

        try:
            result = service.parse_csv_file(temp_path)

            assert result['success'] is True
            assert result['rows_parsed'] == 3
            assert len(result['data']) == 3

            # Check first row
            first_row = result['data'][0]
            assert first_row['material_name'] == 'Al2O3'
            assert first_row['property_value'] == '3.95'
            assert first_row['temperature'] == 298
            assert first_row['data_source'] == DataSource.EXPERIMENTAL

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_parse_csv_file_not_found(self, test_client):
        """Test CSV parsing with non-existent file"""
        service = MaterialsDatasetService()

        result = service.parse_csv_file('/nonexistent/file.csv')

        assert result['success'] is False
        assert 'not found' in result['error']

    def test_parse_csv_file_invalid_columns(self, test_client):
        """Test CSV parsing with invalid columns"""
        service = MaterialsDatasetService()

        invalid_csv = """material_name,invalid_column
Al2O3,test"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(invalid_csv)
            temp_path = f.name

        try:
            result = service.parse_csv_file(temp_path)

            assert result['success'] is False
            assert 'Missing required columns' in result['error']

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_create_material_records_from_csv(self, test_client, test_materials_dataset, sample_csv_content):
        """Test creating MaterialRecords from CSV"""
        service = MaterialsDatasetService()

        # Create temp CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_content)
            temp_path = f.name

        try:
            result = service.create_material_records_from_csv(test_materials_dataset, temp_path)

            assert result['success'] is True
            assert result['records_created'] == 3

            # Verify records were created
            records = MaterialRecord.query.filter_by(materials_dataset_id=test_materials_dataset.id).all()
            assert len(records) == 3

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


# ========== API ENDPOINT TESTS ==========

class TestMaterialsDatasetAPI:
    """Tests for MaterialsDataset API endpoints"""

    def test_list_materials_datasets(self, test_client, test_materials_dataset):
        """Test GET /api/v1/materials-datasets/"""
        response = test_client.get('/api/v1/materials-datasets/')

        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert isinstance(data['items'], list)

    def test_get_materials_dataset(self, test_client, test_materials_dataset):
        """Test GET /api/v1/materials-datasets/{id}"""
        response = test_client.get(f'/api/v1/materials-datasets/{test_materials_dataset.id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == test_materials_dataset.id
        assert data['csv_file_path'] == '/test/path.csv'

    def test_get_materials_dataset_not_found(self, test_client):
        """Test GET /api/v1/materials-datasets/{id} with non-existent ID"""
        response = test_client.get('/api/v1/materials-datasets/99999')

        assert response.status_code == 404
        data = response.get_json()
        assert 'not found' in data['message'].lower()

    def test_create_materials_dataset(self, test_client, test_user, test_metadata):
        """Test POST /api/v1/materials-datasets/"""
        data = {
            'user_id': test_user.id,
            'ds_meta_data_id': test_metadata.id,
            'csv_file_path': '/new/path.csv'
        }

        response = test_client.post(
            '/api/v1/materials-datasets/',
            json=data,
            content_type='application/json'
        )

        assert response.status_code == 201
        response_data = response.get_json()
        assert 'id' in response_data
        assert response_data['message'] == 'MaterialsDataset created successfully'

    def test_delete_materials_dataset(self, test_client, test_materials_dataset):
        """Test DELETE /api/v1/materials-datasets/{id}"""
        dataset_id = test_materials_dataset.id

        response = test_client.delete(f'/api/v1/materials-datasets/{dataset_id}')

        assert response.status_code == 204

        # Verify deletion
        deleted_dataset = MaterialsDataset.query.get(dataset_id)
        assert deleted_dataset is None

    def test_get_statistics(self, test_client, test_materials_dataset, test_material_record):
        """Test GET /api/v1/materials-datasets/{id}/statistics"""
        response = test_client.get(f'/api/v1/materials-datasets/{test_materials_dataset.id}/statistics')

        assert response.status_code == 200
        data = response.get_json()
        assert data['dataset_id'] == test_materials_dataset.id
        assert data['total_records'] == 1
        assert data['materials_count'] == 1
        assert data['properties_count'] == 1
        assert 'Al2O3' in data['unique_materials']
        assert 'density' in data['unique_properties']

    def test_upload_csv(self, test_client, test_materials_dataset, sample_csv_content):
        """Test POST /api/v1/materials-datasets/{id}/upload"""
        # Create temp CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_content)
            temp_path = f.name

        try:
            with open(temp_path, 'rb') as csv_file:
                response = test_client.post(
                    f'/api/v1/materials-datasets/{test_materials_dataset.id}/upload',
                    data={'file': (csv_file, 'test_materials.csv')},
                    content_type='multipart/form-data'
                )

            assert response.status_code == 200
            data = response.get_json()
            assert data['message'] == 'CSV uploaded and parsed successfully'
            assert data['records_created'] == 3

            # Verify records were created
            records = MaterialRecord.query.filter_by(materials_dataset_id=test_materials_dataset.id).all()
            assert len(records) == 3

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_upload_csv_no_file(self, test_client, test_materials_dataset):
        """Test POST /api/v1/materials-datasets/{id}/upload without file"""
        response = test_client.post(
            f'/api/v1/materials-datasets/{test_materials_dataset.id}/upload',
            data={},
            content_type='multipart/form-data'
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'No file part' in data['message']

    def test_upload_csv_invalid_format(self, test_client, test_materials_dataset):
        """Test POST /api/v1/materials-datasets/{id}/upload with non-CSV file"""
        # Create temp text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('Not a CSV')
            temp_path = f.name

        try:
            with open(temp_path, 'rb') as txt_file:
                response = test_client.post(
                    f'/api/v1/materials-datasets/{test_materials_dataset.id}/upload',
                    data={'file': (txt_file, 'test.txt')},
                    content_type='multipart/form-data'
                )

            assert response.status_code == 400
            data = response.get_json()
            assert 'must be a CSV' in data['message']

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestMaterialRecordsAPI:
    """Tests for MaterialRecords API endpoints"""

    def test_get_records(self, test_client, test_materials_dataset, test_material_record):
        """Test GET /api/v1/materials-datasets/{dataset_id}/records"""
        response = test_client.get(f'/api/v1/materials-datasets/{test_materials_dataset.id}/records')

        assert response.status_code == 200
        data = response.get_json()
        assert 'records' in data
        assert data['total'] == 1
        assert data['page'] == 1
        assert len(data['records']) == 1
        assert data['records'][0]['material_name'] == 'Al2O3'

    def test_get_records_pagination(self, test_client, test_materials_dataset):
        """Test GET /api/v1/materials-datasets/{dataset_id}/records with pagination"""
        # Add 25 records
        for i in range(25):
            record = MaterialRecord(
                materials_dataset_id=test_materials_dataset.id,
                material_name=f'Material{i}',
                property_name='density',
                property_value=str(i)
            )
            db.session.add(record)
        db.session.commit()

        # Get first page (10 per page)
        response = test_client.get(
            f'/api/v1/materials-datasets/{test_materials_dataset.id}/records?page=1&per_page=10'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 25
        assert data['page'] == 1
        assert data['per_page'] == 10
        assert data['total_pages'] == 3
        assert len(data['records']) == 10

        # Get second page
        response = test_client.get(
            f'/api/v1/materials-datasets/{test_materials_dataset.id}/records?page=2&per_page=10'
        )

        data = response.get_json()
        assert data['page'] == 2
        assert len(data['records']) == 10

    def test_search_records(self, test_client, test_materials_dataset):
        """Test GET /api/v1/materials-datasets/{dataset_id}/records/search"""
        # Add test records
        records_data = [
            ('Al2O3', 'Al2O3'),
            ('Alumina', 'Al2O3'),
            ('SiO2', 'SiO2')
        ]
        for name, formula in records_data:
            record = MaterialRecord(
                materials_dataset_id=test_materials_dataset.id,
                material_name=name,
                chemical_formula=formula,
                property_name='density',
                property_value='1.0'
            )
            db.session.add(record)
        db.session.commit()

        # Search for Al2O3
        response = test_client.get(
            f'/api/v1/materials-datasets/{test_materials_dataset.id}/records/search?q=Al2O3'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 2
        assert data['search_term'] == 'Al2O3'
        assert len(data['records']) == 2

    def test_search_records_no_query(self, test_client, test_materials_dataset):
        """Test GET /api/v1/materials-datasets/{dataset_id}/records/search without query"""
        response = test_client.get(
            f'/api/v1/materials-datasets/{test_materials_dataset.id}/records/search'
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'required' in data['message'].lower()
