"""
Locust load testing for auth module.

Usage:
    locust -f app/modules/auth/tests/locustfile.py --host=http://localhost:5000
"""

from locust import HttpUser, TaskSet, between, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import fake, get_csrf_token


class AuthenticatedUserBehavior(TaskSet):
    """
    Simulates behavior of logged-in users performing authenticated actions.
    """

    def on_start(self):
        """Called when a simulated user starts - performs login"""
        self.login()

    def login(self):
        """Attempt to login with test credentials"""
        response = self.client.post(
            "/login",
            data={"email": "test@example.com", "password": "test1234"},
            allow_redirects=True,
        )
        if response.status_code == 200:
            print("Login successful")
        else:
            print(f"Login failed: {response.status_code}")

    @task(5)
    def view_homepage(self):
        """Visit homepage as authenticated user"""
        self.client.get("/")

    @task(4)
    def view_profile(self):
        """View user profile"""
        self.client.get("/profile/summary")

    @task(3)
    def browse_datasets(self):
        """Browse datasets"""
        self.client.get("/explore")

    @task(2)
    def search_datasets(self):
        """Search for datasets"""
        queries = ["test", "example", "data"]
        for query in queries:
            self.client.get(f"/explore?query={query}")

    @task(1)
    def view_own_datasets(self):
        """View own uploaded datasets (if route exists)"""
        self.client.get("/dataset/list")

    def on_stop(self):
        """Called when a simulated user stops - performs logout"""
        self.client.get("/logout")


class AuthenticatedUser(HttpUser):
    """
    Represents a logged-in user using the application.

    Weight: 30 (common user type)
    Wait time: 2-6 seconds between tasks
    """

    tasks = [AuthenticatedUserBehavior]
    weight = 30
    wait_time = between(2, 6)


# ============================================================================
# Alternative authentication tests with CSRF token handling
# ============================================================================


class SignupBehavior(TaskSet):
    """Alternative signup behavior with CSRF token handling"""

    def on_start(self):
        # Logout first to ensure we can access signup page
        self.client.get("/logout")
        self.signup()

    @task
    def signup(self):
        # Ensure logged out before signup
        self.client.get("/logout")

        response = self.client.get("/signup")

        # Check if we can see the signup form
        if "Sign up" not in response.text and "Signup" not in response.text:
            print("Cannot access signup page, may be redirected")
            return

        csrf_token = get_csrf_token(response)

        response = self.client.post(
            "/signup", data={"email": fake.email(), "password": fake.password(), "csrf_token": csrf_token}
        )
        if response.status_code != 200:
            print(f"Signup failed: {response.status_code}")


class LoginBehavior(TaskSet):
    """Alternative login behavior with CSRF token handling"""

    def on_start(self):
        # Always logout first to ensure clean state
        self.client.get("/logout")
        self.login()

    def ensure_logged_out(self):
        """Ensure user is logged out before attempting login"""
        self.client.get("/logout")

    @task
    def login(self):
        # First, ensure we're logged out
        self.ensure_logged_out()

        response = self.client.get("/login")

        # Check if we were redirected (already logged in somehow)
        if "Login" not in response.text:
            print("Already logged in, forcing logout...")
            self.ensure_logged_out()
            response = self.client.get("/login")

        csrf_token = get_csrf_token(response)

        response = self.client.post(
            "/login", data={"email": "user1@example.com", "password": "1234", "csrf_token": csrf_token}
        )
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")


class AuthUser(HttpUser):
    """Load testing for authentication endpoints (login/signup) with CSRF handling"""

    tasks = [SignupBehavior, LoginBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
