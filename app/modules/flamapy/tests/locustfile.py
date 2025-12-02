"""
Locust load testing for flamapy module.

Usage:
    locust -f app/modules/flamapy/tests/locustfile.py --host=http://localhost:5000
"""

from locust import HttpUser, TaskSet, task

from core.environment.host import get_host_for_locust_testing


class FlamapyBehavior(TaskSet):
    """Flamapy testing behavior"""

    def on_start(self):
        self.check_uvl()

    @task
    def check_uvl(self):
        # Test check_uvl endpoint with file_id = 1
        response = self.client.get("/flamapy/check_uvl/1")

        if response.status_code not in [200, 404]:
            print(f"Flamapy check_uvl failed: {response.status_code}")

    @task
    def valid_uvl(self):
        # Test valid endpoint with file_id = 1
        response = self.client.get("/flamapy/valid/1")

        if response.status_code not in [200, 404]:
            print(f"Flamapy valid failed: {response.status_code}")


class FlamapyUser(HttpUser):
    """Load testing for Flamapy endpoints"""

    tasks = [FlamapyBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
