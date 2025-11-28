import os
from datetime import datetime, timezone

import pytest

from app import create_app, db
from app.modules.auth.models import User
from app.modules.dataset.models import Author, DataSet, DSDownloadRecord, DSMetaData, DSViewRecord, PublicationType
from app.modules.featuremodel.models import FeatureModel, FMMetaData
from app.modules.profile.models import UserProfile

# Configure webdriver-manager to use only local cached drivers
os.environ["WDM_LOCAL"] = "1"


def pytest_configure(config):
    """Configure pytest for all tests."""
    # Ensure WDM uses local drivers only
    os.environ["WDM_LOCAL"] = "1"
    os.environ["WDM_SSL_VERIFY"] = "0"


@pytest.fixture(scope="session")
def test_app():
    """Create and configure a new app instance for each test session."""
    test_app = create_app("testing")

    with test_app.app_context():
        # Imprimir los blueprints registrados
        print("TESTING SUITE (1): Blueprints registrados:", test_app.blueprints)
        yield test_app


@pytest.fixture(scope="module")
def test_client(test_app):
    with test_app.test_client() as testing_client:
        with test_app.app_context():
            print("TESTING SUITE (2): Blueprints registrados:", test_app.blueprints)

            db.drop_all()
            db.create_all()
            """
            The test suite always includes the following user in order to avoid repetition
            of its creation
            """
            user_test = User(email="test@example.com", password="test1234")
            db.session.add(user_test)
            db.session.commit()

            # Create user profile for the test user
            profile = UserProfile(user_id=user_test.id, name="Test", surname="User")
            db.session.add(profile)
            db.session.commit()

            print("Rutas registradas:")
            for rule in test_app.url_map.iter_rules():
                print(rule)
            yield testing_client

            # Cleanup optimizado: solo cerrar sesión sin drop tables
            # Las tablas se eliminan automáticamente al final de la sesión de pytest
            db.session.remove()


@pytest.fixture(scope="function")
def clean_database():
    db.session.remove()
    db.drop_all()
    db.create_all()
    yield
    db.session.remove()
    db.drop_all()
    db.create_all()


@pytest.fixture(scope="function")
def integration_test_data(test_client):
    """Create test data for integration tests."""
    with test_client.application.app_context():
        # Crear usuario y perfil
        user1 = User(email="user1@example.com", password="test1234")
        db.session.add(user1)
        db.session.flush()  # Flush para obtener el ID sin commit

        profile1 = UserProfile(user_id=user1.id, name="User", surname="One")
        db.session.add(profile1)

        # Crear metadatos de datasets
        ds_meta1 = DSMetaData(
            title="Machine Learning Dataset",
            description="A dataset about machine learning patterns",
            publication_type=PublicationType.CONFERENCE_PAPER,
            dataset_doi="10.1234/ml.2024.001",
            tags="machine learning, patterns, software",
        )
        ds_meta2 = DSMetaData(
            title="Software Patterns Dataset",
            description="A dataset about software design patterns",
            publication_type=PublicationType.JOURNAL_ARTICLE,
            dataset_doi="10.1234/patterns.2024.002",
            tags="patterns, design, software",
        )
        ds_meta3 = DSMetaData(
            title="Unsynchronized Dataset",
            description="A dataset without DOI for testing",
            publication_type=PublicationType.WORKING_PAPER,
            dataset_doi=None,
            tags="testing, unsynchronized",
        )
        db.session.add_all([ds_meta1, ds_meta2, ds_meta3])
        db.session.flush()

        # Crear datasets
        dataset1 = DataSet(user_id=user1.id, ds_meta_data_id=ds_meta1.id, created_at=datetime.now(timezone.utc))
        dataset2 = DataSet(user_id=user1.id, ds_meta_data_id=ds_meta2.id, created_at=datetime.now(timezone.utc))
        dataset3 = DataSet(user_id=user1.id, ds_meta_data_id=ds_meta3.id, created_at=datetime.now(timezone.utc))
        db.session.add_all([dataset1, dataset2, dataset3])
        db.session.flush()

        # Crear metadatos de feature models
        fm_meta1 = FMMetaData(
            uvl_filename="model1.uvl",
            title="ML Feature Model",
            description="Feature model for machine learning",
            publication_type=PublicationType.CONFERENCE_PAPER,
            publication_doi="10.1234/fm.2024.001",
            tags="machine learning, features",
        )
        fm_meta2 = FMMetaData(
            uvl_filename="model2.uvl",
            title="Software Patterns Feature Model",
            description="Feature model for software patterns",
            publication_type=PublicationType.JOURNAL_ARTICLE,
            publication_doi="10.1234/fm.2024.002",
            tags="patterns, design, software",
        )
        fm_meta3 = FMMetaData(
            uvl_filename="model3.uvl",
            title="Unsync Feature Model",
            description="Feature model for unsynchronized dataset",
            publication_type=PublicationType.WORKING_PAPER,
            publication_doi=None,
            tags="testing, unsynchronized",
        )
        db.session.add_all([fm_meta1, fm_meta2, fm_meta3])
        db.session.flush()

        # Crear feature models
        fm1 = FeatureModel(data_set_id=dataset1.id, fm_meta_data_id=fm_meta1.id)
        fm2 = FeatureModel(data_set_id=dataset2.id, fm_meta_data_id=fm_meta2.id)
        fm3 = FeatureModel(data_set_id=dataset3.id, fm_meta_data_id=fm_meta3.id)
        db.session.add_all([fm1, fm2, fm3])

        # Crear autores
        author1 = Author(name="Jane Smith", affiliation="MIT", ds_meta_data_id=ds_meta1.id)
        author2 = Author(name="John Doe", affiliation="Stanford", ds_meta_data_id=ds_meta1.id)
        db.session.add_all([author1, author2])

        # Crear registros de descarga y visualización
        download_record = DSDownloadRecord(
            user_id=user1.id,
            dataset_id=dataset1.id,
            download_date=datetime.now(timezone.utc),
            download_cookie="test_cookie_123",
        )
        view_record = DSViewRecord(
            user_id=user1.id,
            dataset_id=dataset1.id,
            view_date=datetime.now(timezone.utc),
            view_cookie="test_view_cookie_123",
        )
        db.session.add_all([download_record, view_record])

        # Un solo commit para todos los datos
        db.session.commit()

        yield

        # Cleanup: eliminar datos creados para este test
        db.session.query(DSDownloadRecord).delete()
        db.session.query(DSViewRecord).delete()
        db.session.query(FeatureModel).delete()
        db.session.query(FMMetaData).delete()
        db.session.query(Author).delete()
        db.session.query(DataSet).delete()
        db.session.query(DSMetaData).delete()
        db.session.query(UserProfile).delete()
        db.session.query(User).filter_by(email="user1@example.com").delete()
        db.session.commit()


def login(test_client, email, password):
    """
    Authenticates the user with the credentials provided.

    Args:
        test_client: Flask test client.
        email (str): User's email address.
        password (str): User's password.

    Returns:
        response: POST login request response.
    """
    response = test_client.post("/login", data=dict(email=email, password=password), follow_redirects=True)
    return response


def logout(test_client):
    """
    Logs out the user.

    Args:
        test_client: Flask test client.

    Returns:
        response: Response to GET request to log out.
    """
    return test_client.get("/logout", follow_redirects=True)
