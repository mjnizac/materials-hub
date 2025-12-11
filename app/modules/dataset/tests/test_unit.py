"""
Unit tests for dataset module - repositories, models, and services.
"""

import tempfile
import unittest.mock
from datetime import datetime, timezone

import pytest

from app import db
from app.modules.auth.models import User
from app.modules.auth.repositories import UserRepository
from app.modules.dataset.models import (
    Author,
    DatasetVersion,
    DataSource,
    DOIMapping,
    DSDownloadRecord,
    DSMetaData,
    DSViewRecord,
    MaterialRecord,
    MaterialsDataset,
    PublicationType,
)
from app.modules.dataset.repositories import (
    AuthorRepository,
    DatasetVersionRepository,
    DSDownloadRecordRepository,
    DSMetaDataRepository,
    DSViewRecordRepository,
    MaterialRecordRepository,
    MaterialsDatasetRepository,
)
from app.modules.dataset.services import (
    AuthorService,
    DatasetVersionService,
    DOIMappingService,
    DSDownloadRecordService,
    DSMetaDataService,
    DSViewRecordService,
    MaterialsDatasetService,
    SizeService,
    calculate_checksum_and_size,
)
from core.services.BaseService import BaseService

# ============================================================================
# Tests for Dataset Repositories
# ============================================================================


@pytest.mark.unit
def test_materials_dataset_repository_get_by_user(test_client):
    """Test MaterialsDatasetRepository.get_by_user() method"""
    user = User(email="test_get_by_user@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    # Create datasets for the user
    for i in range(3):
        metadata = DSMetaData(title=f"Dataset {i}", description="Test dataset", publication_type=PublicationType.NONE)
        db.session.add(metadata)
        db.session.commit()

        dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
        db.session.add(dataset)
        db.session.commit()

        # Create at least one MaterialRecord for the dataset
        record = MaterialRecord(
            materials_dataset_id=dataset.id,
            material_name="Silicon",
            property_name="thermal_conductivity",
            property_value=148.0,
        )
        db.session.add(record)
        db.session.commit()

    repo = MaterialsDatasetRepository()
    datasets = repo.get_by_user(user.id)

    assert len(datasets) == 3
    assert all(d.user_id == user.id for d in datasets)


@pytest.mark.unit
def test_materials_dataset_repository_count_synchronized(test_client):
    """Test MaterialsDatasetRepository.count_synchronized() method"""
    user = User(email="test_count_sync@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    # Create synchronized dataset (with DOI)
    metadata1 = DSMetaData(
        title="Dataset 1", description="Test", dataset_doi="10.1234/test1", publication_type=PublicationType.NONE
    )
    db.session.add(metadata1)
    db.session.commit()

    dataset1 = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata1.id)
    db.session.add(dataset1)
    db.session.commit()

    record1 = MaterialRecord(
        materials_dataset_id=dataset1.id,
        material_name="Silicon",
        property_name="thermal_conductivity",
        property_value=148.0,
    )
    db.session.add(record1)
    db.session.commit()

    # Create unsynchronized dataset (without DOI)
    metadata2 = DSMetaData(
        title="Dataset 2", description="Test", dataset_doi=None, publication_type=PublicationType.NONE
    )
    db.session.add(metadata2)
    db.session.commit()

    dataset2 = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata2.id)
    db.session.add(dataset2)
    db.session.commit()

    record2 = MaterialRecord(
        materials_dataset_id=dataset2.id,
        material_name="Silicon",
        property_name="thermal_conductivity",
        property_value=148.0,
    )
    db.session.add(record2)
    db.session.commit()

    repo = MaterialsDatasetRepository()
    count = repo.count_synchronized()

    assert count == 1


