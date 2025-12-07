"""
Integration tests for auth module.
"""

import pytest

from app.modules.auth.models import User


@pytest.mark.integration
def test_signup_page_loads(test_client):
    """Test that the signup page loads successfully."""
    response = test_client.get("/signup/")
    assert response.status_code == 200
    assert b"Sign Up" in response.data or b"Sign up" in response.data or b"Signup" in response.data


@pytest.mark.integration
def test_signup_new_user(test_client):
    """Test creating a new user through signup form."""
    # Create a new user
    response = test_client.post(
        "/signup/",
        data={
            "email": "newintegrationuser@example.com",
            "password": "SecurePass123!",
            "name": "Integration",
            "surname": "Test User",
        },
        follow_redirects=True,
    )

    # Should redirect to index after successful signup
    assert response.status_code == 200

    # Verify user was created
    with test_client.application.app_context():
        user = User.query.filter_by(email="newintegrationuser@example.com").first()
        assert user is not None
        assert user.profile.name == "Integration"
        assert user.profile.surname == "Test User"

    # Logout to clean state for next tests
    test_client.get("/logout", follow_redirects=True)


@pytest.mark.integration
def test_signup_duplicate_email(test_client, integration_test_data):
    """Test that signing up with an existing email fails."""
    response = test_client.post(
        "/signup/",
        data={
            "email": "user1@example.com",  # Existing email from integration_test_data
            "password": "AnotherPassword123!",
            "name": "Duplicate",
            "surname": "User",
        },
        follow_redirects=True,
    )

    # Should show error about email in use
    assert b"in use" in response.data or b"exists" in response.data or b"already" in response.data


@pytest.mark.integration
def test_login_page_loads(test_client):
    """Test that the login page loads successfully."""
    response = test_client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data or b"Sign in" in response.data


