"""
Unit tests for webhook module.
"""
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import docker
import pytest
from wtforms import SubmitField

from app import db
from app.modules.webhook.forms import WebhookForm
from app.modules.webhook.models import Webhook
from app.modules.webhook.repositories import WebhookRepository
from app.modules.webhook.services import WebhookService


@pytest.mark.unit
def test_webhook_model_creation(test_client):
    """
    Test that Webhook model can be created and saved to database.
    """
    with test_client.application.app_context():
        webhook = Webhook()
        db.session.add(webhook)
        db.session.commit()

        assert webhook.id is not None, "Webhook model should have an ID after commit"

        # Cleanup
        db.session.delete(webhook)
        db.session.commit()


@pytest.mark.unit
def test_webhook_repository_initialization():
    """
    Test that WebhookRepository initializes correctly.
    """
    repository = WebhookRepository()
    assert repository is not None
    assert repository.model == Webhook


@pytest.mark.unit
def test_webhook_service_initialization():
    """
    Test that WebhookService initializes correctly.
    """
    service = WebhookService()
    assert service is not None
    assert isinstance(service.repository, WebhookRepository)


@pytest.mark.unit
def test_webhook_service_get_volume_name():
    """
    Test WebhookService get_volume_name method.
    """
    service = WebhookService()
    mock_container = Mock()
    mock_container.attrs = {"Mounts": [{"Destination": "/app", "Name": "test_volume"}]}

    volume_name = service.get_volume_name(mock_container)
    assert volume_name == "test_volume"


@pytest.mark.unit
def test_webhook_service_get_volume_name_with_source():
    """
    Test WebhookService get_volume_name method with Source instead of Name.
    """
    service = WebhookService()
    mock_container = Mock()
    mock_container.attrs = {"Mounts": [{"Destination": "/app", "Source": "/host/path"}]}

    volume_name = service.get_volume_name(mock_container)
    assert volume_name == "/host/path"


@pytest.mark.unit
def test_webhook_service_get_volume_name_not_found():
    """
    Test WebhookService get_volume_name method when volume not found.
    """
    service = WebhookService()
    mock_container = Mock()
    mock_container.attrs = {"Mounts": [{"Destination": "/other", "Name": "other_volume"}]}

    with pytest.raises(ValueError, match="No volume or bind mount found mounted on /app"):
        service.get_volume_name(mock_container)


@pytest.mark.unit
def test_webhook_form_initialization(test_client):
    """
    Test that WebhookForm initializes correctly.
    """

    with test_client.application.app_context():
        form = WebhookForm()

        assert form is not None
        assert hasattr(form, "submit")
        assert isinstance(form.submit, SubmitField)


@pytest.mark.unit
def test_webhook_service_get_web_container_not_found():
    """
    Test WebhookService get_web_container when container not found.
    """
    service = WebhookService()

    with patch("app.modules.webhook.services.client.containers.get") as mock_get:
        mock_get.side_effect = docker.errors.NotFound("Container not found")

        with pytest.raises(Exception):  # abort raises an exception
            service.get_web_container()


@pytest.mark.unit
def test_webhook_service_execute_container_command_success():
    """
    Test WebhookService execute_container_command with successful command.
    """
    service = WebhookService()
    mock_container = Mock()
    mock_container.exec_run.return_value = (0, b"Command output")

    result = service.execute_container_command(mock_container, "echo test")

    assert result == "Command output"
    mock_container.exec_run.assert_called_once_with("echo test", workdir="/app")


@pytest.mark.unit
def test_webhook_service_execute_container_command_failure():
    """
    Test WebhookService execute_container_command with failed command.
    """
    service = WebhookService()
    mock_container = Mock()
    mock_container.exec_run.return_value = (1, b"Error message")

    with pytest.raises(Exception):  # abort raises an exception
        service.execute_container_command(mock_container, "false")


@pytest.mark.unit
def test_webhook_service_log_deployment():
    """
    Test WebhookService log_deployment method.
    """
    service = WebhookService()
    mock_container = Mock()
    mock_container.exec_run.return_value = (0, b"")

    with patch("app.modules.webhook.services.datetime") as mock_datetime:
        fixed_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = fixed_time

        service.log_deployment(mock_container)

        mock_container.exec_run.assert_called_once()
        call_args = mock_container.exec_run.call_args[0][0]
        assert "Deployment successful" in call_args
        assert "/app/deployments.log" in call_args


@pytest.mark.unit
def test_webhook_service_restart_container():
    """
    Test WebhookService restart_container method.
    """
    service = WebhookService()
    mock_container = Mock()
    mock_container.id = "container_123"

    with patch("app.modules.webhook.services.subprocess.Popen") as mock_popen:
        service.restart_container(mock_container)

        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        assert call_args[0] == "/bin/sh"
        assert "/app/scripts/restart_container.sh" in call_args
        assert "container_123" in call_args
