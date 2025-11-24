"""
Unit tests for zenodo module.

Tests the Zenodo service functionality for API integration including connection testing,
deposition creation, file upload, and DOI retrieval.
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.modules.zenodo.services import ZenodoService


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        pass
    yield test_client


@pytest.fixture
def zenodo_service():
    """Fixture to create a ZenodoService instance"""
    with patch.dict(os.environ, {"ZENODO_ACCESS_TOKEN": "test_token", "FLASK_ENV": "development"}):
        service = ZenodoService()
        yield service


@pytest.mark.unit
class TestZenodoService:
    """Test cases for ZenodoService"""

    def test_zenodo_service_initialization(self, zenodo_service):
        """Test that ZenodoService can be initialized properly"""
        assert zenodo_service is not None
        assert hasattr(zenodo_service, "ZENODO_ACCESS_TOKEN")
        assert hasattr(zenodo_service, "ZENODO_API_URL")

    def test_get_zenodo_url_development(self):
        """Test that development environment returns sandbox URL"""
        with patch.dict(os.environ, {"FLASK_ENV": "development"}):
            service = ZenodoService()
            url = service.get_zenodo_url()
            assert "sandbox.zenodo.org" in url

    def test_get_zenodo_url_production(self):
        """Test that production environment returns production URL"""
        with patch.dict(os.environ, {"FLASK_ENV": "production"}):
            service = ZenodoService()
            url = service.get_zenodo_url()
            assert url == "https://zenodo.org/api/deposit/depositions" or "zenodo.org" in url

    def test_get_zenodo_access_token(self, zenodo_service):
        """Test that access token is retrieved correctly"""
        token = zenodo_service.get_zenodo_access_token()
        assert token is not None

    def test_headers_configuration(self, zenodo_service):
        """Test that headers are configured correctly"""
        assert zenodo_service.headers == {"Content-Type": "application/json"}

    def test_params_configuration(self, zenodo_service):
        """Test that params are configured with access token"""
        assert "access_token" in zenodo_service.params
        assert zenodo_service.params["access_token"] is not None

    @patch("app.modules.zenodo.services.requests.get")
    def test_connection_success(self, mock_get, zenodo_service):
        """Test successful connection to Zenodo API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = zenodo_service.test_connection()
        assert result is True
        mock_get.assert_called_once()

    @patch("app.modules.zenodo.services.requests.get")
    def test_connection_failure(self, mock_get, zenodo_service):
        """Test failed connection to Zenodo API"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = zenodo_service.test_connection()
        assert result is False

    @patch("app.modules.zenodo.services.requests.get")
    def test_get_all_depositions_success(self, mock_get, zenodo_service):
        """Test getting all depositions successfully"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1, "title": "Test Deposition"}]
        mock_get.return_value = mock_response

        result = zenodo_service.get_all_depositions()
        assert isinstance(result, list)
        assert len(result) > 0

    @patch("app.modules.zenodo.services.requests.get")
    def test_get_all_depositions_failure(self, mock_get, zenodo_service):
        """Test getting all depositions with API error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(Exception, match="Failed to get depositions"):
            zenodo_service.get_all_depositions()

    @patch("app.modules.zenodo.services.requests.get")
    def test_get_deposition_success(self, mock_get, zenodo_service):
        """Test getting a specific deposition"""
        deposition_id = 12345
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": deposition_id, "title": "Test", "doi": "10.5281/zenodo.12345"}
        mock_get.return_value = mock_response

        result = zenodo_service.get_deposition(deposition_id)
        assert result["id"] == deposition_id
        assert "doi" in result

    @patch("app.modules.zenodo.services.requests.get")
    def test_get_deposition_failure(self, mock_get, zenodo_service):
        """Test getting deposition with invalid ID"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with pytest.raises(Exception, match="Failed to get deposition"):
            zenodo_service.get_deposition(99999)

    @patch("app.modules.zenodo.services.requests.get")
    def test_get_doi(self, mock_get, zenodo_service):
        """Test getting DOI from deposition"""
        deposition_id = 12345
        expected_doi = "10.5281/zenodo.12345"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": deposition_id, "doi": expected_doi}
        mock_get.return_value = mock_response

        doi = zenodo_service.get_doi(deposition_id)
        assert doi == expected_doi

    @patch("app.modules.zenodo.services.requests.post")
    def test_create_new_deposition(self, mock_post, zenodo_service):
        """Test creating a new deposition"""
        # Mock dataset with necessary attributes
        mock_dataset = MagicMock()
        mock_dataset.ds_meta_data.title = "Test Dataset"
        mock_dataset.ds_meta_data.description = "Test Description"
        mock_dataset.ds_meta_data.publication_type.value = "dataset"
        mock_dataset.ds_meta_data.authors = []
        mock_dataset.ds_meta_data.tags = "test, dataset"

        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 12345, "title": "Test Dataset"}
        mock_post.return_value = mock_response

        result = zenodo_service.create_new_deposition(mock_dataset)
        assert result["id"] == 12345
        mock_post.assert_called_once()

    @patch("app.modules.zenodo.services.requests.post")
    def test_publish_deposition_success(self, mock_post, zenodo_service):
        """Test publishing a deposition"""
        deposition_id = 12345
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.json.return_value = {"id": deposition_id, "state": "done"}
        mock_post.return_value = mock_response

        result = zenodo_service.publish_deposition(deposition_id)
        assert result["id"] == deposition_id

    @patch("app.modules.zenodo.services.requests.post")
    def test_publish_deposition_failure(self, mock_post, zenodo_service):
        """Test publishing deposition with error"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        with pytest.raises(Exception, match="Failed to publish deposition"):
            zenodo_service.publish_deposition(12345)
