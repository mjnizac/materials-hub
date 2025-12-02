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
    DOIMapping,
    DSDownloadRecord,
    DSMetaData,
    DSViewRecord,
    DataSource,
    MaterialRecord,
    MaterialsDataset,
    PublicationType,
)
from app.modules.dataset.repositories import (
    AuthorRepository,
    DSDownloadRecordRepository,
    DSMetaDataRepository,
    DSViewRecordRepository,
    MaterialRecordRepository,
    MaterialsDatasetRepository,
)
from app.modules.dataset.services import (
    AuthorService,
    DOIMappingService,
    DSDownloadRecordService,
    DSMetaDataService,
    DSViewRecordService,
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
