"""
Integration tests for explore module.
"""
import pytest

from app.modules.dataset.models import PublicationType
from app.modules.explore.services import ExploreService


@pytest.mark.integration
def test_explore_index_page_loads(test_client):
    """
    Test that the explore page loads successfully.
    """
    response = test_client.get("/explore")
    assert response.status_code == 200


@pytest.mark.integration
def test_explore_search_by_query(test_client, integration_test_data):
    """
    Test searching datasets by query string.
    """
    with test_client.application.app_context():
        service = ExploreService()

        # Search for "machine learning"
        results = service.filter(query="machine learning")
        assert len(results) >= 1
        assert any("Machine Learning" in ds.ds_meta_data.title for ds in results)


@pytest.mark.integration
def test_explore_search_by_author_name(test_client, integration_test_data):
    """
    Test searching datasets by author name.
    """
    with test_client.application.app_context():
        service = ExploreService()

        # Search for author "Jane Smith"
        results = service.filter(query="Jane Smith")
        assert len(results) >= 1
        assert any(any(author.name == "Jane Smith" for author in ds.ds_meta_data.authors) for ds in results)


@pytest.mark.integration
def test_explore_search_by_affiliation(test_client, integration_test_data):
    """
    Test searching datasets by author affiliation.
    """
    with test_client.application.app_context():
        service = ExploreService()

        # Search for affiliation "MIT"
        results = service.filter(query="MIT")
        assert len(results) >= 1
        assert any(any(author.affiliation == "MIT" for author in ds.ds_meta_data.authors) for ds in results)


@pytest.mark.integration
def test_explore_filter_by_publication_type(test_client, integration_test_data):
    """
    Test filtering datasets by publication type.
    """
    with test_client.application.app_context():
        service = ExploreService()

        # Filter by conference paper
        results = service.filter(query="", publication_type="conferencepaper")
        assert len(results) >= 1
        assert all(ds.ds_meta_data.publication_type == PublicationType.CONFERENCE_PAPER for ds in results)


@pytest.mark.integration
def test_explore_filter_by_tags(test_client, integration_test_data):
    """
    Test filtering datasets by tags.
    """
    with test_client.application.app_context():
        service = ExploreService()

        # Filter by tag "patterns"
        results = service.filter(query="", tags=["patterns"])
        assert len(results) >= 1
        assert all("patterns" in ds.ds_meta_data.tags.lower() for ds in results)


@pytest.mark.integration
def test_explore_sorting_newest(test_client, integration_test_data):
    """
    Test sorting datasets by newest first.
    """
    with test_client.application.app_context():
        service = ExploreService()

        results = service.filter(query="", sorting="newest")
        assert len(results) >= 2

        # Verify descending order
        for i in range(len(results) - 1):
            assert results[i].created_at >= results[i + 1].created_at


@pytest.mark.integration
def test_explore_sorting_oldest(test_client, integration_test_data):
    """
    Test sorting datasets by oldest first.
    """
    with test_client.application.app_context():
        service = ExploreService()

        results = service.filter(query="", sorting="oldest")
        assert len(results) >= 2

        # Verify ascending order
        for i in range(len(results) - 1):
            assert results[i].created_at <= results[i + 1].created_at


@pytest.mark.integration
def test_explore_combined_filters(test_client, integration_test_data):
    """
    Test using multiple filters together.
    """
    with test_client.application.app_context():
        service = ExploreService()

        # Search with query, publication type, and tags
        results = service.filter(query="software", publication_type="conferencepaper", tags=["patterns"])
        assert len(results) >= 1
        assert all(ds.ds_meta_data.publication_type == PublicationType.CONFERENCE_PAPER for ds in results)


@pytest.mark.integration
def test_explore_api_endpoint(test_client, integration_test_data):
    """
    Test the explore API endpoint returns JSON results.
    """
    response = test_client.post(
        "/explore",
        json={"query": "machine", "sorting": "newest", "publication_type": "any", "tags": []},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) >= 1
