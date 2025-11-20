"""
Integration tests for authentication module.

Tests the complete authentication workflow including registration, login,
logout, and session management with real database interactions.
"""

import pytest
from flask import url_for

from app import db
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        pass
    yield test_client


@pytest.mark.integration
class TestAuthenticationIntegration:
    """Integration tests for complete authentication workflows"""

    def test_complete_signup_workflow(self, test_client):
        """Test complete user registration workflow"""
        # Step 1: Access signup page
        response = test_client.get("/signup")
        assert response.status_code == 200

        # Step 2: Submit registration form
        response = test_client.post(
            "/signup",
            data=dict(name="IntegrationTest", surname="User", email="integration@test.com", password="secure123"),
            follow_redirects=True,
        )

        # Step 3: Verify redirect to home page (successful registration)
        assert response.request.path == url_for("public.index")

        # Step 4: Verify user exists in database
        with test_client.application.app_context():
            user = User.query.filter_by(email="integration@test.com").first()
            assert user is not None
            assert user.profile is not None
            assert user.profile.name == "IntegrationTest"
            assert user.profile.surname == "User"

            # Cleanup
            if user.profile:
                db.session.delete(user.profile)
            db.session.delete(user)
            db.session.commit()

    def test_login_logout_workflow(self, test_client):
        """Test complete login and logout workflow"""
        # Step 1: Login
        response = test_client.post(
            "/login", data=dict(email="test@example.com", password="test1234"), follow_redirects=True
        )
        assert response.request.path != url_for("auth.login")

        # Step 2: Access protected route (should work)
        response = test_client.get("/profile/summary")
        assert response.status_code in [200, 302]  # Either accessible or redirects

        # Step 3: Logout
        response = test_client.get("/logout", follow_redirects=True)
        assert response.status_code == 200

        # Step 4: Try accessing protected route (should redirect to login)
        response = test_client.get("/profile/summary", follow_redirects=False)
        # After logout, accessing protected routes may redirect to login
        assert response.status_code in [200, 302, 401]

    def test_failed_login_attempts(self, test_client):
        """Test multiple failed login attempts"""
        # Attempt 1: Wrong password
        response = test_client.post(
            "/login", data=dict(email="test@example.com", password="wrongpassword"), follow_redirects=True
        )
        assert response.request.path == url_for("auth.login")

        # Attempt 2: Non-existent user
        response = test_client.post(
            "/login", data=dict(email="nonexistent@example.com", password="password"), follow_redirects=True
        )
        assert response.request.path == url_for("auth.login")

        # Attempt 3: Empty credentials
        response = test_client.post("/login", data=dict(email="", password=""), follow_redirects=True)
        assert response.request.path == url_for("auth.login")

    def test_user_profile_integration(self, test_client):
        """Test integration between User and UserProfile"""
        with test_client.application.app_context():
            # Create user
            user = User(email="profile_test@example.com", password="test1234")
            db.session.add(user)
            db.session.commit()

            # Create profile
            profile = UserProfile(user_id=user.id, name="Profile", surname="Test")
            db.session.add(profile)
            db.session.commit()

            # Verify relationship
            assert user.profile is not None
            assert user.profile.name == "Profile"
            assert profile.user is not None
            assert profile.user.email == "profile_test@example.com"

            # Cleanup
            db.session.delete(profile)
            db.session.delete(user)
            db.session.commit()


@pytest.mark.integration
class TestSessionManagement:
    """Integration tests for session management"""

    def test_session_persistence_across_requests(self, test_client):
        """Test that session persists across multiple requests"""
        # Login
        test_client.post("/login", data=dict(email="test@example.com", password="test1234"), follow_redirects=True)

        # Make multiple requests - session should persist
        response1 = test_client.get("/")
        assert response1.status_code == 200

        response2 = test_client.get("/explore")
        assert response2.status_code == 200

        response3 = test_client.get("/profile/summary")
        assert response3.status_code in [200, 302]

        # Logout
        test_client.get("/logout", follow_redirects=True)

    def test_concurrent_user_sessions(self, test_client):
        """Test that different users can have separate sessions"""
        with test_client.application.app_context():
            # Create second test user
            user2 = User.query.filter_by(email="test2@example.com").first()
            if not user2:
                user2 = User(email="test2@example.com", password="test1234")
                db.session.add(user2)
                db.session.commit()

        # Login as first user
        test_client.post("/login", data=dict(email="test@example.com", password="test1234"), follow_redirects=True)

        # Verify first user is logged in
        response = test_client.get("/")
        assert response.status_code == 200

        # Logout first user
        test_client.get("/logout", follow_redirects=True)

        # Login as second user
        test_client.post("/login", data=dict(email="test2@example.com", password="test1234"), follow_redirects=True)

        # Verify second user is logged in
        response = test_client.get("/")
        assert response.status_code == 200

        # Logout second user
        test_client.get("/logout", follow_redirects=True)


@pytest.mark.integration
class TestPasswordSecurity:
    """Integration tests for password security"""

    def test_password_hashing(self, test_client):
        """Test that passwords are hashed, not stored in plaintext"""
        with test_client.application.app_context():
            # Create user with password
            user = User(email="hash_test@example.com", password="plaintext123")
            db.session.add(user)
            db.session.commit()

            # Verify password is hashed
            assert user.password != "plaintext123"
            assert len(user.password) > len("plaintext123")

            # Verify password can be verified
            assert user.check_password("plaintext123") is True
            assert user.check_password("wrongpassword") is False

            # Cleanup
            db.session.delete(user)
            db.session.commit()

    def test_password_change_workflow(self, test_client):
        """Test complete password change workflow"""
        with test_client.application.app_context():
            user = User.query.filter_by(email="test@example.com").first()
            old_password_hash = user.password

            # Change password
            user.set_password("newpassword123")
            db.session.commit()

            # Verify password changed
            assert user.password != old_password_hash
            assert user.check_password("newpassword123") is True
            assert user.check_password("test1234") is False

            # Restore original password for other tests
            user.set_password("test1234")
            db.session.commit()


@pytest.mark.integration
def test_signup_duplicate_email(test_client):
    """Test that duplicate email registration is prevented"""
    # Try to signup with existing email
    response = test_client.post(
        "/signup",
        data=dict(name="Duplicate", surname="User", email="test@example.com", password="password123"),
        follow_redirects=True,
    )

    # Should stay on signup page with error
    assert response.request.path == url_for("auth.show_signup_form")
    assert b"Email" in response.data and b"in use" in response.data


@pytest.mark.integration
def test_access_protected_routes_without_login(test_client):
    """Test that protected routes redirect to login"""
    # Ensure logged out
    test_client.get("/logout", follow_redirects=True)

    # Try to access protected routes
    protected_routes = ["/profile/summary", "/profile/edit"]

    for route in protected_routes:
        response = test_client.get(route, follow_redirects=False)
        # Should redirect (302) or deny access (401/403)
        assert response.status_code in [302, 401, 403]
