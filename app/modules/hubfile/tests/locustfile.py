"""
Locust load testing for hubfile module.

Usage:
    locust -f app/modules/hubfile/tests/locustfile.py --host=http://localhost:5000
"""

from locust import HttpUser, TaskSet, task

from core.environment.host import get_host_for_locust_testing


class HubfileBehavior(TaskSet):
    """Hubfile testing behavior"""

    def on_start(self):
        self.view_file()

    @task
    def view_file(self):
        # Test file view endpoint with file_id = 1
        response = self.client.get("/file/view/1")

        if response.status_code not in [200, 404]:
            print(f"Hubfile view failed: {response.status_code}")

    @task
    def download_file(self):
        # Test file download endpoint with file_id = 1
        response = self.client.get("/file/download/1")

        if response.status_code not in [200, 404]:
            print(f"Hubfile download failed: {response.status_code}")


class HubfileUser(HttpUser):
    """Load testing for file view/download endpoints"""

    tasks = [HubfileBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
