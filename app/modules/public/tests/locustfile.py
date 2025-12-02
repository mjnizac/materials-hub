"""
Locust load testing for public module.

Usage:
    locust -f app/modules/public/tests/locustfile.py --host=http://localhost:5000
"""

from locust import HttpUser, TaskSet, between, task


class PublicUserBehavior(TaskSet):
    """
    Simulates behavior of anonymous users browsing the public website.
    """

    @task(5)
    def view_homepage(self):
        """Visit the homepage (most common action)"""
        self.client.get("/")

    @task(3)
    def browse_datasets(self):
        """Browse datasets in explore page"""
        self.client.get("/explore")

    @task(2)
    def search_datasets(self):
        """Search for datasets with various queries"""
        queries = ["machine learning", "data science", "materials", "test"]
        for query in queries:
            self.client.get(f"/explore?query={query}")

    @task(1)
    def view_dataset_detail(self):
        """View a specific dataset detail page"""
        # Assuming dataset IDs start from 1
        dataset_id = 1
        self.client.get(f"/dataset/view/{dataset_id}")

    @task(1)
    def view_signup_page(self):
        """View the signup page"""
        self.client.get("/signup")

    @task(1)
    def view_login_page(self):
        """View the login page"""
        self.client.get("/login")


class PublicUser(HttpUser):
    """
    Represents an anonymous public user browsing the website.

    Weight: 50 (most common user type)
    Wait time: 1-5 seconds between tasks (realistic browsing)
    """

    tasks = [PublicUserBehavior]
    weight = 50
    wait_time = between(1, 5)


class StressTestUser(HttpUser):
    """
    Stress test user - makes rapid requests to stress the system.
    Use sparingly to test system limits.

    Usage:
        locust -f app/modules/public/tests/locustfile.py --host=http://localhost:5000 StressTestUser
    """

    wait_time = between(0.1, 0.5)  # Very short wait times

    @task(10)
    def rapid_homepage_requests(self):
        """Make rapid homepage requests"""
        self.client.get("/")

    @task(5)
    def rapid_explore_requests(self):
        """Make rapid explore page requests"""
        self.client.get("/explore")

    @task(3)
    def rapid_search_requests(self):
        """Make rapid search requests"""
        self.client.get("/explore?query=test")
