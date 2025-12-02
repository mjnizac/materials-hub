"""
Locust load testing for dataset module.

Usage:
    locust -f app/modules/dataset/tests/locustfile.py --host=http://localhost:5000
"""

from locust import HttpUser, TaskSet, between, task

from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token


class DatasetUploadBehavior(TaskSet):
    """
    Simulates users uploading and managing datasets (heavy operations).
    """

    def on_start(self):
        """Login before starting"""
        self.client.post(
            "/login",
            data={"email": "test@example.com", "password": "test1234"},
        )

    @task(3)
    def view_upload_form(self):
        """View the dataset upload form"""
        self.client.get("/dataset/upload")

    @task(2)
    def view_my_datasets(self):
        """View user's own datasets"""
        self.client.get("/dataset/list")

    @task(1)
    def view_dataset_detail(self):
        """View dataset details"""
        dataset_id = 1
        self.client.get(f"/dataset/view/{dataset_id}")


class APIUserBehavior(TaskSet):
    """
    Simulates API consumers making requests to API endpoints.
    """

    @task(5)
    def api_list_datasets(self):
        """List datasets via API"""
        self.client.get("/api/v1/datasets/", name="/api/v1/datasets/")

    @task(3)
    def api_get_dataset(self):
        """Get specific dataset via API"""
        dataset_id = 1
        self.client.get(f"/api/v1/datasets/{dataset_id}", name="/api/v1/datasets/[id]")

    @task(2)
    def api_search_datasets(self):
        """Search datasets via API"""
        self.client.get("/api/v1/datasets/?query=test", name="/api/v1/datasets/?query=[q]")


class DatasetUploader(HttpUser):
    """
    Represents users uploading and managing datasets.

    Weight: 15 (less common, heavier operations)
    Wait time: 3-8 seconds between tasks
    """

    tasks = [DatasetUploadBehavior]
    weight = 15
    wait_time = between(3, 8)


class APIUser(HttpUser):
    """
    Represents API consumers making programmatic requests.

    Weight: 5 (least common)
    Wait time: 0.5-2 seconds (APIs are used by programs, faster)
    """

    tasks = [APIUserBehavior]
    weight = 5
    wait_time = between(0.5, 2)


# ============================================================================
# Alternative dataset tests with CSRF token handling
# ============================================================================


class DatasetBehavior(TaskSet):
    """Alternative dataset behavior with CSRF token handling"""

    def on_start(self):
        # Login first since dataset upload requires authentication
        self.login()

    def login(self):
        """Login before accessing dataset upload"""
        # Ensure logged out first
        self.client.get("/logout")
        response = self.client.get("/login")

        # Check if we can see the login form
        if "Login" not in response.text:
            print("Cannot access login page, may be already logged in")
            return

        try:
            csrf_token = get_csrf_token(response)
            self.client.post(
                "/login", data={"email": "user1@example.com", "password": "1234", "csrf_token": csrf_token}
            )
        except ValueError:
            print("CSRF token not found, login may fail")

    @task
    def dataset(self):
        # Access dataset upload page (requires login)
        response = self.client.get("/dataset/upload")

        # If not logged in, try login again
        if response.status_code == 302 or "Login" in response.text:
            self.login()
            response = self.client.get("/dataset/upload")


class DatasetUser(HttpUser):
    """Load testing for dataset upload functionality with CSRF handling"""

    tasks = [DatasetBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