@pytest.mark.integration
def test_login_success(test_client, integration_test_data):
    """Test successful login with valid credentials."""
    response = test_client.post(
        "/login",
        data={"email": "user1@example.com", "password": "test1234"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    # After login, should redirect to index
    assert response.request.path == "/"

    # Logout to clean state for next tests
    test_client.get("/logout", follow_redirects=True)


@pytest.mark.integration
def test_login_invalid_credentials(test_client):
    """Test login with invalid credentials."""
    response = test_client.post(
        "/login",
        data={"email": "nonexistent@example.com", "password": "wrongpassword"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid" in response.data or b"incorrect" in response.data or b"failed" in response.data


@pytest.mark.integration
def test_logout(test_client, integration_test_data):
    """Test logout functionality."""
    # First login
    test_client.post("/login", data={"email": "user1@example.com", "password": "test1234"}, follow_redirects=True)

    # Then logout
    response = test_client.get("/logout", follow_redirects=True)

    assert response.status_code == 200
    # Should redirect to index after logout
    assert response.request.path == "/"


@pytest.mark.integration
def test_authenticated_user_redirected_from_login(test_client, integration_test_data):
    """Test that authenticated users are redirected from login page."""
    # Login first
    test_client.post("/login", data={"email": "user1@example.com", "password": "test1234"}, follow_redirects=True)

    # Try to access login page while authenticated
    response = test_client.get("/login", follow_redirects=True)

    # Should redirect to index
    assert response.status_code == 200
    assert response.request.path == "/"

    # Logout to clean state
    test_client.get("/logout", follow_redirects=True)


@pytest.mark.integration
def test_authenticated_user_redirected_from_signup(test_client, integration_test_data):
    """Test that authenticated users are redirected from signup page."""
    # Login first
    test_client.post("/login", data={"email": "user1@example.com", "password": "test1234"}, follow_redirects=True)

    # Try to access signup page while authenticated
    response = test_client.get("/signup/", follow_redirects=True)

    # Should redirect to index
    assert response.status_code == 200
    assert response.request.path == "/"

    # Logout to clean state
    test_client.get("/logout", follow_redirects=True)


@pytest.mark.integration
def test_user_password_hashing(test_client):
    """Test that user passwords are hashed."""
    with test_client.application.app_context():
        from app import db
        from app.modules.auth.models import User

        user = User(email="hashtest@example.com")
        user.set_password("mypassword123")
        db.session.add(user)
        db.session.commit()

        # Password should be hashed, not plain text
        assert user.password != "mypassword123"
        assert user.check_password("mypassword123") is True
        assert user.check_password("wrongpassword") is False


@pytest.mark.integration
def test_user_profile_relationship(test_client, integration_test_data):
    """Test relationship between user and profile."""
    with test_client.application.app_context():
        from app.modules.auth.models import User

        user = User.query.filter_by(email="user1@example.com").first()

        assert user is not None
        assert user.profile is not None
        assert user.profile.name == "User"
        assert user.profile.surname == "One"


@pytest.mark.integration
def test_authentication_service_email_availability(test_client):
    """Test checking email availability."""
    with test_client.application.app_context():
        from app.modules.auth.services import AuthenticationService

        service = AuthenticationService()

        # Check that a new email is available
        assert service.is_email_available("newemail@test.com") is True


@pytest.mark.integration
def test_authentication_service_email_not_available(test_client, integration_test_data):
    """Test checking email not available."""
    with test_client.application.app_context():
        from app.modules.auth.services import AuthenticationService

        service = AuthenticationService()

        # Check that an existing email is not available
        assert service.is_email_available("user1@example.com") is False


@pytest.mark.integration
def test_user_count(test_client, integration_test_data):
    """Test counting users."""
    with test_client.application.app_context():
        from app.modules.auth.models import User

        users = User.query.all()
        assert len(users) >= 1


@pytest.mark.integration
def test_login_with_remember_me(test_client, integration_test_data):
    """Test login with remember me functionality."""
    response = test_client.post(
        "/login",
        data={"email": "user1@example.com", "password": "test1234", "remember_me": True},
        follow_redirects=True,
    )

    assert response.status_code == 200

    # Logout
    test_client.get("/logout", follow_redirects=True)


@pytest.mark.integration
def test_auth_service_create_with_profile(test_client):
    """Test creating user with profile through AuthenticationService."""
    with test_client.application.app_context():
        from app.modules.auth.services import AuthenticationService

        service = AuthenticationService()

        user = service.create_with_profile(
            email="servicetest@example.com", password="testpass123", name="Service", surname="Tester"
        )

        assert user is not None
        assert user.email == "servicetest@example.com"
        assert user.profile.name == "Service"
        assert user.profile.surname == "Tester"


@pytest.mark.integration
def test_auth_repository_get_by_email(test_client, integration_test_data):
    """Test getting user by email through repository."""
    with test_client.application.app_context():
        from app.modules.auth.repositories import UserRepository

        repo = UserRepository()

        user = repo.get_by_email("user1@example.com")
        assert user is not None
        assert user.email == "user1@example.com"


@pytest.mark.integration
def test_auth_repository_create_user(test_client):
    """Test creating user through repository."""
    with test_client.application.app_context():
        from app.modules.auth.repositories import UserRepository

        repo = UserRepository()

        user = repo.create(email="repouser@example.com", password="hashed_password")
        assert user is not None
        assert user.email == "repouser@example.com"


@pytest.mark.integration
def test_user_model_password_check(test_client, integration_test_data):
    """Test user password verification."""
    with test_client.application.app_context():
        user = User.query.filter_by(email="user1@example.com").first()
        assert user is not None
        assert user.check_password("test1234") is True
        assert user.check_password("wrongpassword") is False


@pytest.mark.integration
def test_user_profile_name_display(test_client, integration_test_data):
    """Test user profile name display."""
    with test_client.application.app_context():
        user = User.query.filter_by(email="user1@example.com").first()
        assert user.profile is not None
        full_name = f"{user.profile.name} {user.profile.surname}"
        assert len(full_name) > 0


@pytest.mark.integration
def test_multiple_users_creation(test_client):
    """Test creating multiple users."""
    with test_client.application.app_context():
        from app.modules.auth.services import AuthenticationService

        service = AuthenticationService()

        users = []
        for i in range(3):
            user = service.create_with_profile(
                email=f"bulkuser{i}@example.com", password=f"pass{i}", name=f"User{i}", surname=f"Test{i}"
            )
            users.append(user)

        assert len(users) == 3
        for user in users:
            assert user.id is not None


@pytest.mark.integration
def test_login_route_post_valid(test_client, integration_test_data):
    """Test login route with valid credentials."""
    response = test_client.post(
        "/login", data={"email": "user1@example.com", "password": "test1234"}, follow_redirects=True
    )
    assert response.status_code == 200
    # Logout
    test_client.get("/logout", follow_redirects=True)


@pytest.mark.integration
def test_login_route_post_invalid(test_client):
    """Test login route with invalid credentials."""
    response = test_client.post(
        "/login", data={"email": "invalid@example.com", "password": "wrongpass"}, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Login" in response.data


@pytest.mark.integration
def test_signup_route_get(test_client):
    """Test signup route GET request."""
    response = test_client.get("/signup", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.integration
def test_logout_route(test_client, integration_test_data):
    """Test logout route."""
    # Login first
    test_client.post("/login", data={"email": "user1@example.com", "password": "test1234"}, follow_redirects=True)

    # Logout
    response = test_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
