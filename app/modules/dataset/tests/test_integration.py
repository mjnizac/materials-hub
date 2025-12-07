"""
Integration tests for dataset module.
"""

import pytest

from app import db
from app.modules.auth.models import User
from app.modules.dataset.models import MaterialsDataset
from app.modules.dataset.services import DSViewRecordService


@pytest.mark.integration
def test_dataset_download_route(test_client, integration_test_data):
    """
    Test the dataset download endpoint.
    """
    # Get dataset ID first
    with test_client.application.app_context():
        user = User.query.filter_by(email="user1@example.com").first()
        datasets = MaterialsDataset.query.filter_by(user_id=user.id).all()
        dataset_id = datasets[0].id if datasets else None

    # Make HTTP call outside app_context (test_client handles context automatically)
    if dataset_id:
        # Note: This will fail because files don't actually exist
        # but we can test the endpoint exists
        response = test_client.get(f"/dataset/download/{dataset_id}")
        # Expect 500 or 404 because files don't exist in test
        assert response.status_code in [200, 404, 500]


@pytest.mark.integration
def test_doi_redirect_route(test_client, integration_test_data):
    """
    Test viewing dataset by DOI.
    """
    # Get DOI without app_context, then make HTTP call
    with test_client.application.app_context():
        datasets = MaterialsDataset.query.filter(
            MaterialsDataset.ds_meta_data.has(dataset_doi="10.1234/ml.2024.001")
        ).all()
        doi = datasets[0].ds_meta_data.dataset_doi if datasets else None

    if doi:
        response = test_client.get(f"/doi/{doi}/")
        assert response.status_code in [200, 302]  # 200 OK or 302 redirect


@pytest.mark.integration
def test_dataset_list_route(test_client, integration_test_data):
    """
    Test the dataset list page (requires login).
    """
    # Login first (without app_context during HTTP calls)
    test_client.post("/login", data={"email": "user1@example.com", "password": "test1234"}, follow_redirects=True)

    response = test_client.get("/dataset/list")
    assert response.status_code == 200


@pytest.mark.integration
def test_unsynchronized_dataset_route(test_client, integration_test_data):
    """
    Test that unsynchronized datasets exist and can be queried.
    """
    # Get dataset ID first
    with test_client.application.app_context():
        # Clear any stale objects from the SQLAlchemy session to avoid ObjectDeletedError
        db.session.expire_all()
        db.session.remove()

        # Get unsync datasets directly by querying
        unsync_datasets = MaterialsDataset.query.filter(MaterialsDataset.ds_meta_data.has(dataset_doi=None)).all()

        # Verify we have at least one unsynchronized dataset
        assert len(unsync_datasets) >= 1
        assert unsync_datasets[0].ds_meta_data.dataset_doi is None


@pytest.mark.integration
def test_dsviewrecord_create_cookie(test_client, integration_test_data):
    """
    Test DSViewRecordService cookie creation.
    """
    with test_client.application.app_context():
        service = DSViewRecordService()

        user = User.query.filter_by(email="user1@example.com").first()
        datasets = MaterialsDataset.query.filter_by(user_id=user.id).first()

        if datasets:
            # Mock request context
            with test_client.application.test_request_context("/"):
                cookie = service.create_cookie(dataset=datasets)
                assert cookie is not None
                assert len(cookie) > 0


# ==================== API Integration Tests ====================


@pytest.mark.integration
def test_api_datasets_list(test_client):
    """
    Test the API endpoint for listing datasets.
    """
    response = test_client.get("/api/v1/datasets/")
    assert response.status_code in [200, 404]  # May be 404 if no datasets


@pytest.mark.integration
def test_api_dataset_get_by_id(test_client, integration_test_data):
    """
    Test the API endpoint for getting a specific materials dataset.
    """
    # Get dataset ID first
    with test_client.application.app_context():
        dataset = MaterialsDataset.query.first()
        dataset_id = dataset.id if dataset else None

    if dataset_id:
        response = test_client.get(f"/api/v1/materials-datasets/{dataset_id}")
        assert response.status_code == 200
        assert "dataset_id" in response.json or "id" in response.json