@pytest.mark.unit
def test_materials_dataset_repository_get_synchronized_latest(test_client):
    """Test MaterialsDatasetRepository.get_synchronized_latest() method"""
    user = User(email="test_get_synchronized_lat@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    # Create 3 synchronized datasets
    for i in range(3):
        metadata = DSMetaData(
            title=f"Dataset {i}",
            description="Test",
            dataset_doi=f"10.1234/test{i}",
            publication_type=PublicationType.NONE,
        )
        db.session.add(metadata)
        db.session.commit()

        dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
        db.session.add(dataset)
        db.session.commit()

        record = MaterialRecord(
            materials_dataset_id=dataset.id,
            material_name="Silicon",
            property_name="thermal_conductivity",
            property_value=148.0,
        )
        db.session.add(record)
        db.session.commit()

    repo = MaterialsDatasetRepository()
    datasets = repo.get_synchronized_latest(limit=2)

    assert len(datasets) == 2
    assert all(d.ds_meta_data.dataset_doi is not None for d in datasets)


@pytest.mark.unit
def test_material_record_repository_get_by_dataset(test_client):
    """Test MaterialRecordRepository.get_by_dataset() method"""
    user = User(email="test_get_by_dataset@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Dataset 1", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    # Create 5 material records
    for i in range(5):
        record = MaterialRecord(
            materials_dataset_id=dataset.id,
            material_name=f"Material_{i}",
            property_name="thermal_conductivity",
            property_value=100.0 + i,
        )
        db.session.add(record)
    db.session.commit()

    repo = MaterialRecordRepository()
    records = repo.get_by_dataset(dataset.id)

    assert len(records) == 5
    assert all(r.materials_dataset_id == dataset.id for r in records)


@pytest.mark.unit
def test_material_record_repository_search_materials(test_client):
    """Test MaterialRecordRepository.search_materials() method"""
    user = User(email="test_repository_search_ma@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Dataset 1", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    # Create material records with different names and formulas
    records_data = [
        {"material_name": "Silicon", "chemical_formula": "Si"},
        {"material_name": "Silicon Dioxide", "chemical_formula": "SiO2"},
        {"material_name": "Aluminum", "chemical_formula": "Al"},
    ]

    for data in records_data:
        record = MaterialRecord(
            materials_dataset_id=dataset.id,
            material_name=data["material_name"],
            chemical_formula=data["chemical_formula"],
            property_name="thermal_conductivity",
            property_value=100.0,
        )
        db.session.add(record)
    db.session.commit()

    repo = MaterialRecordRepository()

    # Search by material name
    results = repo.search_materials(dataset.id, "Silicon")
    assert len(results) == 2

    # Search by chemical formula
    results = repo.search_materials(dataset.id, "Al")
    assert len(results) == 1


@pytest.mark.unit
def test_material_record_repository_filter_by_temperature_range(test_client):
    """Test MaterialRecordRepository.filter_by_temperature_range() method"""
    user = User(email="test_by_temperature_range@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Dataset 1", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    # Create records with different temperatures
    temperatures = [100, 200, 300, 400, 500]
    for temp in temperatures:
        record = MaterialRecord(
            materials_dataset_id=dataset.id,
            material_name="Silicon",
            property_name="thermal_conductivity",
            property_value=148.0,
            temperature=temp,
        )
        db.session.add(record)
    db.session.commit()

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


@pytest.mark.unit
def test_material_record_repository_get_unique_materials(test_client):
    """Test MaterialRecordRepository.get_unique_materials() method"""
    user = User(email="test_record_repo_unique_mats@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Dataset 1", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    # Create records with duplicate material names
    materials = ["Silicon", "Silicon", "Aluminum", "Aluminum", "Copper"]
    for material in materials:
        record = MaterialRecord(
            materials_dataset_id=dataset.id,
            material_name=material,
            property_name="thermal_conductivity",
            property_value=100.0,
        )
        db.session.add(record)
    db.session.commit()

    repo = MaterialRecordRepository()
    unique_materials = repo.get_unique_materials(dataset.id)

    # Should return tuples, extract the material names
    material_names = [m[0] for m in unique_materials]
    assert len(material_names) == 3
    assert set(material_names) == {"Silicon", "Aluminum", "Copper"}


@pytest.mark.unit
def test_ds_download_record_repository_total_downloads(test_client):
    """Test DSDownloadRecordRepository.total_dataset_downloads() method"""
    user = User(email="test_repository_total_dow@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Dataset 1", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    record = MaterialRecord(
        materials_dataset_id=dataset.id,
        material_name="Silicon",
        property_name="thermal_conductivity",
        property_value=148.0,
    )
    db.session.add(record)
    db.session.commit()

    # Create 5 download records
    for i in range(5):
        download = DSDownloadRecord(
            user_id=user.id,
            dataset_id=dataset.id,
            download_date=datetime.now(timezone.utc),
            download_cookie=f"cookie{i}",
        )
        db.session.add(download)
    db.session.commit()

    repo = DSDownloadRecordRepository()
    total = repo.total_dataset_downloads()

    # The method returns max(id), which should be 5
    assert total == 5


@pytest.mark.unit
def test_ds_view_record_repository_total_views(test_client):
    """Test DSViewRecordRepository.total_dataset_views() method"""
    user = User(email="test_repository_total_vie@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Dataset 1", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    record = MaterialRecord(
        materials_dataset_id=dataset.id,
        material_name="Silicon",
        property_name="thermal_conductivity",
        property_value=148.0,
    )
    db.session.add(record)
    db.session.commit()

    # Create 7 view records
    for i in range(7):
        view = DSViewRecord(
            user_id=user.id, dataset_id=dataset.id, view_date=datetime.now(timezone.utc), view_cookie=f"cookie{i}"
        )
        db.session.add(view)
    db.session.commit()

    repo = DSViewRecordRepository()
    total = repo.total_dataset_views()

    # The method returns max(id), which should be 7
    assert total == 7


@pytest.mark.unit
def test_ds_metadata_repository_filter_by_doi(test_client):
    """Test DSMetaDataRepository.filter_by_doi() method"""
    # Create metadata with DOI
    metadata = DSMetaData(
        title="Dataset 1", description="Test", dataset_doi="10.1234/test123", publication_type=PublicationType.NONE
    )
    db.session.add(metadata)
    db.session.commit()

    repo = DSMetaDataRepository()
    result = repo.filter_by_doi("10.1234/test123")

    assert result is not None
    assert result.dataset_doi == "10.1234/test123"
    assert result.title == "Dataset 1"

    # Test non-existent DOI
    result = repo.filter_by_doi("10.9999/nonexistent")
    assert result is None


# ============================================================================
# Tests for Dataset Models
# ============================================================================


@pytest.mark.unit
def test_materials_dataset_name_method(test_client):
    """Test MaterialsDataset.name() method"""
    user = User(email="test_dataset_name_method@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test Dataset", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    assert dataset.name() == "Test Dataset"


@pytest.mark.unit
def test_materials_dataset_get_cleaned_publication_type(test_client):
    """Test MaterialsDataset.get_cleaned_publication_type() method"""
    user = User(email="test_cleaned_publication_@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.JOURNAL_ARTICLE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    # Should convert JOURNAL_ARTICLE to "Journal Article"
    assert dataset.get_cleaned_publication_type() == "Journal Article"


@pytest.mark.unit
def test_materials_dataset_get_zenodo_url(test_client):
    """Test MaterialsDataset.get_zenodo_url() method"""
    user = User(email="test_get_zenodo_url@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    # Dataset with DOI and deposition_id
    metadata1 = DSMetaData(
        title="Test1",
        description="Test",
        publication_type=PublicationType.NONE,
        dataset_doi="10.1234/test",
        deposition_id=123456,
    )
    db.session.add(metadata1)
    db.session.commit()

    dataset1 = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata1.id)
    db.session.add(dataset1)
    db.session.commit()

    assert dataset1.get_zenodo_url() == "https://zenodo.org/record/123456"

    # Dataset without DOI
    metadata2 = DSMetaData(title="Test2", description="Test", publication_type=PublicationType.NONE, dataset_doi=None)
    db.session.add(metadata2)
    db.session.commit()

    dataset2 = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata2.id)
    db.session.add(dataset2)
    db.session.commit()

    assert dataset2.get_zenodo_url() is None


@pytest.mark.unit
def test_materials_dataset_get_materials_count(test_client):
    """Test MaterialsDataset.get_materials_count() method"""
    user = User(email="test_get_materials_count@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    # Create 3 material records
    for i in range(3):
        record = MaterialRecord(
            materials_dataset_id=dataset.id,
            material_name=f"Material_{i}",
            property_name="density",
            property_value="100",
        )
        db.session.add(record)
    db.session.commit()

    assert dataset.get_materials_count() == 3


@pytest.mark.unit
def test_materials_dataset_get_unique_materials(test_client):
    """Test MaterialsDataset.get_unique_materials() method"""
    user = User(email="test_dataset_unique_mats@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    # Create records with duplicate material names
    materials = ["Silicon", "Silicon", "Aluminum", "Copper"]
    for material in materials:
        record = MaterialRecord(
            materials_dataset_id=dataset.id, material_name=material, property_name="density", property_value="100"
        )
        db.session.add(record)
    db.session.commit()

    unique_materials = dataset.get_unique_materials()
    assert len(unique_materials) == 3
    assert set(unique_materials) == {"Silicon", "Aluminum", "Copper"}


@pytest.mark.unit
def test_materials_dataset_get_unique_properties(test_client):
    """Test MaterialsDataset.get_unique_properties() method"""
    user = User(email="test_get_unique_propertie@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    # Create records with different properties
    properties = ["density", "thermal_conductivity", "density", "electrical_conductivity"]
    for prop in properties:
        record = MaterialRecord(
            materials_dataset_id=dataset.id, material_name="Silicon", property_name=prop, property_value="100"
        )
        db.session.add(record)
    db.session.commit()

    unique_properties = dataset.get_unique_properties()
    assert len(unique_properties) == 3
    assert set(unique_properties) == {"density", "thermal_conductivity", "electrical_conductivity"}


@pytest.mark.unit
def test_materials_dataset_validate_success(test_client):
    """Test MaterialsDataset.validate() method with valid dataset"""
    user = User(email="test_dataset_validate_suc@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id, csv_file_path="/path/to/file.csv")
    db.session.add(dataset)
    db.session.commit()

    record = MaterialRecord(
        materials_dataset_id=dataset.id, material_name="Silicon", property_name="density", property_value="2.33"
    )
    db.session.add(record)
    db.session.commit()

    # Should not raise any exception
    dataset.validate()


@pytest.mark.unit
def test_materials_dataset_validate_no_csv_path(test_client):
    """Test MaterialsDataset.validate() fails without CSV path"""
    user = User(email="test_no_csv_path@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id, csv_file_path=None)
    db.session.add(dataset)
    db.session.commit()

    with pytest.raises(ValueError, match="Materials dataset must have a CSV file path"):
        dataset.validate()


@pytest.mark.unit
def test_materials_dataset_validate_no_records(test_client):
    """Test MaterialsDataset.validate() fails without material records"""
    user = User(email="test_validate_no_records@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id, csv_file_path="/path/to/file.csv")
    db.session.add(dataset)
    db.session.commit()

    with pytest.raises(ValueError, match="Materials dataset must have at least one material record"):
        dataset.validate()


@pytest.mark.unit
def test_material_record_to_dict(test_client):
    """Test MaterialRecord.to_dict() method"""
    user = User(email="test_record_to_dict@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    record = MaterialRecord(
        materials_dataset_id=dataset.id,
        material_name="Silicon",
        chemical_formula="Si",
        structure_type="Diamond",
        composition_method="CVD",
        property_name="thermal_conductivity",
        property_value="148",
        property_unit="W/mK",
        temperature=300,
        pressure=1,
        data_source=DataSource.EXPERIMENTAL,
        uncertainty=5,
        description="High purity silicon",
    )
    db.session.add(record)
    db.session.commit()

    result = record.to_dict()

    assert result["material_name"] == "Silicon"
    assert result["chemical_formula"] == "Si"
    assert result["structure_type"] == "Diamond"
    assert result["composition_method"] == "CVD"
    assert result["property_name"] == "thermal_conductivity"
    assert result["property_value"] == "148"
    assert result["property_unit"] == "W/mK"
    assert result["temperature"] == 300
    assert result["pressure"] == 1
    assert result["data_source"] == "experimental"
    assert result["uncertainty"] == 5
    assert result["description"] == "High purity silicon"


# ============================================================================
# Tests for Services - UserProfileService, BaseService, and dataset services
# ============================================================================


@pytest.mark.unit
def test_base_service_create(test_client):
    """Test BaseService.create() method"""
    service = BaseService(UserRepository())
    user = service.create(email="test_base_service_create@example.com", password="test123")

    assert user is not None
    assert user.email == "test_base_service_create@example.com"


@pytest.mark.unit
def test_base_service_get_by_id(test_client):
    """Test BaseService.get_by_id() method"""
    user = User(email="test_base_service_get@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    service = BaseService(UserRepository())
    retrieved_user = service.get_by_id(user.id)

    assert retrieved_user is not None
    assert retrieved_user.id == user.id
    assert retrieved_user.email == "test_base_service_get@example.com"


@pytest.mark.unit
def test_base_service_count(test_client):
    """Test BaseService.count() method"""
    initial_count = User.query.count()

    user = User(email="test_base_service_count@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    service = BaseService(UserRepository())
    count = service.count()

    assert count == initial_count + 1


@pytest.mark.unit
def test_base_service_update(test_client):
    """Test BaseService.update() method"""
    user = User(email="test_base_service_update@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    service = BaseService(UserRepository())
    updated_user = service.update(user.id, email="updated_email@example.com")

    assert updated_user is not None
    assert updated_user.email == "updated_email@example.com"


@pytest.mark.unit
def test_base_service_delete(test_client):
    """Test BaseService.delete() method"""
    user = User(email="test_base_service_delete@example.com", password="test123")
    db.session.add(user)
    db.session.commit()
    user_id = user.id

    service = BaseService(UserRepository())
    result = service.delete(user_id)

    assert result is True
    assert User.query.get(user_id) is None


@pytest.mark.unit
def test_base_repository_create(test_client):
    """Test BaseRepository.create() method"""
    repo = UserRepository()
    user = repo.create(email="test_base_repo_create@example.com", password="test123")

    assert user is not None
    assert user.email == "test_base_repo_create@example.com"


@pytest.mark.unit
def test_base_repository_get_by_column(test_client):
    """Test BaseRepository.get_by_column() method"""
    user = User(email="test_base_repo_column@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    repo = UserRepository()
    results = repo.get_by_column("email", "test_base_repo_column@example.com")

    assert len(results) == 1
    assert results[0].email == "test_base_repo_column@example.com"


@pytest.mark.unit
def test_base_repository_delete_by_column(test_client):
    """Test BaseRepository.delete_by_column() method"""
    # Using Author model since it doesn't have unique constraint on name
    author1 = Author(name="John Doe", affiliation="University A")
    author2 = Author(name="John Doe", affiliation="University B")
    db.session.add(author1)
    db.session.add(author2)
    db.session.commit()

    repo = AuthorRepository()
    result = repo.delete_by_column("name", "John Doe")

    assert result is True
    remaining = repo.get_by_column("name", "John Doe")
    assert len(remaining) == 0


@pytest.mark.unit
def test_author_service_initialization(test_client):
    """Test AuthorService initialization"""
    service = AuthorService()
    assert service.repository is not None


@pytest.mark.unit
def test_ds_download_record_service_initialization(test_client):
    """Test DSDownloadRecordService initialization"""
    service = DSDownloadRecordService()
    assert service.repository is not None


@pytest.mark.unit
def test_ds_metadata_service_filter_by_doi(test_client):
    """Test DSMetaDataService.filter_by_doi() method"""
    metadata = DSMetaData(
        title="Test Dataset", description="Test", dataset_doi="10.1234/test", publication_type=PublicationType.NONE
    )
    db.session.add(metadata)
    db.session.commit()

    service = DSMetaDataService()
    result = service.filter_by_doi("10.1234/test")

    assert result is not None
    assert result.dataset_doi == "10.1234/test"


@pytest.mark.unit
def test_ds_view_record_service_create_cookie_new(test_client):
    """Test DSViewRecordService.create_cookie() for new cookie"""
    user = User(email="test_view_cookie_new@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    record = MaterialRecord(
        materials_dataset_id=dataset.id, material_name="Silicon", property_name="density", property_value="100"
    )
    db.session.add(record)
    db.session.commit()

    service = DSViewRecordService()

    # Mock request to simulate no cookie
    with test_client.application.test_request_context():
        from flask import request

        with unittest.mock.patch.object(request, "cookies", {"view_cookie": None}):
            cookie = service.create_cookie(dataset)

    assert cookie is not None
    assert len(cookie) > 0


@pytest.mark.unit
def test_doi_mapping_service_get_new_doi(test_client):
    """Test DOIMappingService.get_new_doi() method"""
    mapping = DOIMapping(dataset_doi_old="10.1234/old", dataset_doi_new="10.1234/new")
    db.session.add(mapping)
    db.session.commit()

    service = DOIMappingService()
    new_doi = service.get_new_doi("10.1234/old")

    assert new_doi == "10.1234/new"


@pytest.mark.unit
def test_doi_mapping_service_get_new_doi_not_found(test_client):
    """Test DOIMappingService.get_new_doi() when mapping not found"""
    service = DOIMappingService()
    new_doi = service.get_new_doi("10.1234/nonexistent")

    assert new_doi is None


@pytest.mark.unit
def test_size_service_bytes(test_client):
    """Test SizeService.get_human_readable_size() for bytes"""
    service = SizeService()
    result = service.get_human_readable_size(512)

    assert result == "512 bytes"


@pytest.mark.unit
def test_size_service_kilobytes(test_client):
    """Test SizeService.get_human_readable_size() for KB"""
    service = SizeService()
    result = service.get_human_readable_size(1024 * 5)

    assert result == "5.0 KB"


@pytest.mark.unit
def test_size_service_megabytes(test_client):
    """Test SizeService.get_human_readable_size() for MB"""
    service = SizeService()
    result = service.get_human_readable_size(1024 * 1024 * 10)

    assert result == "10.0 MB"


@pytest.mark.unit
def test_size_service_gigabytes(test_client):
    """Test SizeService.get_human_readable_size() for GB"""
    service = SizeService()
    result = service.get_human_readable_size(1024 * 1024 * 1024 * 2)

    assert result == "2.0 GB"


@pytest.mark.unit
def test_calculate_checksum_and_size(test_client):
    """Test calculate_checksum_and_size() function"""
    import os

    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("test content")
        temp_path = f.name

    try:
        checksum, size = calculate_checksum_and_size(temp_path)

        assert checksum is not None
        assert len(checksum) == 32  # MD5 hash length
        assert size > 0
    finally:
        os.unlink(temp_path)


# ============================================================================
# Tests for DSMetaDataService
# ============================================================================


@pytest.mark.unit
def test_ds_metadata_service_update(test_client):
    """Test DSMetaDataService.update() method"""
    metadata = DSMetaData(title="Original Title", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    service = DSMetaDataService()
    updated = service.update(metadata.id, title="Updated Title", description="Updated description")

    assert updated is not None
    assert updated.title == "Updated Title"
    assert updated.description == "Updated description"


# ============================================================================
# Tests for DSViewRecordService
# ============================================================================


@pytest.mark.unit
def test_ds_view_record_service_the_record_exists_true(test_client):
    """Test DSViewRecordService.the_record_exists() returns True"""
    from unittest.mock import Mock, patch

    user = User(email="test_record_exists_tru@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    record = MaterialRecord(
        materials_dataset_id=dataset.id, material_name="Silicon", property_name="density", property_value="100"
    )
    db.session.add(record)
    db.session.commit()

    # Create a view record
    view_record = DSViewRecord(
        user_id=user.id, dataset_id=dataset.id, view_date=datetime.now(timezone.utc), view_cookie="test_cookie"
    )
    db.session.add(view_record)
    db.session.commit()

    # Mock current_user
    mock_user = Mock()
    mock_user.id = user.id
    mock_user.is_authenticated = True

    service = DSViewRecordService()
    with patch("app.modules.dataset.repositories.current_user", mock_user):
        exists = service.the_record_exists(dataset, "test_cookie")

    assert exists is not None


@pytest.mark.unit
def test_ds_view_record_service_the_record_exists_false(test_client):
    """Test DSViewRecordService.the_record_exists() returns False"""
    from unittest.mock import Mock, patch

    user = User(email="test_record_exists_fal@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    record = MaterialRecord(
        materials_dataset_id=dataset.id, material_name="Silicon", property_name="density", property_value="100"
    )
    db.session.add(record)
    db.session.commit()

    # Mock current_user
    mock_user = Mock()
    mock_user.id = user.id
    mock_user.is_authenticated = True

    service = DSViewRecordService()
    with patch("app.modules.dataset.repositories.current_user", mock_user):
        exists = service.the_record_exists(dataset, "nonexistent_cookie")

    assert exists is None


@pytest.mark.unit
def test_ds_view_record_service_create_new_record(test_client):
    """Test DSViewRecordService.create_new_record() method"""
    from unittest.mock import Mock, patch

    user = User(email="test_create_new_record@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    record = MaterialRecord(
        materials_dataset_id=dataset.id, material_name="Silicon", property_name="density", property_value="100"
    )
    db.session.add(record)
    db.session.commit()

    # Mock current_user
    mock_user = Mock()
    mock_user.id = user.id
    mock_user.is_authenticated = True

    service = DSViewRecordService()
    with patch("app.modules.dataset.repositories.current_user", mock_user):
        view_record = service.create_new_record(dataset, "new_cookie_123")

    assert view_record is not None
    assert view_record.dataset_id == dataset.id
    assert view_record.view_cookie == "new_cookie_123"
    assert view_record.view_date is not None


# ============================================================================
# Tests for MaterialsDatasetService
# ============================================================================


@pytest.mark.unit
def test_materials_dataset_service_validate_csv_columns_valid(test_client):
    """Test MaterialsDatasetService.validate_csv_columns() with valid columns"""
    service = MaterialsDatasetService()
    columns = ["material_name", "property_name", "property_value", "chemical_formula", "temperature"]

    result = service.validate_csv_columns(columns)

    assert result["valid"] is True
    assert len(result["missing_required"]) == 0
    assert result["message"] == "CSV structure is valid"


@pytest.mark.unit
def test_materials_dataset_service_validate_csv_columns_missing_required(test_client):
    """Test MaterialsDatasetService.validate_csv_columns() with missing required columns"""
    service = MaterialsDatasetService()
    columns = ["material_name", "property_name"]  # Missing property_value

    result = service.validate_csv_columns(columns)

    assert result["valid"] is False
    assert "property_value" in result["missing_required"]
    assert "Missing required columns" in result["message"]


@pytest.mark.unit
def test_materials_dataset_service_validate_csv_columns_extra(test_client):
    """Test MaterialsDatasetService.validate_csv_columns() with extra unknown columns"""
    service = MaterialsDatasetService()
    columns = ["material_name", "property_name", "property_value", "unknown_column"]

    result = service.validate_csv_columns(columns)

    assert result["valid"] is True  # Still valid if has required columns
    assert "unknown_column" in result["extra_columns"]
    assert "Unknown columns" in result["message"]


@pytest.mark.unit
def test_materials_dataset_service_build_validation_message(test_client):
    """Test MaterialsDatasetService._build_validation_message() method"""
    service = MaterialsDatasetService()

    # No errors
    message = service._build_validation_message([], [])
    assert message == "CSV structure is valid"

    # Missing required
    message = service._build_validation_message(["col1", "col2"], [])
    assert "Missing required columns: col1, col2" in message

    # Extra columns
    message = service._build_validation_message([], ["extra1", "extra2"])
    assert "Unknown columns (will be ignored): extra1, extra2" in message

    # Both missing and extra
    message = service._build_validation_message(["missing"], ["extra"])
    assert "Missing required columns" in message
    assert "Unknown columns" in message


@pytest.mark.unit
def test_materials_dataset_service_parse_csv_file_success(test_client):
    """Test MaterialsDatasetService.parse_csv_file() with valid CSV"""
    import csv
    import os

    service = MaterialsDatasetService()

    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["material_name", "property_name", "property_value", "temperature"])
        writer.writerow(["Silicon", "thermal_conductivity", "148", "300"])
        writer.writerow(["Aluminum", "density", "2.7", ""])
        temp_path = f.name

    try:
        result = service.parse_csv_file(temp_path)

        assert result["success"] is True
        assert result["rows_parsed"] == 2
        assert len(result["data"]) == 2
        assert result["data"][0]["material_name"] == "Silicon"
        assert result["data"][0]["temperature"] == 300
        assert result["data"][1]["material_name"] == "Aluminum"
        assert result["data"][1]["temperature"] is None
    finally:
        os.unlink(temp_path)


@pytest.mark.unit
def test_materials_dataset_service_parse_csv_file_missing_columns(test_client):
    """Test MaterialsDatasetService.parse_csv_file() with missing required columns"""
    import csv
    import os

    service = MaterialsDatasetService()

    # Create a CSV with missing required column
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["material_name", "property_name"])  # Missing property_value
        writer.writerow(["Silicon", "thermal_conductivity"])
        temp_path = f.name

    try:
        result = service.parse_csv_file(temp_path)

        assert result["success"] is False
        assert "Missing required columns" in result["error"]
    finally:
        os.unlink(temp_path)


@pytest.mark.unit
def test_materials_dataset_service_parse_csv_file_not_found(test_client):
    """Test MaterialsDatasetService.parse_csv_file() with non-existent file"""
    service = MaterialsDatasetService()

    result = service.parse_csv_file("/nonexistent/path/to/file.csv")

    assert result["success"] is False
    assert "CSV file not found" in result["error"]


@pytest.mark.unit
def test_materials_dataset_service_parse_csv_row_valid(test_client):
    """Test MaterialsDatasetService._parse_csv_row() with valid data"""
    service = MaterialsDatasetService()

    row = {
        "material_name": "Silicon",
        "property_name": "thermal_conductivity",
        "property_value": "148",
        "chemical_formula": "Si",
        "temperature": "300",
        "pressure": "1",
        "uncertainty": "5",
        "data_source": "EXPERIMENTAL",
    }

    parsed = service._parse_csv_row(row, row_num=2)

    assert parsed["material_name"] == "Silicon"
    assert parsed["property_name"] == "thermal_conductivity"
    assert parsed["property_value"] == "148"
    assert parsed["chemical_formula"] == "Si"
    assert parsed["temperature"] == 300
    assert parsed["pressure"] == 1
    assert parsed["uncertainty"] == 5
    assert parsed["data_source"] == DataSource.EXPERIMENTAL


@pytest.mark.unit
def test_materials_dataset_service_parse_csv_row_missing_required(test_client):
    """Test MaterialsDatasetService._parse_csv_row() with missing required field"""
    service = MaterialsDatasetService()

    row = {
        "material_name": "",  # Empty required field
        "property_name": "thermal_conductivity",
        "property_value": "148",
    }

    with pytest.raises(ValueError, match="material_name is required"):
        service._parse_csv_row(row, row_num=2)


@pytest.mark.unit
def test_materials_dataset_service_parse_csv_row_invalid_data_source(test_client):
    """Test MaterialsDatasetService._parse_csv_row() with invalid data_source"""
    service = MaterialsDatasetService()

    row = {
        "material_name": "Silicon",
        "property_name": "thermal_conductivity",
        "property_value": "148",
        "data_source": "INVALID_SOURCE",
    }

    # Should not raise, but set data_source to None
    parsed = service._parse_csv_row(row, row_num=2)
    assert parsed["data_source"] is None


@pytest.mark.unit
def test_materials_dataset_service_create_material_records_from_csv(test_client):
    """Test MaterialsDatasetService.create_material_records_from_csv()"""
    import csv
    import os

    user = User(email="test_create_mat_records@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    service = MaterialsDatasetService()

    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["material_name", "property_name", "property_value"])
        writer.writerow(["Silicon", "thermal_conductivity", "148"])
        writer.writerow(["Aluminum", "density", "2.7"])
        temp_path = f.name

    try:
        result = service.create_material_records_from_csv(dataset, temp_path)

        assert result["success"] is True
        assert result["records_created"] == 2
        assert result["error"] is None

        # Verify records were created
        records = MaterialRecord.query.filter_by(materials_dataset_id=dataset.id).all()
        assert len(records) == 2
    finally:
        os.unlink(temp_path)


@pytest.mark.unit
def test_materials_dataset_service_get_recommendations(test_client):
    """Test MaterialsDatasetService.get_recommendations()"""
    user = User(email="test_get_recommendations@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    # Create current dataset with tags
    metadata1 = DSMetaData(
        title="Dataset 1",
        description="Test",
        publication_type=PublicationType.JOURNAL_ARTICLE,
        tags="materials, silicon, conductivity",
    )
    db.session.add(metadata1)
    db.session.commit()

    dataset1 = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata1.id)
    db.session.add(dataset1)
    db.session.commit()

    record1 = MaterialRecord(
        materials_dataset_id=dataset1.id, material_name="Silicon", property_name="density", property_value="100"
    )
    db.session.add(record1)
    db.session.commit()

    # Create similar dataset (shares tags)
    metadata2 = DSMetaData(
        title="Dataset 2",
        description="Test",
        publication_type=PublicationType.JOURNAL_ARTICLE,
        tags="materials, aluminum",
    )
    db.session.add(metadata2)
    db.session.commit()

    dataset2 = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata2.id)
    db.session.add(dataset2)
    db.session.commit()

    record2 = MaterialRecord(
        materials_dataset_id=dataset2.id, material_name="Aluminum", property_name="density", property_value="100"
    )
    db.session.add(record2)
    db.session.commit()

    service = MaterialsDatasetService()
    recommendations = service.get_recommendations(dataset1.id, limit=3)

    assert len(recommendations) >= 1
    assert dataset2 in recommendations


@pytest.mark.unit
def test_materials_dataset_service_get_recommendations_no_tags(test_client):
    """Test MaterialsDatasetService.get_recommendations() with dataset without tags"""
    user = User(email="test_recommendations_no@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    # Create dataset without tags
    metadata = DSMetaData(title="Dataset 1", description="Test", publication_type=PublicationType.NONE, tags=None)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    record = MaterialRecord(
        materials_dataset_id=dataset.id, material_name="Silicon", property_name="density", property_value="100"
    )
    db.session.add(record)
    db.session.commit()

    service = MaterialsDatasetService()
    recommendations = service.get_recommendations(dataset.id, limit=3)

    # Should return recent datasets (empty list since this is the only one)
    assert isinstance(recommendations, list)


@pytest.mark.unit
def test_materials_dataset_service_get_all_except(test_client):
    """Test MaterialsDatasetService.get_all_except()"""
    user = User(email="test_get_all_except@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    # Create 3 datasets
    datasets = []
    for i in range(3):
        metadata = DSMetaData(title=f"Dataset {i}", description="Test", publication_type=PublicationType.NONE)
        db.session.add(metadata)
        db.session.commit()

        dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
        db.session.add(dataset)
        db.session.commit()

        record = MaterialRecord(
            materials_dataset_id=dataset.id, material_name="Silicon", property_name="density", property_value="100"
        )
        db.session.add(record)
        db.session.commit()

        datasets.append(dataset)

    service = MaterialsDatasetService()
    result = service.get_all_except(datasets[0].id)

    assert len(result) >= 2
    assert datasets[0] not in result


@pytest.mark.unit
def test_materials_dataset_service_filter_by_authors(test_client):
    """Test MaterialsDatasetService.filter_by_authors()"""
    user = User(email="test_filter_by_authors@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    # Create dataset with author
    metadata1 = DSMetaData(title="Dataset 1", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata1)
    db.session.commit()

    author1 = Author(name="John Doe", affiliation="University A", ds_meta_data_id=metadata1.id)
    db.session.add(author1)
    db.session.commit()

    dataset1 = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata1.id)
    db.session.add(dataset1)
    db.session.commit()

    record1 = MaterialRecord(
        materials_dataset_id=dataset1.id, material_name="Silicon", property_name="density", property_value="100"
    )
    db.session.add(record1)
    db.session.commit()

    # Create dataset with same author
    metadata2 = DSMetaData(title="Dataset 2", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata2)
    db.session.commit()

    author2 = Author(name="John Doe", affiliation="University B", ds_meta_data_id=metadata2.id)
    db.session.add(author2)
    db.session.commit()

    dataset2 = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata2.id)
    db.session.add(dataset2)
    db.session.commit()

    record2 = MaterialRecord(
        materials_dataset_id=dataset2.id, material_name="Aluminum", property_name="density", property_value="100"
    )
    db.session.add(record2)
    db.session.commit()

    # Create dataset with different author
    metadata3 = DSMetaData(title="Dataset 3", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata3)
    db.session.commit()

    author3 = Author(name="Jane Smith", affiliation="University C", ds_meta_data_id=metadata3.id)
    db.session.add(author3)
    db.session.commit()

    dataset3 = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata3.id)
    db.session.add(dataset3)
    db.session.commit()

    record3 = MaterialRecord(
        materials_dataset_id=dataset3.id, material_name="Copper", property_name="density", property_value="100"
    )
    db.session.add(record3)
    db.session.commit()

    service = MaterialsDatasetService()
    all_datasets = [dataset2, dataset3]
    filtered = service.filter_by_authors(all_datasets, dataset1)

    assert dataset2 in filtered  # Same author
    assert dataset3 not in filtered  # Different author


@pytest.mark.unit
def test_materials_dataset_service_filter_by_tags(test_client):
    """Test MaterialsDatasetService.filter_by_tags()"""
    user = User(email="test_filter_by_tags@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    # Create dataset with tags
    metadata1 = DSMetaData(
        title="Dataset 1", description="Test", publication_type=PublicationType.NONE, tags="materials, silicon"
    )
    db.session.add(metadata1)
    db.session.commit()

    dataset1 = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata1.id)
    db.session.add(dataset1)
    db.session.commit()

    record1 = MaterialRecord(
        materials_dataset_id=dataset1.id, material_name="Silicon", property_name="density", property_value="100"
    )
    db.session.add(record1)
    db.session.commit()

    # Create dataset with overlapping tags
    metadata2 = DSMetaData(
        title="Dataset 2", description="Test", publication_type=PublicationType.NONE, tags="silicon, conductivity"
    )
    db.session.add(metadata2)
    db.session.commit()

    dataset2 = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata2.id)
    db.session.add(dataset2)
    db.session.commit()

    record2 = MaterialRecord(
        materials_dataset_id=dataset2.id, material_name="Silicon", property_name="conductivity", property_value="100"
    )
    db.session.add(record2)
    db.session.commit()

    # Create dataset with no overlapping tags
    metadata3 = DSMetaData(
        title="Dataset 3", description="Test", publication_type=PublicationType.NONE, tags="aluminum, copper"
    )
    db.session.add(metadata3)
    db.session.commit()

    dataset3 = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata3.id)
    db.session.add(dataset3)
    db.session.commit()

    record3 = MaterialRecord(
        materials_dataset_id=dataset3.id, material_name="Aluminum", property_name="density", property_value="100"
    )
    db.session.add(record3)
    db.session.commit()

    service = MaterialsDatasetService()
    all_datasets = [dataset2, dataset3]
    filtered = service.filter_by_tags(all_datasets, dataset1)

    assert dataset2 in filtered  # Shares 'silicon' tag
    assert dataset3 not in filtered  # No shared tags


@pytest.mark.unit
def test_materials_dataset_service_filter_by_properties(test_client):
    """Test MaterialsDatasetService.filter_by_properties()"""
    user = User(email="test_filter_by_properti@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    # Create dataset with specific properties
    metadata1 = DSMetaData(title="Dataset 1", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata1)
    db.session.commit()

    dataset1 = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata1.id)
    db.session.add(dataset1)
    db.session.commit()

    record1 = MaterialRecord(
        materials_dataset_id=dataset1.id,
        material_name="Silicon",
        property_name="thermal_conductivity",
        property_value="148",
    )
    db.session.add(record1)
    db.session.commit()

    # Create dataset with same property
    metadata2 = DSMetaData(title="Dataset 2", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata2)
    db.session.commit()

    dataset2 = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata2.id)
    db.session.add(dataset2)
    db.session.commit()

    record2 = MaterialRecord(
        materials_dataset_id=dataset2.id,
        material_name="Aluminum",
        property_name="thermal_conductivity",
        property_value="237",
    )
    db.session.add(record2)
    db.session.commit()

    # Create dataset with different property
    metadata3 = DSMetaData(title="Dataset 3", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata3)
    db.session.commit()

    dataset3 = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata3.id)
    db.session.add(dataset3)
    db.session.commit()

    record3 = MaterialRecord(
        materials_dataset_id=dataset3.id,
        material_name="Copper",
        property_name="electrical_resistivity",
        property_value="1.68",
    )
    db.session.add(record3)
    db.session.commit()

    service = MaterialsDatasetService()
    all_datasets = [dataset2, dataset3]
    filtered = service.filter_by_properties(all_datasets, dataset1)

    assert dataset2 in filtered  # Same property
    assert dataset3 not in filtered  # Different property


@pytest.mark.unit
def test_materials_dataset_service_get_top_global_downloads(test_client):
    """Test MaterialsDatasetService.get_top_global() for downloads"""
    service = MaterialsDatasetService()

    # Call the method (it delegates to repository)
    result = service.get_top_global(metric="downloads", limit=10, days=30)

    # Just verify it returns a list
    assert isinstance(result, list)


@pytest.mark.unit
def test_materials_dataset_service_get_top_global_views(test_client):
    """Test MaterialsDatasetService.get_top_global() for views"""
    service = MaterialsDatasetService()

    # Call the method (it delegates to repository)
    result = service.get_top_global(metric="views", limit=10, days=30)

    # Just verify it returns a list
    assert isinstance(result, list)


# ============================================================================
# Tests for MaterialsDatasetService.create_from_form()
# ============================================================================


@pytest.mark.unit
def test_materials_dataset_service_create_from_form(test_client):
    """Test MaterialsDatasetService.create_from_form() method"""
    from unittest.mock import Mock

    service = MaterialsDatasetService()

    # Create mock user
    mock_user = Mock()
    mock_user.id = 1
    mock_user.profile = Mock()
    mock_user.profile.name = "John"
    mock_user.profile.surname = "Doe"
    mock_user.profile.affiliation = "University"
    mock_user.profile.orcid = "0000-0001-2345-6789"

    # Create mock form
    mock_form = Mock()
    mock_form.get_dsmetadata.return_value = {
        "title": "Test Dataset",
        "description": "Test description",
        "publication_type": PublicationType.NONE,
    }
    mock_form.get_authors.return_value = []

    # Create dataset
    dataset = service.create_from_form(form=mock_form, current_user=mock_user)

    assert dataset is not None
    assert dataset.user_id == mock_user.id
    assert dataset.ds_meta_data is not None
    assert dataset.ds_meta_data.title == "Test Dataset"


# ============================================================================
# Tests for helper functions (regenerate_csv_for_dataset)
# ============================================================================


@pytest.mark.unit
def test_regenerate_csv_for_dataset_success(test_client):
    """Test regenerate_csv_for_dataset() creates CSV file correctly"""
    import os

    from app.modules.dataset.routes import regenerate_csv_for_dataset

    user = User(email="test_regenerate_csv@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    # Create some material records
    for i in range(3):
        record = MaterialRecord(
            materials_dataset_id=dataset.id,
            material_name=f"Material_{i}",
            property_name="density",
            property_value="100",
        )
        db.session.add(record)
    db.session.commit()

    # Generate CSV
    result = regenerate_csv_for_dataset(dataset.id)

    assert result is True
    assert dataset.csv_file_path is not None

    # Verify CSV file was created
    csv_path = dataset.csv_file_path
    if not os.path.isabs(csv_path):
        csv_path = os.path.abspath(csv_path)

    assert os.path.exists(csv_path)

    # Clean up
    if os.path.exists(csv_path):
        os.remove(csv_path)


@pytest.mark.unit
def test_regenerate_csv_for_dataset_not_found(test_client):
    """Test regenerate_csv_for_dataset() with non-existent dataset"""
    from app.modules.dataset.routes import regenerate_csv_for_dataset

    result = regenerate_csv_for_dataset(99999)

    assert result is False


#  ============================================================================
# Tests for MaterialRecord model methods
# ============================================================================


@pytest.mark.unit
def test_material_record_to_dict_with_data_source_enum(test_client):
    """Test MaterialRecord.to_dict() converts DataSource enum correctly"""
    user = User(email="test_material_record_enum@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    record = MaterialRecord(
        materials_dataset_id=dataset.id,
        material_name="Silicon",
        property_name="thermal_conductivity",
        property_value="148",
        data_source=DataSource.COMPUTATIONAL,
    )
    db.session.add(record)
    db.session.commit()

    result = record.to_dict()

    assert result["data_source"] == "computational"


@pytest.mark.unit
def test_material_record_to_dict_with_none_values(test_client):
    """Test MaterialRecord.to_dict() handles None values correctly"""
    user = User(email="test_material_record_none@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    record = MaterialRecord(
        materials_dataset_id=dataset.id,
        material_name="Silicon",
        property_name="density",
        property_value="2.33",
        chemical_formula=None,
        temperature=None,
        data_source=None,
    )
    db.session.add(record)
    db.session.commit()

    result = record.to_dict()

    assert result["chemical_formula"] is None
    assert result["temperature"] is None
    assert result["data_source"] is None


# ============================================================================
# Tests for calculate_checksum_and_size function
# ============================================================================


@pytest.mark.unit
def test_calculate_checksum_and_size_with_actual_content(test_client):
    """Test calculate_checksum_and_size() with specific content"""
    import hashlib
    import os

    # Create a file with known content
    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".txt") as f:
        content = b"Hello, World!"
        f.write(content)
        temp_path = f.name

    try:
        checksum, size = calculate_checksum_and_size(temp_path)

        # Verify checksum matches expected MD5
        expected_checksum = hashlib.md5(content).hexdigest()
        assert checksum == expected_checksum
        assert size == len(content)
    finally:
        os.unlink(temp_path)


# ============================================================================
# Tests for MaterialsDataset model methods
# ============================================================================


@pytest.mark.unit
def test_materials_dataset_to_dict(test_client):
    """Test MaterialsDataset.to_dict() method"""
    user = User(email="test_dataset_to_dict@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(
        title="Test Dataset",
        description="Test",
        publication_type=PublicationType.NONE,
        tags="materials, silicon",
    )
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id, csv_file_path="/path/to/file.csv")
    db.session.add(dataset)
    db.session.commit()

    record = MaterialRecord(
        materials_dataset_id=dataset.id, material_name="Silicon", property_name="density", property_value="2.33"
    )
    db.session.add(record)
    db.session.commit()

    # Use Flask application context for to_dict() which uses url_for and request
    with test_client.application.test_request_context():
        result = dataset.to_dict()

        assert result["id"] == dataset.id
        assert result["csv_file_path"] == "/path/to/file.csv"
        assert result["materials_count"] == 1


@pytest.mark.unit
def test_materials_dataset_get_records_count(test_client):
    """Test MaterialsDataset.get_materials_count() returns correct count"""
    user = User(email="test_records_count@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    # Add 5 records
    for i in range(5):
        record = MaterialRecord(
            materials_dataset_id=dataset.id,
            material_name=f"Material_{i}",
            property_name="density",
            property_value="100",
        )
        db.session.add(record)
    db.session.commit()

    assert dataset.get_materials_count() == 5


# ============================================================================
# Tests for Author model
# ============================================================================


@pytest.mark.unit
def test_author_to_dict(test_client):
    """Test Author.to_dict() method"""
    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    author = Author(
        name="John Doe",
        affiliation="University of Test",
        orcid="0000-0001-2345-6789",
        ds_meta_data_id=metadata.id,
    )
    db.session.add(author)
    db.session.commit()

    result = author.to_dict()

    assert result["name"] == "John Doe"
    assert result["affiliation"] == "University of Test"
    assert result["orcid"] == "0000-0001-2345-6789"


# ============================================================================
# Tests for DSViewRecordService.create_cookie()
# ============================================================================


@pytest.mark.unit
def test_ds_view_record_service_create_cookie_with_existing_cookie(test_client):
    """Test DSViewRecordService.create_cookie() with existing cookie"""
    from unittest.mock import Mock, patch

    user = User(email="test_create_cookie_existing@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    record = MaterialRecord(
        materials_dataset_id=dataset.id, material_name="Silicon", property_name="density", property_value="100"
    )
    db.session.add(record)
    db.session.commit()

    # Create existing view record with UUID format cookie (36 chars max)
    existing_cookie = "12345678-1234-5678-1234-567812345678"
    view_record = DSViewRecord(
        user_id=user.id, dataset_id=dataset.id, view_date=datetime.now(timezone.utc), view_cookie=existing_cookie
    )
    db.session.add(view_record)
    db.session.commit()

    # Mock current_user
    mock_user = Mock()
    mock_user.id = user.id
    mock_user.is_authenticated = True

    service = DSViewRecordService()

    # Mock request.cookies to return existing cookie
    with test_client.application.test_request_context():
        with patch("app.modules.dataset.repositories.current_user", mock_user):
            with patch("app.modules.dataset.services.request") as mock_request:
                # Properly mock cookies.get() method
                mock_cookies = Mock()
                mock_cookies.get = Mock(return_value=existing_cookie)
                mock_request.cookies = mock_cookies

                cookie = service.create_cookie(dataset)

    assert cookie == existing_cookie


# ============================================================================
# Tests for MaterialsDatasetService filter methods with empty datasets
# ============================================================================


@pytest.mark.unit
def test_materials_dataset_service_filter_by_authors_no_authors(test_client):
    """Test MaterialsDatasetService.filter_by_authors() with dataset without authors"""
    user = User(email="test_filter_no_authors@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    # Create dataset without authors
    metadata = DSMetaData(title="Dataset 1", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    record = MaterialRecord(
        materials_dataset_id=dataset.id, material_name="Silicon", property_name="density", property_value="100"
    )
    db.session.add(record)
    db.session.commit()

    service = MaterialsDatasetService()
    filtered = service.filter_by_authors([], dataset)

    assert filtered == []


@pytest.mark.unit
def test_materials_dataset_service_filter_by_tags_no_tags(test_client):
    """Test MaterialsDatasetService.filter_by_tags() with dataset without tags"""
    user = User(email="test_filter_no_tags@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    # Create dataset without tags
    metadata = DSMetaData(title="Dataset 1", description="Test", publication_type=PublicationType.NONE, tags=None)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    record = MaterialRecord(
        materials_dataset_id=dataset.id, material_name="Silicon", property_name="density", property_value="100"
    )
    db.session.add(record)
    db.session.commit()

    service = MaterialsDatasetService()
    filtered = service.filter_by_tags([], dataset)

    assert filtered == []


@pytest.mark.unit
def test_materials_dataset_service_filter_by_properties_no_properties(test_client):
    """Test MaterialsDatasetService.filter_by_properties() with dataset without properties"""
    user = User(email="test_filter_no_properties@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    # Create dataset without any material records (no properties)
    metadata = DSMetaData(title="Dataset 1", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id)
    db.session.add(dataset)
    db.session.commit()

    service = MaterialsDatasetService()
    filtered = service.filter_by_properties([], dataset)

    assert filtered == []


# ============================================================================
# Tests for MaterialsDatasetService error handling and edge cases
# ============================================================================


@pytest.mark.unit
def test_materials_dataset_service_parse_csv_row_missing_material_name(test_client):
    """Test _parse_csv_row raises ValueError when material_name is missing"""
    service = MaterialsDatasetService()

    # Row without material_name
    row = {"property_name": "density", "property_value": "2.5"}

    with pytest.raises(ValueError, match="material_name is required"):
        service._parse_csv_row(row, row_num=1)


@pytest.mark.unit
def test_materials_dataset_service_parse_csv_row_missing_property_name(test_client):
    """Test _parse_csv_row raises ValueError when property_name is missing"""
    service = MaterialsDatasetService()

    # Row without property_name
    row = {"material_name": "Gold", "property_value": "2.5"}

    with pytest.raises(ValueError, match="property_name is required"):
        service._parse_csv_row(row, row_num=1)


@pytest.mark.unit
def test_materials_dataset_service_parse_csv_row_missing_property_value(test_client):
    """Test _parse_csv_row raises ValueError when property_value is missing"""
    service = MaterialsDatasetService()

    # Row without property_value
    row = {"material_name": "Gold", "property_name": "density"}

    with pytest.raises(ValueError, match="property_value is required"):
        service._parse_csv_row(row, row_num=1)


@pytest.mark.unit
def test_materials_dataset_service_parse_csv_row_invalid_temperature(test_client):
    """Test _parse_csv_row handles invalid temperature value"""
    service = MaterialsDatasetService()

    # Row with invalid temperature
    row = {"material_name": "Gold", "property_name": "density", "property_value": "2.5", "temperature": "invalid"}

    result = service._parse_csv_row(row, row_num=1)

    assert result["temperature"] is None
    assert result["material_name"] == "Gold"


@pytest.mark.unit
def test_materials_dataset_service_parse_csv_row_invalid_pressure(test_client):
    """Test _parse_csv_row handles invalid pressure value"""
    service = MaterialsDatasetService()

    # Row with invalid pressure
    row = {"material_name": "Gold", "property_name": "density", "property_value": "2.5", "pressure": "not_a_number"}

    result = service._parse_csv_row(row, row_num=1)

    assert result["pressure"] is None
    assert result["material_name"] == "Gold"


@pytest.mark.unit
def test_materials_dataset_service_parse_csv_row_invalid_uncertainty(test_client):
    """Test _parse_csv_row handles invalid uncertainty value"""
    service = MaterialsDatasetService()

    # Row with invalid uncertainty
    row = {"material_name": "Gold", "property_name": "density", "property_value": "2.5", "uncertainty": "abc"}

    result = service._parse_csv_row(row, row_num=1)

    assert result["uncertainty"] is None
    assert result["material_name"] == "Gold"


@pytest.mark.unit
def test_materials_dataset_service_parse_csv_file_encoding_error(test_client):
    """Test parse_csv_file handles UnicodeDecodeError"""
    import tempfile

    service = MaterialsDatasetService()

    # Create a file with invalid encoding
    with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".csv") as f:
        # Write invalid UTF-8 bytes
        f.write(b"\xff\xfe\xff\xfe")
        temp_path = f.name

    try:
        result = service.parse_csv_file(temp_path, encoding="utf-8")

        assert result["success"] is False
        assert "Encoding error" in result["error"]
    finally:
        import os

        os.unlink(temp_path)


@pytest.mark.unit
def test_materials_dataset_service_parse_csv_file_with_invalid_row(test_client):
    """Test parse_csv_file skips invalid rows and continues"""
    import tempfile

    service = MaterialsDatasetService()

    # Create CSV with one invalid and one valid row
    csv_content = """material_name,property_name,property_value
Gold,density,19.3
,density,10.5
Silver,density,10.5"""

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", newline="") as f:
        f.write(csv_content)
        temp_path = f.name

    try:
        result = service.parse_csv_file(temp_path)

        assert result["success"] is True
        assert result["rows_parsed"] == 2  # Only 2 valid rows (invalid one skipped)
        assert len(result["data"]) == 2
    finally:
        import os

        os.unlink(temp_path)


@pytest.mark.unit
def test_materials_dataset_service_get_recommendations_nonexistent_dataset(test_client):
    """Test get_recommendations returns empty list for nonexistent dataset"""
    service = MaterialsDatasetService()

    recommendations = service.get_recommendations(materials_dataset_id=999999, limit=3)

    assert recommendations == []


# ============================================================================
# Tests for Dataset Versioning - DatasetVersion Model
# ============================================================================


@pytest.mark.unit
def test_dataset_version_to_dict(test_client):
    """Test DatasetVersion.to_dict() method"""
    user = User(email="test_version_to_dict@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test Dataset", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id, csv_file_path="/path/to/file.csv")
    db.session.add(dataset)
    db.session.commit()

    # Create a version
    version = DatasetVersion(
        materials_dataset_id=dataset.id,
        version_number=1,
        created_by_user_id=user.id,
        csv_snapshot_path="/path/to/snapshot_v1.csv",
        metadata_snapshot={"title": "Test Dataset", "description": "Test"},
        changelog={"action": "Created dataset"},
        records_count=10,
    )
    db.session.add(version)
    db.session.commit()

    result = version.to_dict()

    assert result["id"] == version.id
    assert result["version_number"] == 1
    assert result["records_count"] == 10
    assert result["changelog"] == {"action": "Created dataset"}
    assert "created_at" in result
    assert "created_at_timestamp" in result


@pytest.mark.unit
def test_dataset_version_relationship_with_dataset(test_client):
    """Test DatasetVersion relationship with MaterialsDataset"""
    user = User(email="test_version_relationship@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id, csv_file_path="/path/to/file.csv")
    db.session.add(dataset)
    db.session.commit()

    # Create two versions
    for i in range(1, 3):
        version = DatasetVersion(
            materials_dataset_id=dataset.id,
            version_number=i,
            created_by_user_id=user.id,
            csv_snapshot_path=f"/path/to/snapshot_v{i}.csv",
            metadata_snapshot={"title": "Test"},
            records_count=10,
        )
        db.session.add(version)
    db.session.commit()

    # Verify relationship
    assert len(dataset.versions) == 2
    assert dataset.versions[0].version_number == 2  # Ordered DESC
    assert dataset.versions[1].version_number == 1


@pytest.mark.unit
def test_dataset_version_cascade_delete(test_client):
    """Test that deleting a dataset deletes its versions"""
    user = User(email="test_version_cascade@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id, csv_file_path="/path/to/file.csv")
    db.session.add(dataset)
    db.session.commit()

    version = DatasetVersion(
        materials_dataset_id=dataset.id,
        version_number=1,
        created_by_user_id=user.id,
        csv_snapshot_path="/path/to/snapshot.csv",
        metadata_snapshot={"title": "Test"},
        records_count=10,
    )
    db.session.add(version)
    db.session.commit()

    version_id = version.id

    # Delete dataset
    db.session.delete(dataset)
    db.session.commit()

    # Verify version was also deleted
    deleted_version = DatasetVersion.query.get(version_id)
    assert deleted_version is None


# ============================================================================
# Tests for DatasetVersionRepository
# ============================================================================


@pytest.mark.unit
def test_dataset_version_repository_get_by_dataset(test_client):
    """Test DatasetVersionRepository.get_by_dataset() method"""
    user = User(email="test_version_repo_get@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id, csv_file_path="/path/to/file.csv")
    db.session.add(dataset)
    db.session.commit()

    # Create 3 versions
    for i in range(1, 4):
        version = DatasetVersion(
            materials_dataset_id=dataset.id,
            version_number=i,
            created_by_user_id=user.id,
            csv_snapshot_path=f"/path/to/snapshot_v{i}.csv",
            metadata_snapshot={"title": "Test"},
            records_count=10,
        )
        db.session.add(version)
    db.session.commit()

    repo = DatasetVersionRepository()
    versions = repo.get_by_dataset(dataset.id)

    assert len(versions) == 3
    assert versions[0].version_number == 3  # Ordered DESC
    assert versions[1].version_number == 2
    assert versions[2].version_number == 1


@pytest.mark.unit
def test_dataset_version_repository_get_next_version_number(test_client):
    """Test DatasetVersionRepository.get_next_version_number() method"""
    user = User(email="test_next_version_num@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id, csv_file_path="/path/to/file.csv")
    db.session.add(dataset)
    db.session.commit()

    repo = DatasetVersionRepository()

    # No versions yet - should return 1
    next_version = repo.get_next_version_number(dataset.id)
    assert next_version == 1

    # Create version 1
    version1 = DatasetVersion(
        materials_dataset_id=dataset.id,
        version_number=1,
        created_by_user_id=user.id,
        csv_snapshot_path="/path/to/snapshot_v1.csv",
        metadata_snapshot={"title": "Test"},
        records_count=10,
    )
    db.session.add(version1)
    db.session.commit()

    # Should now return 2
    next_version = repo.get_next_version_number(dataset.id)
    assert next_version == 2

    # Create version 2
    version2 = DatasetVersion(
        materials_dataset_id=dataset.id,
        version_number=2,
        created_by_user_id=user.id,
        csv_snapshot_path="/path/to/snapshot_v2.csv",
        metadata_snapshot={"title": "Test"},
        records_count=15,
    )
    db.session.add(version2)
    db.session.commit()

    # Should now return 3
    next_version = repo.get_next_version_number(dataset.id)
    assert next_version == 3


@pytest.mark.unit
def test_dataset_version_repository_get_latest_version(test_client):
    """Test DatasetVersionRepository.get_latest_version() method"""
    user = User(email="test_latest_version@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id, csv_file_path="/path/to/file.csv")
    db.session.add(dataset)
    db.session.commit()

    repo = DatasetVersionRepository()

    # No versions yet
    latest = repo.get_latest_version(dataset.id)
    assert latest is None

    # Create versions 1, 2, 3
    for i in range(1, 4):
        version = DatasetVersion(
            materials_dataset_id=dataset.id,
            version_number=i,
            created_by_user_id=user.id,
            csv_snapshot_path=f"/path/to/snapshot_v{i}.csv",
            metadata_snapshot={"title": "Test"},
            records_count=10 + i,
        )
        db.session.add(version)
    db.session.commit()

    # Should return version 3
    latest = repo.get_latest_version(dataset.id)
    assert latest is not None
    assert latest.version_number == 3
    assert latest.records_count == 13


@pytest.mark.unit
def test_dataset_version_repository_get_by_version_number(test_client):
    """Test DatasetVersionRepository.get_by_version_number() method"""
    user = User(email="test_get_by_version_num@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id, csv_file_path="/path/to/file.csv")
    db.session.add(dataset)
    db.session.commit()

    # Create version 2 (intentionally skip 1)
    version2 = DatasetVersion(
        materials_dataset_id=dataset.id,
        version_number=2,
        created_by_user_id=user.id,
        csv_snapshot_path="/path/to/snapshot_v2.csv",
        metadata_snapshot={"title": "Test"},
        records_count=20,
    )
    db.session.add(version2)
    db.session.commit()

    repo = DatasetVersionRepository()

    # Get version 2
    version = repo.get_version_by_number(dataset.id, 2)
    assert version is not None
    assert version.version_number == 2
    assert version.records_count == 20

    # Try to get non-existent version 1
    version = repo.get_version_by_number(dataset.id, 1)
    assert version is None


# ============================================================================
# Tests for DatasetVersionService
# ============================================================================


@pytest.mark.unit
def test_dataset_version_service_list_versions(test_client):
    """Test DatasetVersionService.list_versions() method"""
    user = User(email="test_service_list_versions@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id, csv_file_path="/path/to/file.csv")
    db.session.add(dataset)
    db.session.commit()

    # Create 2 versions
    for i in range(1, 3):
        version = DatasetVersion(
            materials_dataset_id=dataset.id,
            version_number=i,
            created_by_user_id=user.id,
            csv_snapshot_path=f"/path/to/snapshot_v{i}.csv",
            metadata_snapshot={"title": "Test"},
            records_count=10 + i,
        )
        db.session.add(version)
    db.session.commit()

    service = DatasetVersionService()
    versions = service.list_versions(dataset.id)

    assert len(versions) == 2
    assert versions[0].version_number == 2  # DESC order
    assert versions[1].version_number == 1


@pytest.mark.unit
def test_dataset_version_service_compare_metadata(test_client):
    """Test DatasetVersionService.compare_metadata() method"""
    user = User(email="test_compare_metadata@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id, csv_file_path="/path/to/file.csv")
    db.session.add(dataset)
    db.session.commit()

    # Create version 1 with original metadata
    version1 = DatasetVersion(
        materials_dataset_id=dataset.id,
        version_number=1,
        created_by_user_id=user.id,
        csv_snapshot_path="/path/to/snapshot_v1.csv",
        metadata_snapshot={"title": "Original Title", "description": "Original Description", "tags": "tag1,tag2"},
        records_count=10,
    )
    db.session.add(version1)

    # Create version 2 with modified metadata
    version2 = DatasetVersion(
        materials_dataset_id=dataset.id,
        version_number=2,
        created_by_user_id=user.id,
        csv_snapshot_path="/path/to/snapshot_v2.csv",
        metadata_snapshot={"title": "Updated Title", "description": "Original Description", "tags": "tag1,tag3"},
        records_count=12,
    )
    db.session.add(version2)
    db.session.commit()

    service = DatasetVersionService()
    comparison = service.compare_metadata(version1.id, version2.id)

    # Title should be changed
    assert comparison["title"]["old"] == "Original Title"
    assert comparison["title"]["new"] == "Updated Title"
    assert comparison["title"]["changed"] is True

    # Description should be unchanged
    assert comparison["description"]["old"] == "Original Description"
    assert comparison["description"]["new"] == "Original Description"
    assert comparison["description"]["changed"] is False

    # Tags should be changed
    assert comparison["tags"]["changed"] is True


@pytest.mark.unit
def test_dataset_version_service_compare_files(test_client):
    """Test DatasetVersionService.compare_files() method"""
    import csv
    import os

    user = User(email="test_compare_files@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id, csv_file_path="/path/to/file.csv")
    db.session.add(dataset)
    db.session.commit()

    # Create temporary CSV files for version 1
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix="_v1.csv", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["material_name", "property_name", "property_value"])
        writer.writerow(["Silicon", "density", "2.33"])
        writer.writerow(["Aluminum", "density", "2.70"])
        csv_path_v1 = f.name

    # Create temporary CSV files for version 2 (modified Aluminum, added Copper, removed Silicon)
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix="_v2.csv", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["material_name", "property_name", "property_value"])
        writer.writerow(["Aluminum", "density", "2.75"])  # Modified value
        writer.writerow(["Copper", "density", "8.96"])  # Added
        csv_path_v2 = f.name

    try:
        # Create versions with these CSV files
        version1 = DatasetVersion(
            materials_dataset_id=dataset.id,
            version_number=1,
            created_by_user_id=user.id,
            csv_snapshot_path=csv_path_v1,
            metadata_snapshot={"title": "Test"},
            records_count=2,
        )
        db.session.add(version1)

        version2 = DatasetVersion(
            materials_dataset_id=dataset.id,
            version_number=2,
            created_by_user_id=user.id,
            csv_snapshot_path=csv_path_v2,
            metadata_snapshot={"title": "Test"},
            records_count=2,
        )
        db.session.add(version2)
        db.session.commit()

        service = DatasetVersionService()
        comparison = service.compare_files(version1.id, version2.id)

        # Verify comparison results
        assert len(comparison["added_records"]) == 1  # Copper added
        assert comparison["added_records"][0]["material_name"] == "Copper"

        assert len(comparison["deleted_records"]) == 1  # Silicon removed
        assert comparison["deleted_records"][0]["material_name"] == "Silicon"

        assert len(comparison["modified_records"]) == 1  # Aluminum modified
        assert comparison["modified_records"][0]["old"]["material_name"] == "Aluminum"
        assert comparison["modified_records"][0]["new"]["material_name"] == "Aluminum"

    finally:
        # Clean up temporary files
        if os.path.exists(csv_path_v1):
            os.unlink(csv_path_v1)
        if os.path.exists(csv_path_v2):
            os.unlink(csv_path_v2)


@pytest.mark.unit
def test_dataset_version_service_get_csv_diff(test_client):
    """Test DatasetVersionService.get_csv_diff() method"""
    import csv
    import os

    user = User(email="test_get_csv_diff@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id, csv_file_path="/path/to/file.csv")
    db.session.add(dataset)
    db.session.commit()

    # Create temporary CSV files
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix="_v1.csv", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["material_name", "property_name", "property_value"])
        writer.writerow(["Silicon", "density", "2.33"])
        csv_path_v1 = f.name

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix="_v2.csv", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["material_name", "property_name", "property_value"])
        writer.writerow(["Silicon", "density", "2.35"])  # Modified value
        csv_path_v2 = f.name

    try:
        version1 = DatasetVersion(
            materials_dataset_id=dataset.id,
            version_number=1,
            created_by_user_id=user.id,
            csv_snapshot_path=csv_path_v1,
            metadata_snapshot={"title": "Test"},
            records_count=1,
        )
        db.session.add(version1)

        version2 = DatasetVersion(
            materials_dataset_id=dataset.id,
            version_number=2,
            created_by_user_id=user.id,
            csv_snapshot_path=csv_path_v2,
            metadata_snapshot={"title": "Test"},
            records_count=1,
        )
        db.session.add(version2)
        db.session.commit()

        service = DatasetVersionService()
        diff = service.get_csv_diff(version1.id, version2.id)

        # Verify diff contains the change
        assert diff is not None
        assert isinstance(diff, str)
        assert "2.33" in diff or "2.35" in diff  # Should contain the changed values

    finally:
        # Clean up
        if os.path.exists(csv_path_v1):
            os.unlink(csv_path_v1)
        if os.path.exists(csv_path_v2):
            os.unlink(csv_path_v2)


@pytest.mark.unit
def test_dataset_version_service_compare_files_no_changes(test_client):
    """Test DatasetVersionService.compare_files() with identical files"""
    import csv
    import os

    user = User(email="test_compare_no_changes@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    metadata = DSMetaData(title="Test", description="Test", publication_type=PublicationType.NONE)
    db.session.add(metadata)
    db.session.commit()

    dataset = MaterialsDataset(user_id=user.id, ds_meta_data_id=metadata.id, csv_file_path="/path/to/file.csv")
    db.session.add(dataset)
    db.session.commit()

    # Create identical CSV files
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix="_v1.csv", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["material_name", "property_name", "property_value"])
        writer.writerow(["Silicon", "density", "2.33"])
        csv_path_v1 = f.name

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix="_v2.csv", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["material_name", "property_name", "property_value"])
        writer.writerow(["Silicon", "density", "2.33"])
        csv_path_v2 = f.name

    try:
        version1 = DatasetVersion(
            materials_dataset_id=dataset.id,
            version_number=1,
            created_by_user_id=user.id,
            csv_snapshot_path=csv_path_v1,
            metadata_snapshot={"title": "Test"},
            records_count=1,
        )
        db.session.add(version1)

        version2 = DatasetVersion(
            materials_dataset_id=dataset.id,
            version_number=2,
            created_by_user_id=user.id,
            csv_snapshot_path=csv_path_v2,
            metadata_snapshot={"title": "Test"},
            records_count=1,
        )
        db.session.add(version2)
        db.session.commit()

        service = DatasetVersionService()
        comparison = service.compare_files(version1.id, version2.id)

        # No changes
        assert len(comparison["added_records"]) == 0
        assert len(comparison["deleted_records"]) == 0
        assert len(comparison["modified_records"]) == 0
        assert comparison["unchanged_records_count"] == 1

    finally:
        # Clean up
        if os.path.exists(csv_path_v1):
            os.unlink(csv_path_v1)
        if os.path.exists(csv_path_v2):
            os.unlink(csv_path_v2)
