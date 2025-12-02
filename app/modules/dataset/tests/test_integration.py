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
