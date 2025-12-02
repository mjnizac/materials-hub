"""
Main Locust load testing file for Materials Hub.

This file aggregates all load testing scenarios from different modules
to run comprehensive load tests on the entire application.

Usage:
    # Run all load tests with web UI
    locust --host=http://localhost:5000

    # Run headless with specific configuration
    locust --host=http://localhost:5000 --users 100 --spawn-rate 10 --run-time 1m --headless

    # Run specific user type
    locust --host=http://localhost:5000 PublicUser

    # Generate HTML report
    locust --host=http://localhost:5000 --users 100 --spawn-rate 10 --run-time 2m --headless \
           --html reports/locust_report.html

Module-specific tests:
    # Test only public module
    locust -f app/modules/public/tests/locustfile.py --host=http://localhost:5000

    # Test only auth module
    locust -f app/modules/auth/tests/locustfile.py --host=http://localhost:5000

    # Test only dataset module
    locust -f app/modules/dataset/tests/locustfile.py --host=http://localhost:5000

    # Test only featuremodel module
    locust -f app/modules/featuremodel/tests/locustfile.py --host=http://localhost:5000

    # Test only flamapy module
    locust -f app/modules/flamapy/tests/locustfile.py --host=http://localhost:5000

    # Test only hubfile module
    locust -f app/modules/hubfile/tests/locustfile.py --host=http://localhost:5000

Access web UI at: http://localhost:8089
"""

# Import all user classes from module-specific locust files
from app.modules.auth.tests.locustfile import AuthenticatedUser, AuthUser
from app.modules.dataset.tests.locustfile import APIUser, DatasetUploader, DatasetUser
from app.modules.featuremodel.tests.locustfile import FeaturemodelUser
from app.modules.flamapy.tests.locustfile import FlamapyUser
from app.modules.hubfile.tests.locustfile import HubfileUser
from app.modules.public.tests.locustfile import PublicUser, StressTestUser

# All user classes are automatically registered by Locust when imported
# The weight parameter in each class determines the proportion of each user type

__all__ = [
    "PublicUser",  # Weight: 50 - most common
    "AuthenticatedUser",  # Weight: 30 - common
    "DatasetUploader",  # Weight: 15 - less common
    "APIUser",  # Weight: 5 - least common
    "AuthUser",  # With CSRF token handling
    "DatasetUser",  # With CSRF token handling
    "FeaturemodelUser",  # Feature model specific
    "FlamapyUser",  # Flamapy specific
    "HubfileUser",  # File operations
    "StressTestUser",  # No default weight - use explicitly
]
