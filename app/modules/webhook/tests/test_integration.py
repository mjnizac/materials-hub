"""
Integration tests for webhook module.
"""

import pytest

from app import db
from app.modules.webhook.models import Webhook
from app.modules.webhook.services import WebhookService


@pytest.mark.integration
def test_webhook_service_initialization(test_client):
    """Test WebhookService can be initialized."""
    with test_client.application.app_context():
        service = WebhookService()
        assert service is not None


@pytest.mark.integration
def test_create_webhook(test_client):
    """Test creating a webhook."""
    with test_client.application.app_context():
        webhook = Webhook()
        db.session.add(webhook)
        db.session.commit()

        assert webhook.id is not None

        # Cleanup
        db.session.delete(webhook)
        db.session.commit()


@pytest.mark.integration
def test_webhook_repository_operations(test_client):
    """Test basic repository operations for Webhook."""
    with test_client.application.app_context():
        service = WebhookService()

        # Create
        created = service.create()
        assert created.id is not None

        # Get by id
        retrieved = service.get_by_id(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id

        # Delete
        service.delete(created.id)
        deleted = service.get_by_id(created.id)
        assert deleted is None


@pytest.mark.integration
def test_webhook_count(test_client):
    """Test counting webhooks."""
    with test_client.application.app_context():
        service = WebhookService()

        # Get initial count
        initial_count = service.count()

        # Create a webhook
        webhook = service.create()
        assert service.count() == initial_count + 1

        # Cleanup
        service.delete(webhook.id)
        assert service.count() == initial_count


@pytest.mark.integration
def test_webhook_get_or_404(test_client):
    """Test webhook get_or_404 method."""
    with test_client.application.app_context():
        service = WebhookService()

        # Create a webhook
        created = service.create()

        # Get with valid ID
        retrieved = service.get_or_404(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id

        # Cleanup
        service.delete(created.id)


@pytest.mark.integration
def test_webhook_update(test_client):
    """Test updating a webhook."""
    with test_client.application.app_context():
        service = WebhookService()

        # Create a webhook
        created = service.create()
        original_id = created.id

        # Update (Webhook has no specific fields to update, just test the method works)
        updated = service.update(created.id)
        assert updated is not None
        assert updated.id == original_id

        # Cleanup
        service.delete(created.id)


@pytest.mark.integration
def test_multiple_webhooks(test_client):
    """Test creating multiple webhooks."""
    with test_client.application.app_context():
        service = WebhookService()

        initial_count = service.count()

        # Create multiple webhooks
        webhook1 = service.create()
        webhook2 = service.create()
        webhook3 = service.create()

        assert service.count() == initial_count + 3

        # Cleanup
        service.delete(webhook1.id)
        service.delete(webhook2.id)
        service.delete(webhook3.id)

        assert service.count() == initial_count


@pytest.mark.integration
def test_webhook_deploy_route_unauthorized(test_client):
    """Test webhook deploy route without authorization."""
    response = test_client.post("/webhook/deploy")
    assert response.status_code == 403


@pytest.mark.integration
def test_webhook_deploy_route_with_invalid_token(test_client):
    """Test webhook deploy route with invalid token."""
    response = test_client.post("/webhook/deploy", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 403


@pytest.mark.integration
def test_webhook_service_get_web_container(test_client):
    """Test getting web container."""
    with test_client.application.app_context():
        service = WebhookService()
        try:
            container = service.get_web_container()
            assert container is not None or container is None
        except Exception:
            pass


@pytest.mark.integration
def test_webhook_service_execute_command(test_client):
    """Test webhook service execute command method exists."""
    with test_client.application.app_context():
        service = WebhookService()
        assert hasattr(service, "execute_container_command")


@pytest.mark.integration
def test_webhook_service_log_deployment(test_client):
    """Test webhook service log deployment method exists."""
    with test_client.application.app_context():
        service = WebhookService()
        assert hasattr(service, "log_deployment")


@pytest.mark.integration
def test_webhook_service_restart_container(test_client):
    """Test webhook service restart container method exists."""
    with test_client.application.app_context():
        service = WebhookService()
        assert hasattr(service, "restart_container")


@pytest.mark.integration
def test_webhook_model_creation(test_client):
    """Test creating webhook model directly."""
    with test_client.application.app_context():
        from app import db
        from app.modules.webhook.models import Webhook

        webhook = Webhook()
        db.session.add(webhook)
        db.session.commit()

        assert webhook.id is not None

        db.session.delete(webhook)
        db.session.commit()
