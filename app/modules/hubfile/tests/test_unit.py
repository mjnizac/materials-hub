"""
Unit tests for hubfile module.
"""
<<<<<<< HEAD

import pytest

from app import db
from app.modules.dataset.models import PublicationType
from app.modules.featuremodel.models import FeatureModel, FMMetaData
from app.modules.hubfile.models import (
    Hubfile,
    HubfileDownloadRecord,
    HubfileViewRecord,
)
from app.modules.hubfile.repositories import (
    HubfileDownloadRecordRepository,
    HubfileRepository,
    HubfileViewRecordRepository,
)
from app.modules.hubfile.services import (
    HubfileDownloadRecordService,
    HubfileService,
)
=======
>>>>>>> feature/tests-selenium

# ===========================
# Hubfile Model Tests
# ===========================


@pytest.mark.unit
def test_hubfile_creation(test_client):
    """Test Hubfile can be created and saved"""
    # Create feature model first
    fm_metadata = FMMetaData(
        uvl_filename="test.uvl",
        title="Test Feature Model",
        description="Test description",
        publication_type=PublicationType.NONE,
    )
    db.session.add(fm_metadata)
    db.session.commit()

    feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
    db.session.add(feature_model)
    db.session.commit()

    # Create hubfile
    hubfile = Hubfile(
        name="test_file.uvl",
        checksum="abc123",
        size=1024,
        feature_model_id=feature_model.id,
    )
    db.session.add(hubfile)
    db.session.commit()

    assert hubfile.id is not None
    assert hubfile.name == "test_file.uvl"
    assert hubfile.checksum == "abc123"
    assert hubfile.size == 1024


@pytest.mark.unit
def test_hubfile_repr(test_client):
    """Test Hubfile __repr__ method"""
    fm_metadata = FMMetaData(
        uvl_filename="test.uvl", title="Test", description="Test", publication_type=PublicationType.NONE
    )
    db.session.add(fm_metadata)
    db.session.commit()

    feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
    db.session.add(feature_model)
    db.session.commit()

    hubfile = Hubfile(name="test.uvl", checksum="abc123", size=1024, feature_model_id=feature_model.id)
    db.session.add(hubfile)
    db.session.commit()

    assert repr(hubfile) == f"File<{hubfile.id}>"


@pytest.mark.unit
def test_hubfile_get_formatted_size(test_client):
    """Test Hubfile get_formatted_size method"""
    fm_metadata = FMMetaData(
        uvl_filename="test.uvl", title="Test", description="Test", publication_type=PublicationType.NONE
    )
    db.session.add(fm_metadata)
    db.session.commit()

    feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
    db.session.add(feature_model)
    db.session.commit()

    hubfile = Hubfile(name="test.uvl", checksum="abc123", size=1024, feature_model_id=feature_model.id)
    db.session.add(hubfile)
    db.session.commit()

    formatted_size = hubfile.get_formatted_size()
    assert formatted_size is not None
    assert isinstance(formatted_size, str)


@pytest.mark.unit
def test_hubfile_to_dict(test_client):
    """Test Hubfile to_dict method"""
    fm_metadata = FMMetaData(
        uvl_filename="test.uvl", title="Test", description="Test", publication_type=PublicationType.NONE
    )
    db.session.add(fm_metadata)
    db.session.commit()

    feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
    db.session.add(feature_model)
    db.session.commit()

    hubfile = Hubfile(name="test.uvl", checksum="abc123", size=1024, feature_model_id=feature_model.id)
    db.session.add(hubfile)
    db.session.commit()

    with test_client.application.test_request_context():
        hubfile_dict = hubfile.to_dict()

    assert hubfile_dict["id"] == hubfile.id
    assert hubfile_dict["name"] == "test.uvl"
    assert hubfile_dict["checksum"] == "abc123"
    assert hubfile_dict["size_in_bytes"] == 1024
    assert "size_in_human_format" in hubfile_dict
    assert "url" in hubfile_dict


# ===========================
# HubfileViewRecord Model Tests
# ===========================


