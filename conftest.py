import os
from datetime import datetime, timezone

import pytest

from app import create_app, db
from app.modules.auth.models import User
from app.modules.dataset.models import (
    Author,
    DataSource,
    DSDownloadRecord,
    DSMetaData,
    DSViewRecord,
    MaterialRecord,
    MaterialsDataset,
    PublicationType,
)
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


@pytest.fixture(scope="function")
def test_client(test_app):
    with test_app.test_client() as testing_client:
        with test_app.app_context():
            # Crear tablas de la base de datos
            db.create_all()

            # Limpiar sesión antes de crear nuevos datos
            db.session.expire_all()
            db.session.remove()

            # Crear usuario de test si no existe
            user_test = User.query.filter_by(email="test@example.com").first()
            if not user_test:
                user_test = User(email="test@example.com", password="test1234")
                db.session.add(user_test)
                db.session.commit()

                # Create user profile for the test user
                profile = UserProfile(user_id=user_test.id, name="Test", surname="User")
                db.session.add(profile)
                db.session.commit()

            yield testing_client

            # Cleanup: cerrar sesión
            db.session.expire_all()
            db.session.remove()


@pytest.fixture(scope="function")
def clean_database(test_app):
    with test_app.app_context():
        # Rollback any pending transactions
        db.session.rollback()
        db.session.remove()
        # Disable foreign key checks for MySQL
        db.session.execute(db.text("SET FOREIGN_KEY_CHECKS=0;"))
        db.session.commit()
        db.drop_all()
        db.session.execute(db.text("SET FOREIGN_KEY_CHECKS=1;"))
        db.session.commit()
        db.create_all()
        yield
        # Rollback any pending transactions
        db.session.rollback()
        db.session.remove()
        # Disable foreign key checks for MySQL
        db.session.execute(db.text("SET FOREIGN_KEY_CHECKS=0;"))
        db.session.commit()
        db.drop_all()
        db.session.execute(db.text("SET FOREIGN_KEY_CHECKS=1;"))
        db.session.commit()
        db.create_all()


