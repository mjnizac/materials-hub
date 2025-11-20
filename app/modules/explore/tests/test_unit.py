"""
Unit tests for explore module.

Tests the explore service and repository functionality for searching and filtering datasets.
"""

import pytest

from app.modules.explore.services import ExploreService


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        pass
    yield test_client


class TestExploreService:
    """Test cases for ExploreService"""

    def test_explore_service_initialization(self):
        """Test that ExploreService can be initialized properly"""
        service = ExploreService()
        assert service is not None
        assert hasattr(service, "repository")

    def test_filter_method_exists(self):
        """Test that filter method exists in ExploreService"""
        service = ExploreService()
        assert hasattr(service, "filter")
        assert callable(service.filter)

    def test_filter_with_default_parameters(self, test_client):
        """Test filter method with default parameters"""
        service = ExploreService()
        result = service.filter()
        assert result is not None

    def test_filter_with_query(self, test_client):
        """Test filter method with search query"""
        service = ExploreService()
        result = service.filter(query="test")
        assert result is not None

    def test_filter_with_sorting_newest(self, test_client):
        """Test filter method with newest sorting"""
        service = ExploreService()
        result = service.filter(sorting="newest")
        assert result is not None

    def test_filter_with_sorting_oldest(self, test_client):
        """Test filter method with oldest sorting"""
        service = ExploreService()
        result = service.filter(sorting="oldest")
        assert result is not None

    def test_filter_with_publication_type(self, test_client):
        """Test filter method with publication type filter"""
        service = ExploreService()
        result = service.filter(publication_type="dataset")
        assert result is not None

    def test_filter_with_tags(self, test_client):
        """Test filter method with tags filter"""
        service = ExploreService()
        result = service.filter(tags=["test", "example"])
        assert result is not None

    def test_filter_with_all_parameters(self, test_client):
        """Test filter method with all parameters combined"""
        service = ExploreService()
        result = service.filter(
            query="test dataset", sorting="newest", publication_type="dataset", tags=["machine-learning", "data"]
        )
        assert result is not None


def test_explore_route_accessible(test_client):
    """Test that explore route is accessible"""
    response = test_client.get("/explore")
    assert response.status_code == 200


def test_explore_route_returns_html(test_client):
    """Test that explore route returns HTML content"""
    response = test_client.get("/explore")
    assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data
