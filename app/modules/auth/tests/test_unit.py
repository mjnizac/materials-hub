"""
Unit tests for auth module.
"""

import pytest
from flask import url_for

from app.modules.auth.repositories import UserRepository
from app.modules.auth.services import AuthenticationService
from app.modules.profile.repositories import UserProfileRepository


@pytest.mark.unit
def test_login_success(test_client):
    response = test_client.post(
        "/login", data=dict(email="test@example.com", password="test1234"), follow_redirects=True
    )

    assert response.request.path != url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


@pytest.mark.unit
def test_login_unsuccessful_bad_email(test_client):
    response = test_client.post(
        "/login", data=dict(email="bademail@example.com", password="test1234"), follow_redirects=True
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


@pytest.mark.unit
def test_login_unsuccessful_bad_password(test_client):
    response = test_client.post(
        "/login", data=dict(email="test@example.com", password="basspassword"), follow_redirects=True
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


@pytest.mark.unit
def test_signup_user_no_name(test_client):
    response = test_client.post(
        "/signup", data=dict(surname="Foo", email="test@example.com", password="test1234"), follow_redirects=True
    )
    assert response.request.path == url_for("auth.show_signup_form"), "Signup was unsuccessful"
    assert b"This field is required" in response.data, response.data


@pytest.mark.unit
def test_signup_user_unsuccessful(test_client):
    email = "test@example.com"
    response = test_client.post(
        "/signup", data=dict(name="Test", surname="Foo", email=email, password="test1234"), follow_redirects=True
    )
    assert response.request.path == url_for("auth.show_signup_form"), "Signup was unsuccessful"
    assert f"Email {email} in use".encode("utf-8") in response.data


@pytest.mark.unit
def test_signup_user_successful(test_client):
    response = test_client.post(
        "/signup",
        data=dict(name="Foo", surname="Example", email="foo@example.com", password="foo1234"),
        follow_redirects=True,
    )
    assert response.request.path == url_for("public.index"), "Signup was unsuccessful"


@pytest.mark.unit
def test_service_create_with_profie_success(clean_database):
    data = {"name": "Test", "surname": "Foo", "email": "service_test@example.com", "password": "test1234"}

    AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 1
    assert UserProfileRepository().count() == 1


@pytest.mark.unit
def test_service_create_with_profile_fail_no_email(clean_database):
    data = {"name": "Test", "surname": "Foo", "email": "", "password": "1234"}

    with pytest.raises(ValueError, match="Email is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


@pytest.mark.unit
def test_service_create_with_profile_fail_no_password(clean_database):
    data = {"name": "Test", "surname": "Foo", "email": "test@example.com", "password": ""}

    with pytest.raises(ValueError, match="Password is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


@pytest.mark.unit
def test_service_create_with_profile_fail_no_name(clean_database):
    """Test AuthenticationService.create_with_profile() fails without name"""
    data = {"name": "", "surname": "Foo", "email": "test@example.com", "password": "test1234"}

    with pytest.raises(ValueError, match="Name is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


@pytest.mark.unit
def test_service_create_with_profile_fail_no_surname(clean_database):
    """Test AuthenticationService.create_with_profile() fails without surname"""
    data = {"name": "Test", "surname": "", "email": "test@example.com", "password": "test1234"}

    with pytest.raises(ValueError, match="Surname is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


@pytest.mark.unit
def test_service_is_email_available_true(clean_database):
    """Test AuthenticationService.is_email_available() returns True for unused email"""
    service = AuthenticationService()

    assert service.is_email_available("unused@example.com") is True


@pytest.mark.unit
def test_service_is_email_available_false(test_client):
    """Test AuthenticationService.is_email_available() returns False for used email"""
    from app.modules.auth.models import User

    service = AuthenticationService()

    # Create a user explicitly for this test
    user = User(email="used_email@example.com", password="test1234")
    service.repository.session.add(user)
    service.repository.session.commit()

    assert service.is_email_available("used_email@example.com") is False


@pytest.mark.unit
def test_service_login_method_success(test_client):
    """Test AuthenticationService.login() method directly"""
    from app.modules.auth.models import User

    service = AuthenticationService()

    # Create a test user
    user = User(email="login_test@example.com", password="testpass123")
    service.repository.session.add(user)
    service.repository.session.commit()

    # Test login
    result = service.login("login_test@example.com", "testpass123", remember=False)
    assert result is True


@pytest.mark.unit
def test_service_login_method_fail_bad_email(test_client):
    """Test AuthenticationService.login() fails with wrong email"""
    service = AuthenticationService()

    result = service.login("nonexistent@example.com", "anypassword")
    assert result is False


@pytest.mark.unit
def test_service_login_method_fail_bad_password(test_client):
    """Test AuthenticationService.login() fails with wrong password"""
    service = AuthenticationService()

    # test@example.com exists from fixtures
    result = service.login("test@example.com", "wrongpassword")
    assert result is False


@pytest.mark.unit
def test_service_temp_folder_by_user(test_client):
    """Test AuthenticationService.temp_folder_by_user()"""
    from app.modules.auth.models import User

    service = AuthenticationService()
    user = User(id=123, email="test@example.com", password="test")

    folder = service.temp_folder_by_user(user)

    assert "temp" in folder
    assert "123" in folder
