"""
Unit tests for fakenodo module.
"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from app import db
from app.modules.fakenodo.models import Deposition
from app.modules.fakenodo.repositories import DepositionRepository
from app.modules.fakenodo.services import FakenodoService, calculate_checksum


@pytest.mark.unit
def test_deposition_model_creation(test_client):
    """Test creating a Deposition model instance."""
    metadata = {
        "title": "Test Dataset",
        "description": "Test description",
        "upload_type": "dataset",
    }

    deposition = Deposition(dep_metadata=metadata, status="draft")
    db.session.add(deposition)
    db.session.commit()

    assert deposition.id is not None
    assert deposition.dep_metadata == metadata
    assert deposition.status == "draft"
    assert deposition.doi is None
    assert repr(deposition) == f"Deposition<{deposition.id}>"


@pytest.mark.unit
def test_deposition_repository_initialization(test_client):
    """Test DepositionRepository initialization."""
    repository = DepositionRepository()
    assert repository.model == Deposition


@pytest.mark.unit
def test_deposition_repository_create_new_deposition(test_client):
    """Test creating a new deposition through repository."""
    repository = DepositionRepository()
    metadata = {
        "title": "Test Dataset",
        "description": "Test description",
        "upload_type": "dataset",
    }

    deposition = repository.create_new_deposition(dep_metadata=metadata)

    assert deposition.id is not None
    assert deposition.dep_metadata == metadata
    assert deposition.status == "draft"


@pytest.mark.unit
def test_fakenodo_service_initialization(test_client):
    """Test FakenodoService initialization."""
    service = FakenodoService()
    assert isinstance(service.deposition_repository, DepositionRepository)


@pytest.mark.unit
def test_fakenodo_service_create_new_deposition(test_client):
    """Test creating a new deposition through service."""
    service = FakenodoService()

    # Mock dataset with metadata
    mock_dataset = Mock()
    mock_dataset.ds_meta_data.title = "Test Dataset"
    mock_dataset.ds_meta_data.description = "Test description"
    mock_dataset.ds_meta_data.publication_type.value = "none"
    mock_dataset.ds_meta_data.tags = "tag1, tag2"

    # Mock authors
    mock_author = Mock()
    mock_author.name = "John Doe"
    mock_author.affiliation = "Test University"
    mock_author.orcid = "0000-0000-0000-0000"
    mock_dataset.ds_meta_data.authors = [mock_author]

    result = service.create_new_deposition(mock_dataset)

    assert "id" in result
    assert "metadata" in result
    assert "conceptrecid" in result
    assert result["metadata"]["title"] == "Test Dataset"
    assert result["metadata"]["description"] == "Test description"
    assert result["metadata"]["upload_type"] == "dataset"
    assert result["metadata"]["creators"][0]["name"] == "John Doe"
    assert "uvlhub" in result["metadata"]["keywords"]


@pytest.mark.unit
def test_fakenodo_service_create_new_deposition_publication_type(test_client):
    """Test creating a new deposition with publication type."""
    service = FakenodoService()

    # Mock dataset with publication type
    mock_dataset = Mock()
    mock_dataset.ds_meta_data.title = "Test Publication"
    mock_dataset.ds_meta_data.description = "Test description"
    mock_dataset.ds_meta_data.publication_type.value = "article"
    mock_dataset.ds_meta_data.tags = ""

    # Mock authors without optional fields
    mock_author = Mock()
    mock_author.name = "Jane Doe"
    mock_author.affiliation = None
    mock_author.orcid = None
    mock_dataset.ds_meta_data.authors = [mock_author]

    result = service.create_new_deposition(mock_dataset)

    assert result["metadata"]["upload_type"] == "publication"
    assert result["metadata"]["publication_type"] == "article"
    assert result["metadata"]["creators"][0] == {"name": "Jane Doe"}


@pytest.mark.unit
@patch("app.modules.fakenodo.services.current_user")
@patch("app.modules.fakenodo.services.os.path.getsize")
@patch("app.modules.fakenodo.services.calculate_checksum")
def test_fakenodo_service_upload_file(mock_checksum, mock_getsize, mock_current_user, test_client):
    """Test uploading a file through service."""
    service = FakenodoService()

    # Mock user
    mock_current_user.id = 1

    # Mock dataset
    mock_dataset = Mock()
    mock_dataset.id = 1

    # Mock feature model
    mock_feature_model = Mock()
    mock_feature_model.fm_meta_data.uvl_filename = "test.uvl"

    # Mock file operations
    mock_getsize.return_value = 1024
    mock_checksum.return_value = "abc123"

    result = service.upload_file(mock_dataset, 1, mock_feature_model)

    assert result["id"] == 1
    assert result["filename"] == "test.uvl"
    assert result["filesize"] == 1024
    assert result["checksum"] == "abc123"
    assert "message" in result


@pytest.mark.unit
def test_fakenodo_service_publish_deposition(test_client):
    """Test publishing a deposition through service."""
    service = FakenodoService()

    # Create a deposition first
    metadata = {
        "title": "Test Dataset",
        "description": "Test description",
    }
    deposition = service.deposition_repository.create_new_deposition(dep_metadata=metadata)

    # Publish it
    result = service.publish_deposition(deposition.id)

    assert result["id"] == deposition.id
    assert result["status"] == "published"
    assert result["conceptdoi"] == f"10.5281/fakenodo.{deposition.id}"
    assert "message" in result

    # Verify deposition was updated
    updated_deposition = Deposition.query.get(deposition.id)
    assert updated_deposition.status == "published"
    assert updated_deposition.doi == f"10.5281/fakenodo.{deposition.id}"


@pytest.mark.unit
def test_fakenodo_service_publish_deposition_not_found(test_client):
    """Test publishing a non-existent deposition."""
    service = FakenodoService()

    with pytest.raises(Exception, match="Deposition not found"):
        service.publish_deposition(99999)


@pytest.mark.unit
def test_fakenodo_service_get_deposition(test_client):
    """Test getting a deposition through service."""
    service = FakenodoService()

    # Create a deposition first
    metadata = {
        "title": "Test Dataset",
        "description": "Test description",
    }
    deposition = service.deposition_repository.create_new_deposition(dep_metadata=metadata)

    # Get it
    result = service.get_deposition(deposition.id)

    assert result["id"] == deposition.id
    assert result["metadata"] == metadata
    assert result["status"] == "draft"
    assert result["doi"] is None
    assert "message" in result


@pytest.mark.unit
def test_fakenodo_service_get_deposition_not_found(test_client):
    """Test getting a non-existent deposition."""
    service = FakenodoService()

    with pytest.raises(Exception, match="Deposition not found"):
        service.get_deposition(99999)


@pytest.mark.unit
def test_fakenodo_service_get_doi(test_client):
    """Test getting DOI of a deposition."""
    service = FakenodoService()

    # Create and publish a deposition
    metadata = {
        "title": "Test Dataset",
        "description": "Test description",
    }
    deposition = service.deposition_repository.create_new_deposition(dep_metadata=metadata)
    service.publish_deposition(deposition.id)

    # Get DOI
    doi = service.get_doi(deposition.id)

    assert doi == f"10.5281/fakenodo.{deposition.id}"


@pytest.mark.unit
def test_calculate_checksum():
    """Test calculate_checksum function."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
        f.write(b"test content")
        temp_file_path = f.name

    try:
        checksum = calculate_checksum(temp_file_path)
        # MD5 of "test content"
        assert checksum == "9473fdd0d880a43c21b7778d34872157"
    finally:
        os.remove(temp_file_path)