@pytest.mark.unit
def test_hubfile_view_record_creation(test_client):
    """Test HubfileViewRecord can be created and saved"""
    fm_metadata = FMMetaData(
        uvl_filename="test.uvl", title="Test", description="Test", publication_type=PublicationType.NONE
    )
    db.session.add(fm_metadata)
    db.session.commit()

    feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
    db.session.add(feature_model)
    db.session.commit()

    hubfile = Hubfile(name="test.uvl", checksum="abc123", size=1024, feature_model_id=feature_model.id)
    db.session.add(hubfile)
    db.session.commit()

    view_record = HubfileViewRecord(file_id=hubfile.id, view_cookie="test-cookie-123")
    db.session.add(view_record)
    db.session.commit()

    assert view_record.id is not None
    assert view_record.file_id == hubfile.id
    assert view_record.view_cookie == "test-cookie-123"
    assert view_record.view_date is not None


@pytest.mark.unit
def test_hubfile_view_record_repr(test_client):
    """Test HubfileViewRecord __repr__ method"""
    fm_metadata = FMMetaData(
        uvl_filename="test.uvl", title="Test", description="Test", publication_type=PublicationType.NONE
    )
    db.session.add(fm_metadata)
    db.session.commit()

    feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
    db.session.add(feature_model)
    db.session.commit()

    hubfile = Hubfile(name="test.uvl", checksum="abc123", size=1024, feature_model_id=feature_model.id)
    db.session.add(hubfile)
    db.session.commit()

    view_record = HubfileViewRecord(file_id=hubfile.id)
    db.session.add(view_record)
    db.session.commit()

    assert repr(view_record) == f"<FileViewRecord {view_record.id}>"


# ===========================
# HubfileDownloadRecord Model Tests
# ===========================


@pytest.mark.unit
def test_hubfile_download_record_creation(test_client):
    """Test HubfileDownloadRecord can be created and saved"""
    fm_metadata = FMMetaData(
        uvl_filename="test.uvl", title="Test", description="Test", publication_type=PublicationType.NONE
    )
    db.session.add(fm_metadata)
    db.session.commit()

    feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
    db.session.add(feature_model)
    db.session.commit()

    hubfile = Hubfile(name="test.uvl", checksum="abc123", size=1024, feature_model_id=feature_model.id)
    db.session.add(hubfile)
    db.session.commit()

    download_record = HubfileDownloadRecord(file_id=hubfile.id, download_cookie="download-cookie-456")
    db.session.add(download_record)
    db.session.commit()

    assert download_record.id is not None
    assert download_record.file_id == hubfile.id
    assert download_record.download_cookie == "download-cookie-456"
    assert download_record.download_date is not None


@pytest.mark.unit
def test_hubfile_download_record_repr(test_client):
    """Test HubfileDownloadRecord __repr__ method"""
    fm_metadata = FMMetaData(
        uvl_filename="test.uvl", title="Test", description="Test", publication_type=PublicationType.NONE
    )
    db.session.add(fm_metadata)
    db.session.commit()

    feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
    db.session.add(feature_model)
    db.session.commit()

    hubfile = Hubfile(name="test.uvl", checksum="abc123", size=1024, feature_model_id=feature_model.id)
    db.session.add(hubfile)
    db.session.commit()

    download_record = HubfileDownloadRecord(file_id=hubfile.id, download_cookie="test-cookie")
    db.session.add(download_record)
    db.session.commit()

    repr_string = repr(download_record)
    assert "<FileDownload id=" in repr_string
    assert f"file_id={hubfile.id}" in repr_string
    assert "cookie=test-cookie" in repr_string


# ===========================
# HubfileRepository Tests
# ===========================


@pytest.mark.unit
def test_hubfile_repository_initialization():
    """Test HubfileRepository initializes correctly"""
    repository = HubfileRepository()
    assert repository is not None
    assert repository.model == Hubfile


# ===========================
# HubfileViewRecordRepository Tests
# ===========================


@pytest.mark.unit
def test_hubfile_view_record_repository_initialization():
    """Test HubfileViewRecordRepository initializes correctly"""
    repository = HubfileViewRecordRepository()
    assert repository is not None
    assert repository.model == HubfileViewRecord


