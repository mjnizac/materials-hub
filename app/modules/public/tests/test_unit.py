"""
Unit tests for public module.
"""
import pytest
from unittest.mock import Mock, patch


@pytest.mark.unit
def test_index_page_loads(test_client):
    """
    Test that the index page loads successfully and returns 200 status code.
    """
    with patch("app.modules.public.routes.MaterialsDatasetRepository") as mock_materials_repo, patch(
        "app.modules.public.routes.DSDownloadRecordRepository"
    ) as mock_download_repo, patch("app.modules.public.routes.DSViewRecordRepository") as mock_view_repo:
        # Mock repository methods
        mock_materials_repo_instance = Mock()
        mock_materials_repo_instance.count_synchronized.return_value = 10
        mock_materials_repo_instance.get_synchronized_latest.return_value = []
        mock_materials_repo.return_value = mock_materials_repo_instance

        mock_download_repo_instance = Mock()
        mock_download_repo_instance.count.return_value = 100
        mock_download_repo.return_value = mock_download_repo_instance

        mock_view_repo_instance = Mock()
        mock_view_repo_instance.count.return_value = 500
        mock_view_repo.return_value = mock_view_repo_instance

        response = test_client.get("/")

        assert response.status_code == 200, "The index page should return status code 200"


@pytest.mark.unit
def test_index_page_calls_repositories(test_client):
    """
    Test that the index page calls all required repositories.
    """
    with patch("app.modules.public.routes.MaterialsDatasetRepository") as mock_materials_repo, patch(
        "app.modules.public.routes.DSDownloadRecordRepository"
    ) as mock_download_repo, patch("app.modules.public.routes.DSViewRecordRepository") as mock_view_repo:
        # Mock repository methods
        mock_materials_repo_instance = Mock()
        mock_materials_repo_instance.count_synchronized.return_value = 10
        mock_materials_repo_instance.get_synchronized_latest.return_value = []
        mock_materials_repo.return_value = mock_materials_repo_instance

        mock_download_repo_instance = Mock()
        mock_download_repo_instance.count.return_value = 100
        mock_download_repo.return_value = mock_download_repo_instance

        mock_view_repo_instance = Mock()
        mock_view_repo_instance.count.return_value = 500
        mock_view_repo.return_value = mock_view_repo_instance

        test_client.get("/")

        # Verify repository methods were called
        mock_materials_repo_instance.count_synchronized.assert_called_once()
        mock_materials_repo_instance.get_synchronized_latest.assert_called_once_with(limit=5)
        mock_download_repo_instance.count.assert_called_once()
        mock_view_repo_instance.count.assert_called_once()
