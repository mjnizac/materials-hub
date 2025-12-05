"""
Unit tests for core module (BaseRepository and BaseService).
"""

import pytest

from app import db
from app.modules.zenodo.models import Zenodo
from core.repositories.BaseRepository import BaseRepository
from core.services.BaseService import BaseService
from core.seeders.BaseSeeder import BaseSeeder


@pytest.mark.unit
def test_base_repository_initialization(test_client):
    """Test BaseRepository initialization."""
    repository = BaseRepository(Zenodo)
    assert repository.model == Zenodo
    assert repository.session == db.session


@pytest.mark.unit
def test_base_repository_create(test_client):
    """Test BaseRepository create method."""
    repository = BaseRepository(Zenodo)
    instance = repository.create()

    assert instance.id is not None
    assert isinstance(instance, Zenodo)


@pytest.mark.unit
def test_base_repository_create_no_commit(test_client):
    """Test BaseRepository create method without committing."""
    repository = BaseRepository(Zenodo)
    instance = repository.create(commit=False)

    # Instance should exist but not be committed yet
    assert instance is not None
    db.session.commit()  # Commit manually
    assert instance.id is not None


@pytest.mark.unit
def test_base_repository_get_by_id(test_client):
    """Test BaseRepository get_by_id method."""
    repository = BaseRepository(Zenodo)
    created = repository.create()

    retrieved = repository.get_by_id(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id


@pytest.mark.unit
def test_base_repository_get_by_id_not_found(test_client):
    """Test BaseRepository get_by_id with non-existent ID."""
    repository = BaseRepository(Zenodo)
    result = repository.get_by_id(99999)

    assert result is None


@pytest.mark.unit
def test_base_repository_count(test_client):
    """Test BaseRepository count method."""
    repository = BaseRepository(Zenodo)

    initial_count = repository.count()
    repository.create()
    repository.create()

    final_count = repository.count()

    assert final_count == initial_count + 2


@pytest.mark.unit
def test_base_repository_update(test_client):
    """Test BaseRepository update method."""
    repository = BaseRepository(Zenodo)
    instance = repository.create()

    # Zenodo model only has id, so we can't update other fields
    # This test just verifies the update method works
    updated = repository.update(instance.id)

    assert updated is not None
    assert updated.id == instance.id


@pytest.mark.unit
def test_base_repository_update_not_found(test_client):
    """Test BaseRepository update with non-existent ID."""
    repository = BaseRepository(Zenodo)
    result = repository.update(99999)

    assert result is None


@pytest.mark.unit
def test_base_repository_delete(test_client):
    """Test BaseRepository delete method."""
    repository = BaseRepository(Zenodo)
    instance = repository.create()
    instance_id = instance.id

    result = repository.delete(instance_id)

    assert result is True
    assert repository.get_by_id(instance_id) is None


@pytest.mark.unit
def test_base_repository_delete_not_found(test_client):
    """Test BaseRepository delete with non-existent ID."""
    repository = BaseRepository(Zenodo)
    result = repository.delete(99999)

    assert result is False


@pytest.mark.unit
def test_base_service_initialization(test_client):
    """Test BaseService initialization."""
    repository = BaseRepository(Zenodo)
    service = BaseService(repository)

    assert service.repository == repository


@pytest.mark.unit
def test_base_service_create(test_client):
    """Test BaseService create method."""
    repository = BaseRepository(Zenodo)
    service = BaseService(repository)

    instance = service.create()

    assert instance.id is not None
    assert isinstance(instance, Zenodo)


@pytest.mark.unit
def test_base_service_get_by_id(test_client):
    """Test BaseService get_by_id method."""
    repository = BaseRepository(Zenodo)
    service = BaseService(repository)

    created = service.create()
    retrieved = service.get_by_id(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id


@pytest.mark.unit
def test_base_service_count(test_client):
    """Test BaseService count method."""
    repository = BaseRepository(Zenodo)
    service = BaseService(repository)

    initial_count = service.count()
    service.create()
    service.create()

    final_count = service.count()

    assert final_count == initial_count + 2


@pytest.mark.unit
def test_base_service_update(test_client):
    """Test BaseService update method."""
    repository = BaseRepository(Zenodo)
    service = BaseService(repository)

    instance = service.create()
    updated = service.update(instance.id)

    assert updated is not None
    assert updated.id == instance.id


@pytest.mark.unit
def test_base_service_delete(test_client):
    """Test BaseService delete method."""
    repository = BaseRepository(Zenodo)
    service = BaseService(repository)

    instance = service.create()
    instance_id = instance.id

    result = service.delete(instance_id)

    assert result is True
    assert service.get_by_id(instance_id) is None


@pytest.mark.unit
def test_base_service_get_or_404(test_client):
    """Test BaseService get_or_404 method."""
    repository = BaseRepository(Zenodo)
    service = BaseService(repository)

    instance = service.create()
    retrieved = service.get_or_404(instance.id)

    assert retrieved is not None
    assert retrieved.id == instance.id


@pytest.mark.unit
def test_base_repository_get_by_column(test_client):
    """Test BaseRepository get_by_column method."""
    from app.modules.auth.models import User

    repository = BaseRepository(User)

    # Create users with specific emails
    user1 = repository.create(email="test1@example.com", password="pass1")
    user2 = repository.create(email="test2@example.com", password="pass2")
    user3 = repository.create(email="test1@example.com", password="pass3")  # Duplicate email

    # Get by email column
    results = repository.get_by_column("email", "test1@example.com")

    assert len(results) == 2
    assert user1 in results
    assert user3 in results
    assert user2 not in results


@pytest.mark.unit
def test_base_repository_delete_by_column(test_client):
    """Test BaseRepository delete_by_column method."""
    from app.modules.auth.models import User

    repository = BaseRepository(User)

    # Create users
    repository.create(email="delete@example.com", password="pass1")
    repository.create(email="delete@example.com", password="pass2")
    repository.create(email="keep@example.com", password="pass3")

    initial_count = repository.count()

    # Delete by email column
    result = repository.delete_by_column("email", "delete@example.com")

    assert result is True
    assert repository.count() == initial_count - 2

    # Verify they're gone
    remaining = repository.get_by_column("email", "delete@example.com")
    assert len(remaining) == 0

    # Verify other user still exists
    kept = repository.get_by_column("email", "keep@example.com")
    assert len(kept) == 1


@pytest.mark.unit
def test_base_repository_get_or_404_success(test_client):
    """Test BaseRepository get_or_404 method with existing ID."""
    repository = BaseRepository(Zenodo)
    instance = repository.create()

    retrieved = repository.get_or_404(instance.id)

    assert retrieved is not None
    assert retrieved.id == instance.id


# ===========================
# BaseSeeder Tests
# ===========================


@pytest.mark.unit
def test_base_seeder_initialization(test_client):
    """Test BaseSeeder initialization."""
    seeder = BaseSeeder()
    assert seeder.db == db
    assert seeder.priority == 10


@pytest.mark.unit
def test_base_seeder_run_not_implemented(test_client):
    """Test BaseSeeder run method raises NotImplementedError."""
    seeder = BaseSeeder()
    with pytest.raises(NotImplementedError, match="The 'run' method must be implemented by the child class."):
        seeder.run()


@pytest.mark.unit
def test_base_seeder_seed_empty_data(test_client):
    """Test BaseSeeder seed method with empty data."""
    seeder = BaseSeeder()
    result = seeder.seed([])
    assert result == []


@pytest.mark.unit
def test_base_seeder_seed_valid_data(test_client):
    """Test BaseSeeder seed method with valid data."""
    seeder = BaseSeeder()

    # Create test data
    zenodos = [Zenodo(), Zenodo(), Zenodo()]

    result = seeder.seed(zenodos)

    assert len(result) == 3
    assert all(z.id is not None for z in result)
    assert all(isinstance(z, Zenodo) for z in result)


@pytest.mark.unit
def test_base_seeder_seed_mixed_types_error(test_client):
    """Test BaseSeeder seed method with mixed model types."""
    from app.modules.auth.models import User

    seeder = BaseSeeder()

    # Mix different model types
    mixed_data = [Zenodo(), User()]

    with pytest.raises(ValueError, match="All objects must be of the same model."):
        seeder.seed(mixed_data)


@pytest.mark.unit
def test_base_seeder_seed_integrity_error(test_client):
    """Test BaseSeeder seed method handles IntegrityError."""
    from app.modules.auth.models import User

    seeder = BaseSeeder()

    # Create user with duplicate email (violates unique constraint)
    user1 = User(email="duplicate@example.com", password="pass1")
    seeder.seed([user1])

    # Try to create another user with same email
    user2 = User(email="duplicate@example.com", password="pass2")

    with pytest.raises(Exception, match="Failed to insert data into `user` table"):
        seeder.seed([user2])
