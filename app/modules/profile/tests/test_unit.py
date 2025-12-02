"""
Unit tests for profile module.
"""
import pytest

from app.modules.conftest import login, logout


@pytest.mark.unit
def test_edit_profile_page_get(test_client):
    """
    Tests access to the profile editing page via a GET request.
    """
    login_response = login(test_client, "test@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/profile/edit")
    assert response.status_code == 200, "The profile editing page could not be accessed."
    assert b"Edit profile" in response.data, "The expected content is not present on the page"

    logout(test_client)


@pytest.mark.unit
def test_user_profile_service_initialization(test_client):
    """Test UserProfileService initialization"""
    from app.modules.profile.services import UserProfileService

    service = UserProfileService()
    assert service.repository is not None


@pytest.mark.unit
def test_user_profile_service_update_profile_success(test_client):
    """Test UserProfileService.update_profile() with valid form"""
    from app import db
    from app.modules.auth.models import User
    from app.modules.profile.forms import UserProfileForm
    from app.modules.profile.models import UserProfile
    from app.modules.profile.services import UserProfileService
    from werkzeug.datastructures import ImmutableMultiDict

    user = User(email="test_profile_update@example.com", password="test123")
    db.session.add(user)
    db.session.commit()

    profile = UserProfile(user_id=user.id, name="Old Name", surname="Old Surname")
    db.session.add(profile)
    db.session.commit()

    # Create valid form data
    form_data = ImmutableMultiDict([("name", "New Name"), ("surname", "New Surname")])
    form = UserProfileForm(form_data)

    service = UserProfileService()
    updated_profile, errors = service.update_profile(profile.id, form)

    assert errors is None
    assert updated_profile is not None
    assert updated_profile.name == "New Name"
    assert updated_profile.surname == "New Surname"
