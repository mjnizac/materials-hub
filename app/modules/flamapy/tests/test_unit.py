"""
Unit tests for flamapy module.
"""

import pytest

from app import db
from app.modules.flamapy.models import Flamapy
from app.modules.flamapy.repositories import FlamapyRepository
from app.modules.flamapy.services import FlamapyService


# ===========================
# Flamapy Model Tests
# ===========================


@pytest.mark.unit
def test_flamapy_creation(test_client):
    """Test Flamapy can be created and saved"""
    flamapy = Flamapy()
    db.session.add(flamapy)
    db.session.commit()

    assert flamapy.id is not None


@pytest.mark.unit
def test_flamapy_repr(test_client):
    """Test Flamapy __repr__ method"""
    flamapy = Flamapy()
    db.session.add(flamapy)
    db.session.commit()

    assert repr(flamapy) == f"<Flamapy {flamapy.id}>"


# ===========================
# FlamapyRepository Tests
# ===========================


@pytest.mark.unit
def test_flamapy_repository_initialization():
    """Test FlamapyRepository initializes correctly"""
    repository = FlamapyRepository()
    assert repository is not None
    assert repository.model == Flamapy


# ===========================
# FlamapyService Tests
# ===========================


@pytest.mark.unit
def test_flamapy_service_initialization():
    """Test FlamapyService initializes correctly"""
    service = FlamapyService()
    assert service is not None
    assert isinstance(service.repository, FlamapyRepository)