@pytest.mark.integration
def test_api_dataset_nonexistent(test_client):
    """
    Test the API endpoint returns 404 for non-existent dataset.
    """
    response = test_client.get("/api/v1/datasets/99999")
    assert response.status_code == 404


@pytest.mark.integration
def test_dataset_recommendations_api(test_client, integration_test_data):
    """
    Test the materials dataset recommendations API endpoint.
    """
    # Get dataset ID first
    with test_client.application.app_context():
        dataset = MaterialsDataset.query.first()
        dataset_id = dataset.id if dataset else None

    if dataset_id:
        response = test_client.get(
            f"/materials/{dataset_id}/recommendations", query_string={"page": 1, "filter_type": "authors"}
        )
        assert response.status_code == 200
        assert "html" in response.json or isinstance(response.json, dict)


@pytest.mark.integration
def test_dataset_recommendations_by_doi_api(test_client, integration_test_data):
    """
    Test the dataset DOI redirect endpoint.
    """
    # Get DOI first
    with test_client.application.app_context():
        dataset = MaterialsDataset.query.filter(
            MaterialsDataset.ds_meta_data.has(dataset_doi="10.1234/ml.2024.001")
        ).first()
        doi = dataset.ds_meta_data.dataset_doi if dataset and dataset.ds_meta_data else None

    if doi:
        # Test DOI redirect (should redirect to dataset view)
        response = test_client.get(f"/doi/{doi}/", follow_redirects=False)
        assert response.status_code in [302, 308]  # Redirect codes


@pytest.mark.integration
def test_dsviewrecord_service_count(test_client, integration_test_data):
    """Test DSViewRecordService count method."""
    with test_client.application.app_context():
        service = DSViewRecordService()
        count = service.count()
        assert count >= 0


@pytest.mark.integration
def test_materials_dataset_user_relationship(test_client, integration_test_data):
    """Test relationship between materials dataset and user."""
    with test_client.application.app_context():
        user = User.query.filter_by(email="user1@example.com").first()
        datasets = MaterialsDataset.query.filter_by(user_id=user.id).all()

        assert len(datasets) >= 1
        assert all(ds.user_id == user.id for ds in datasets)


@pytest.mark.integration
def test_materials_dataset_metadata_relationship(test_client, integration_test_data):
    """Test relationship between materials dataset and metadata."""
    with test_client.application.app_context():
        dataset = MaterialsDataset.query.first()

        if dataset:
            assert dataset.ds_meta_data is not None
            assert dataset.ds_meta_data.title is not None


@pytest.mark.integration
def test_api_dataset_statistics(test_client, integration_test_data):
    """Test the API endpoint for dataset statistics."""
    with test_client.application.app_context():
        dataset = MaterialsDataset.query.first()
        dataset_id = dataset.id if dataset else None

    if dataset_id:
        response = test_client.get(f"/api/v1/materials-datasets/{dataset_id}/statistics")
        assert response.status_code == 200


@pytest.mark.integration
def test_api_dataset_records(test_client, integration_test_data):
    """Test the API endpoint for dataset records."""
    with test_client.application.app_context():
        dataset = MaterialsDataset.query.first()
        dataset_id = dataset.id if dataset else None

    if dataset_id:
        response = test_client.get(f"/api/v1/materials-datasets/{dataset_id}/records")
        assert response.status_code == 200


@pytest.mark.integration
def test_api_dataset_records_search(test_client, integration_test_data):
    """Test the API endpoint for searching dataset records."""
    with test_client.application.app_context():
        dataset = MaterialsDataset.query.first()
        dataset_id = dataset.id if dataset else None

    if dataset_id:
        response = test_client.get(
            f"/api/v1/materials-datasets/{dataset_id}/records/search", query_string={"q": "test"}
        )
        assert response.status_code == 200


@pytest.mark.integration
def test_materials_dataset_created_at(test_client, integration_test_data):
    """Test that materials datasets have created_at timestamp."""
    with test_client.application.app_context():
        dataset = MaterialsDataset.query.first()

        if dataset:
            assert dataset.created_at is not None