@pytest.mark.unit
def test_hubfile_view_record_repository_total_hubfile_views(test_client):
    """Test total_hubfile_views method"""
    repository = HubfileViewRecordRepository()

    initial_count = repository.total_hubfile_views()

    # Create view records
    fm_metadata = FMMetaData(
        uvl_filename="test.uvl", title="Test", description="Test", publication_type=PublicationType.NONE
    )
    db.session.add(fm_metadata)
    db.session.commit()

    feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
    db.session.add(feature_model)
    db.session.commit()

    hubfile = Hubfile(name="test.uvl", checksum="abc123", size=1024, feature_model_id=feature_model.id)
    db.session.add(hubfile)
    db.session.commit()

    for i in range(3):
        view_record = HubfileViewRecord(file_id=hubfile.id, view_cookie=f"cookie-{i}")
        db.session.add(view_record)
        db.session.commit()

    final_count = repository.total_hubfile_views()
    assert final_count >= initial_count + 3


# ===========================
# HubfileDownloadRecordRepository Tests
# ===========================


@pytest.mark.unit
def test_hubfile_download_record_repository_initialization():
    """Test HubfileDownloadRecordRepository initializes correctly"""
    repository = HubfileDownloadRecordRepository()
    assert repository is not None
    assert repository.model == HubfileDownloadRecord


@pytest.mark.unit
def test_hubfile_download_record_repository_total_hubfile_downloads(test_client):
    """Test total_hubfile_downloads method"""
    repository = HubfileDownloadRecordRepository()

    initial_count = repository.total_hubfile_downloads()

    # Create download records
    fm_metadata = FMMetaData(
        uvl_filename="test.uvl", title="Test", description="Test", publication_type=PublicationType.NONE
    )
    db.session.add(fm_metadata)
    db.session.commit()

    feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
    db.session.add(feature_model)
    db.session.commit()

    hubfile = Hubfile(name="test.uvl", checksum="abc123", size=1024, feature_model_id=feature_model.id)
    db.session.add(hubfile)
    db.session.commit()

    for i in range(3):
        download_record = HubfileDownloadRecord(file_id=hubfile.id, download_cookie=f"download-{i}")
        db.session.add(download_record)
        db.session.commit()

    final_count = repository.total_hubfile_downloads()
    assert final_count >= initial_count + 3


# ===========================
# HubfileService Tests
# ===========================


@pytest.mark.unit
def test_hubfile_service_initialization():
    """Test HubfileService initializes correctly"""
    service = HubfileService()
    assert service is not None
    assert isinstance(service.repository, HubfileRepository)


@pytest.mark.unit
def test_hubfile_service_total_hubfile_views(test_client):
    """Test HubfileService total_hubfile_views method"""
    service = HubfileService()

    initial_count = service.total_hubfile_views()

    # Create a view record
    fm_metadata = FMMetaData(
        uvl_filename="test.uvl", title="Test", description="Test", publication_type=PublicationType.NONE
    )
    db.session.add(fm_metadata)
    db.session.commit()

    feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
    db.session.add(feature_model)
    db.session.commit()

    hubfile = Hubfile(name="test.uvl", checksum="abc123", size=1024, feature_model_id=feature_model.id)
    db.session.add(hubfile)
    db.session.commit()

    view_record = HubfileViewRecord(file_id=hubfile.id, view_cookie="service-test")
    db.session.add(view_record)
    db.session.commit()

    final_count = service.total_hubfile_views()
    assert final_count >= initial_count + 1


@pytest.mark.unit
def test_hubfile_service_total_hubfile_downloads(test_client):
    """Test HubfileService total_hubfile_downloads method"""
    service = HubfileService()

    initial_count = service.total_hubfile_downloads()

    # Create a download record
    fm_metadata = FMMetaData(
        uvl_filename="test.uvl", title="Test", description="Test", publication_type=PublicationType.NONE
    )
    db.session.add(fm_metadata)
    db.session.commit()

    feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
    db.session.add(feature_model)
    db.session.commit()

    hubfile = Hubfile(name="test.uvl", checksum="abc123", size=1024, feature_model_id=feature_model.id)
    db.session.add(hubfile)
    db.session.commit()

    download_record = HubfileDownloadRecord(file_id=hubfile.id, download_cookie="download-test")
    db.session.add(download_record)
    db.session.commit()

    final_count = service.total_hubfile_downloads()
    assert final_count >= initial_count + 1


# ===========================
# HubfileDownloadRecordService Tests
# ===========================


@pytest.mark.unit
def test_hubfile_download_record_service_initialization():
    """Test HubfileDownloadRecordService initializes correctly"""
    service = HubfileDownloadRecordService()
    assert service is not None
    assert isinstance(service.repository, HubfileDownloadRecordRepository)
