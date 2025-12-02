"""
Unit tests for team module.
"""
import pytest


@pytest.mark.unit
def test_team_page_loads(test_client):
    """
    Test that the team page loads successfully and returns 200 status code.
    """
    response = test_client.get("/team")

    assert response.status_code == 200, "The team page should return status code 200"


@pytest.mark.unit
def test_team_page_content(test_client):
    """
    Test that the team page contains expected content.
    """
    response = test_client.get("/team")

    assert response.status_code == 200
    assert b"text/html" in response.content_type.encode(), "Response should be HTML"