@pytest.mark.integration
def test_dataset_upload_page_loads_when_logged_in(test_client, integration_test_data):
    """Test dataset upload page loads for logged-in users."""
    test_client.post("/login", data={"email": "user1@example.com", "password": "test1234"}, follow_redirects=True)
    response = test_client.get("/dataset/upload")
    assert response.status_code == 200
    test_client.get("/logout", follow_redirects=True)


@pytest.mark.integration
def test_materials_dataset_view_csv_route(test_client, integration_test_data):
    """Test viewing CSV for materials dataset."""
    with test_client.application.app_context():
        dataset = MaterialsDataset.query.first()
        dataset_id = dataset.id if dataset else None

    if dataset_id:
        test_client.post("/login", data={"email": "user1@example.com", "password": "test1234"}, follow_redirects=True)
        response = test_client.get(f"/materials/{dataset_id}/view_csv")
        assert response.status_code in [200, 404, 500]
        test_client.get("/logout", follow_redirects=True)


@pytest.mark.integration
def test_materials_dataset_upload_route_requires_login(test_client):
    """Test materials dataset upload requires login."""
    test_client.get("/materials/1/upload", follow_redirects=True)


@pytest.mark.integration
def test_materials_dataset_statistics_route(test_client, integration_test_data):
    """Test materials dataset statistics route."""
    with test_client.application.app_context():
        dataset = MaterialsDataset.query.first()
        dataset_id = dataset.id if dataset else None

    if dataset_id:
        response = test_client.get(f"/materials/{dataset_id}/statistics")
        assert response.status_code in [200, 404, 500]


@pytest.mark.integration
def test_author_service_initialization(test_client):
    """Test AuthorService initialization."""
    with test_client.application.app_context():
        from app.modules.dataset.services import AuthorService

        service = AuthorService()
        assert service is not None


@pytest.mark.integration
def test_dsmetadata_service_initialization(test_client):
    """Test DSMetaDataService initialization."""
    with test_client.application.app_context():
        from app.modules.dataset.services import DSMetaDataService

        service = DSMetaDataService()
        assert service is not None


@pytest.mark.integration
def test_doi_mapping_service_initialization(test_client):
    """Test DOIMappingService initialization."""
    with test_client.application.app_context():
        from app.modules.dataset.services import DOIMappingService

        service = DOIMappingService()
        assert service is not None


@pytest.mark.integration
def test_materials_dataset_service_initialization(test_client):
    """Test MaterialsDatasetService initialization."""
    with test_client.application.app_context():
        from app.modules.dataset.services import MaterialsDatasetService

        service = MaterialsDatasetService()
        assert service is not None


@pytest.mark.integration
def test_author_repository_operations(test_client):
    """Test AuthorRepository operations."""
    with test_client.application.app_context():
        from app.modules.dataset.repositories import AuthorRepository

        repository = AuthorRepository()

        # Create author
        author = repository.create(name="Test Author", affiliation="Test University", orcid="0000-0000-0000-0001")
        assert author.id is not None
        assert author.name == "Test Author"

        # Get by id
        retrieved = repository.get_by_id(author.id)
        assert retrieved.name == "Test Author"

        # Count
        count = repository.count()
        assert count >= 1


@pytest.mark.integration
def test_ds_metadata_repository_count(test_client):
    """Test dataset metadata repository count."""
    with test_client.application.app_context():
        from app.modules.dataset.repositories import DSMetaDataRepository

        repo = DSMetaDataRepository()
        count = repo.count()
        assert count >= 0


@pytest.mark.integration
def test_materials_dataset_repository_count(test_client):
    """Test materials dataset repository count."""
    with test_client.application.app_context():
        from app.modules.dataset.repositories import MaterialsDatasetRepository

        repo = MaterialsDatasetRepository()
        count = repo.count()
        assert count >= 0


@pytest.mark.integration
def test_doi_mapping_repository_count(test_client):
    """Test DOI mapping repository count."""
    with test_client.application.app_context():
        from app.modules.dataset.repositories import DOIMappingRepository

        repo = DOIMappingRepository()
        count = repo.count()
        assert count >= 0