@pytest.mark.unit
def test_fakenodo_service_create_deposition_exception(test_client):
    """Test handling exception when creating deposition."""
    service = FakenodoService()

    # Mock dataset
    mock_dataset = Mock()
    mock_dataset.ds_meta_data.title = "Test"
    mock_dataset.ds_meta_data.description = "Test"
    mock_dataset.ds_meta_data.publication_type.value = "none"
    mock_dataset.ds_meta_data.tags = ""
    mock_dataset.ds_meta_data.authors = []

    # Mock repository to raise exception
    with patch.object(service.deposition_repository, "create_new_deposition", side_effect=Exception("Database error")):
        with pytest.raises(Exception, match="Failed to create local deposition: Database error"):
            service.create_new_deposition(mock_dataset)


@pytest.mark.unit
def test_fakenodo_service_publish_deposition_exception(test_client):
    """Test handling exception when publishing deposition."""
    service = FakenodoService()

    # Create a deposition
    metadata = {"title": "Test", "description": "Test"}
    deposition = service.deposition_repository.create_new_deposition(dep_metadata=metadata)

    # Mock repository update to raise exception
    with patch.object(service.deposition_repository, "update", side_effect=Exception("Database error")):
        with pytest.raises(Exception, match="Failed to publish deposition: Database error"):
            service.publish_deposition(deposition.id)