@pytest.fixture(scope="function")
def integration_test_data(test_client):
    """Create test data for integration tests."""
    # Limpiar datos residuales antes de crear nuevos (por si quedaron de tests anteriores)
    # Primero identificar los datasets de test
    ds_meta_ids_subq = db.session.query(DSMetaData.id).filter(
        db.or_(DSMetaData.dataset_doi.like("10.1234/%"), DSMetaData.tags.like("%testing%"))
    ).scalar_subquery()
    test_dataset_ids_subq = db.session.query(MaterialsDataset.id).filter(
        MaterialsDataset.ds_meta_data_id.in_(ds_meta_ids_subq)
    ).scalar_subquery()

    # Borrar TODOS los records asociados con datasets de test
    db.session.query(DSDownloadRecord).filter(DSDownloadRecord.dataset_id.in_(test_dataset_ids_subq)).delete(
        synchronize_session=False
    )
    db.session.query(DSViewRecord).filter(DSViewRecord.dataset_id.in_(test_dataset_ids_subq)).delete(
        synchronize_session=False
    )

    # Borrar autores
    db.session.query(Author).filter(Author.affiliation.in_(["MIT", "Stanford"])).delete(synchronize_session=False)

    # Borrar MaterialRecords asociados a los datasets de test
    db.session.query(MaterialRecord).filter(
        MaterialRecord.materials_dataset_id.in_(test_dataset_ids_subq)
    ).delete(synchronize_session=False)

    # Borrar MaterialsDatasets
    db.session.query(MaterialsDataset).filter(
        MaterialsDataset.ds_meta_data_id.in_(ds_meta_ids_subq)
    ).delete(synchronize_session=False)

    # Ahora borrar los metadatos
    db.session.query(DSMetaData).filter(
        db.or_(DSMetaData.dataset_doi.like("10.1234/%"), DSMetaData.tags.like("%testing%"))
    ).delete(synchronize_session=False)

    # Finalmente borrar usuario y perfil
    db.session.query(UserProfile).filter(UserProfile.name == "User", UserProfile.surname == "One").delete(
        synchronize_session=False
    )
    db.session.query(User).filter(User.email == "user1@example.com").delete(synchronize_session=False)
    db.session.commit()

    # Crear usuario y perfil
    user1 = User(email="user1@example.com", password="test1234")
    db.session.add(user1)
    db.session.flush()  # Flush para obtener el ID

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
    dataset1 = MaterialsDataset(user_id=user1.id, ds_meta_data_id=ds_meta1.id, created_at=datetime.now(timezone.utc))
    dataset2 = MaterialsDataset(user_id=user1.id, ds_meta_data_id=ds_meta2.id, created_at=datetime.now(timezone.utc))
    dataset3 = MaterialsDataset(user_id=user1.id, ds_meta_data_id=ds_meta3.id, created_at=datetime.now(timezone.utc))
    db.session.add_all([dataset1, dataset2, dataset3])
    db.session.flush()

    # Crear material records para cada dataset
    material1 = MaterialRecord(
        materials_dataset_id=dataset1.id,
        material_name="Graphene",
        chemical_formula="C",
        structure_type="2D",
        property_name="Thermal Conductivity",
        property_value="5000",
        property_unit="W/mK",
        temperature=300,
        data_source=DataSource.EXPERIMENTAL,
        description="Machine learning model prediction for graphene",
    )
    material2 = MaterialRecord(
        materials_dataset_id=dataset1.id,
        material_name="Silicon",
        chemical_formula="Si",
        structure_type="Crystal",
        property_name="Band Gap",
        property_value="1.12",
        property_unit="eV",
        temperature=300,
        data_source=DataSource.COMPUTATIONAL,
        description="Computational study",
    )
    material3 = MaterialRecord(
        materials_dataset_id=dataset2.id,
        material_name="Steel Alloy",
        chemical_formula="Fe-C",
        structure_type="Metallic",
        property_name="Yield Strength",
        property_value="250",
        property_unit="MPa",
        temperature=298,
        data_source=DataSource.EXPERIMENTAL,
        description="Pattern analysis for steel",
    )
    material4 = MaterialRecord(
        materials_dataset_id=dataset3.id,
        material_name="Test Material",
        chemical_formula="XYZ",
        structure_type="Unknown",
        property_name="Test Property",
        property_value="100",
        property_unit="unit",
        data_source=DataSource.OTHER,
        description="Testing material",
    )
    db.session.add_all([material1, material2, material3, material4])

    # Crear autores
    author1 = Author(name="Jane Smith", affiliation="MIT", ds_meta_data_id=ds_meta1.id)
    author2 = Author(name="John Doe", affiliation="Stanford", ds_meta_data_id=ds_meta1.id)
    # Dataset2 también necesita un autor para aparecer en explore (join con authors)
    author3_ds2 = Author(name="Jane Smith", affiliation="MIT", ds_meta_data_id=ds_meta2.id)
    db.session.add_all([author1, author2, author3_ds2])

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

    # Commit para que los datos estén disponibles
    db.session.commit()

    yield

    # Cleanup: eliminar datos de test con synchronize_session=False para evitar errores
    try:
        # Expirar todos los objetos cached para evitar ObjectDeletedError
        db.session.expire_all()

        # Primero identificar los datasets de test
        ds_meta_ids = db.session.query(DSMetaData.id).filter(
            db.or_(DSMetaData.dataset_doi.like("10.1234/%"), DSMetaData.tags.like("%testing%"))
        ).scalar_subquery()
        test_dataset_ids = db.session.query(MaterialsDataset.id).filter(
            MaterialsDataset.ds_meta_data_id.in_(ds_meta_ids)
        ).scalar_subquery()

        # Borrar TODOS los records asociados con datasets de test (no solo los que tienen cookie de test)
        db.session.query(DSDownloadRecord).filter(DSDownloadRecord.dataset_id.in_(test_dataset_ids)).delete(
            synchronize_session=False
        )
        db.session.query(DSViewRecord).filter(DSViewRecord.dataset_id.in_(test_dataset_ids)).delete(
            synchronize_session=False
        )

        # Borrar autores
        db.session.query(Author).filter(Author.affiliation.in_(["MIT", "Stanford"])).delete(synchronize_session=False)

        # Borrar MaterialRecords asociados a los datasets de test
        db.session.query(MaterialRecord).filter(
            MaterialRecord.materials_dataset_id.in_(test_dataset_ids)
        ).delete(synchronize_session=False)

        # Borrar MaterialsDatasets
        db.session.query(MaterialsDataset).filter(
            MaterialsDataset.ds_meta_data_id.in_(ds_meta_ids)
        ).delete(synchronize_session=False)

        # Ahora borrar los metadatos
        db.session.query(DSMetaData).filter(
            db.or_(DSMetaData.dataset_doi.like("10.1234/%"), DSMetaData.tags.like("%testing%"))
        ).delete(synchronize_session=False)

        # Finalmente borrar usuario y perfil
        db.session.query(UserProfile).filter(UserProfile.name == "User", UserProfile.surname == "One").delete(
            synchronize_session=False
        )
        db.session.query(User).filter(User.email == "user1@example.com").delete(synchronize_session=False)
        db.session.commit()
    except Exception:
        # Si hay algún error en el cleanup, hacer rollback e intentar cerrar sesión limpiamente
        db.session.rollback()
        db.session.remove()


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