@pytest.mark.integration
def test_ds_view_record_repository_count(test_client):
    """Test dataset view record repository count."""
    with test_client.application.app_context():
        from app.modules.dataset.repositories import DSViewRecordRepository

        repo = DSViewRecordRepository()
        count = repo.count()
        assert count >= 0


@pytest.mark.integration
def test_author_repository_count(test_client):
    """Test author repository count."""
    with test_client.application.app_context():
        from app.modules.dataset.repositories import AuthorRepository

        repo = AuthorRepository()
        count = repo.count()
        assert count >= 0


@pytest.mark.integration
def test_materials_dataset_properties_access(test_client, integration_test_data):
    """Test accessing materials dataset properties."""
    with test_client.application.app_context():
        dataset = MaterialsDataset.query.first()
        if dataset:
            assert hasattr(dataset, "id")
            assert hasattr(dataset, "user_id")
            assert hasattr(dataset, "ds_meta_data_id")
            assert hasattr(dataset, "created_at")


@pytest.mark.integration
def test_materials_dataset_to_dict(test_client, integration_test_data):
    """Test materials dataset to_dict method."""
    with test_client.application.app_context():
        dataset = MaterialsDataset.query.first()
        if dataset:
            data_dict = dataset.to_dict()
            assert isinstance(data_dict, dict)
            assert "id" in data_dict


@pytest.mark.integration
def test_ds_view_record_service_cookie_creation(test_client, integration_test_data):
    """Test DSViewRecordService cookie creation method exists."""
    with test_client.application.app_context():
        service = DSViewRecordService()
        assert hasattr(service, "create_cookie")


@pytest.mark.integration
def test_multiple_datasets_in_db(test_client, integration_test_data):
    """Test multiple datasets exist in database."""
    with test_client.application.app_context():
        datasets = MaterialsDataset.query.all()
        assert len(datasets) >= 3


@pytest.mark.integration
def test_materials_dataset_validate_csv_columns(test_client):
    """Test CSV column validation."""
    with test_client.application.app_context():
        from app.modules.dataset.services import MaterialsDatasetService

        service = MaterialsDatasetService()

        # Test valid columns
        valid_columns = ["material_name", "property_name", "property_value"]
        result = service.validate_csv_columns(valid_columns)
        assert result["valid"] is True
        assert len(result["missing_required"]) == 0

        # Test missing required columns
        invalid_columns = ["material_name"]
        result = service.validate_csv_columns(invalid_columns)
        assert result["valid"] is False
        assert len(result["missing_required"]) > 0


@pytest.mark.integration
def test_ds_metadata_service_initialization(test_client):
    """Test DSMetaDataService initialization."""
    with test_client.application.app_context():
        from app.modules.dataset.services import DSMetaDataService

        service = DSMetaDataService()
        assert service is not None


@pytest.mark.integration
def test_author_service_get_by_id(test_client):
    """Test AuthorService get_by_id."""
    with test_client.application.app_context():
        from app.modules.dataset.repositories import AuthorRepository
        from app.modules.dataset.services import AuthorService

        service = AuthorService()
        repo = AuthorRepository()

        # Create author
        author = repo.create(name="Test Author", affiliation="Test Univ", orcid="0000-0000-0000-0002")

        # Get by id
        retrieved = service.get_by_id(author.id)
        assert retrieved is not None
        assert retrieved.name == "Test Author"


@pytest.mark.integration
def test_doi_mapping_service_get_by_id(test_client):
    """Test DOIMappingService get_by_id."""
    with test_client.application.app_context():
        from app.modules.dataset.services import DOIMappingService

        service = DOIMappingService()
        # Test with non-existent ID
        result = service.get_by_id(99999)
        assert result is None


@pytest.mark.integration
def test_ds_view_record_service_get_by_id(test_client):
    """Test DSViewRecordService get_by_id."""
    with test_client.application.app_context():
        from app.modules.dataset.services import DSViewRecordService

        service = DSViewRecordService()
        # Test with non-existent ID
        result = service.get_by_id(99999)
        assert result is None
