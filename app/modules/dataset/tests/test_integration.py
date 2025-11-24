"""
Integration tests for dataset module.

Tests the full workflow of dataset operations including creation, retrieval,
update, and deletion with real database interactions.
"""

import pytest
from flask import url_for

from app import db
from app.modules.auth.models import User
from app.modules.dataset.models import Author, DataSet, DSMetaData, PublicationType
from app.modules.dataset.services import DataSetService


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Create test user for dataset ownership
        user = User.query.filter_by(email="test@example.com").first()
        if not user:
            user = User(email="test@example.com", password="test1234")
            db.session.add(user)
            db.session.commit()

    yield test_client


@pytest.mark.integration
class TestDataSetIntegration:
    """Integration tests for DataSet CRUD operations"""

    def test_create_dataset_full_workflow(self, test_client):
        """Test creating a complete dataset with metadata and authors"""
        with test_client.application.app_context():
            # Step 1: Create user
            user = User.query.filter_by(email="integration@example.com").first()
            if not user:
                user = User(email="integration@example.com", password="test1234")
                db.session.add(user)
                db.session.commit()

            # Step 2: Create authors
            author1 = Author(name="John Doe", affiliation="Test University", orcid="0000-0001-2345-6789")
            author2 = Author(name="Jane Smith", affiliation="Research Institute")
            db.session.add(author1)
            db.session.add(author2)
            db.session.commit()

            # Step 3: Create metadata
            metadata = DSMetaData(
                title="Integration Test Dataset",
                description="This is a test dataset for integration testing",
                publication_type=PublicationType.DATA_MANAGEMENT_PLAN,
                tags="test, integration, dataset",
            )
            metadata.authors.append(author1)
            metadata.authors.append(author2)
            db.session.add(metadata)
            db.session.commit()

            # Step 4: Create dataset
            dataset = DataSet(user_id=user.id, ds_meta_data_id=metadata.id)
            db.session.add(dataset)
            db.session.commit()

            # Verify all relationships
            assert dataset.id is not None
            assert dataset.user_id == user.id
            assert dataset.ds_meta_data.title == "Integration Test Dataset"
            assert len(dataset.ds_meta_data.authors) == 2
            assert dataset.ds_meta_data.authors[0].name == "John Doe"

            # Cleanup
            db.session.delete(dataset)
            db.session.delete(metadata)
            db.session.delete(author1)
            db.session.delete(author2)
            db.session.commit()

    def test_dataset_service_integration(self, test_client):
        """Test DataSetService operations with real database"""
        with test_client.application.app_context():
            service = DataSetService()

            # Create test data
            user = User.query.filter_by(email="test@example.com").first()

            author = Author(name="Service Test Author", affiliation="Test Org")
            db.session.add(author)
            db.session.commit()

            metadata = DSMetaData(
                title="Service Integration Test",
                description="Testing service methods",
                publication_type=PublicationType.NONE,
            )
            metadata.authors.append(author)
            db.session.add(metadata)
            db.session.commit()

            dataset = DataSet(user_id=user.id, ds_meta_data_id=metadata.id)
            db.session.add(dataset)
            db.session.commit()

            # Test service methods
            retrieved = service.get_by_id(dataset.id)
            assert retrieved is not None
            assert retrieved.id == dataset.id

            # Cleanup
            db.session.delete(dataset)
            db.session.delete(metadata)
            db.session.delete(author)
            db.session.commit()

    def test_author_metadata_relationship(self, test_client):
        """Test many-to-many relationship between authors and metadata"""
        with test_client.application.app_context():
            # Create multiple authors
            authors = [
                Author(name=f"Author {i}", affiliation=f"University {i}", orcid=f"0000-0001-0000-000{i}")
                for i in range(3)
            ]
            for author in authors:
                db.session.add(author)
            db.session.commit()

            # Create metadata with multiple authors
            metadata = DSMetaData(
                title="Multi-author Dataset",
                description="Testing author relationships",
                publication_type=PublicationType.NONE,
            )
            for author in authors:
                metadata.authors.append(author)
            db.session.add(metadata)
            db.session.commit()

            # Verify relationships
            assert len(metadata.authors) == 3
            for i, author in enumerate(metadata.authors):
                assert author.name == f"Author {i}"

            # Cleanup
            db.session.delete(metadata)
            for author in authors:
                db.session.delete(author)
            db.session.commit()


@pytest.mark.integration
class TestAuthenticationDatasetIntegration:
    """Integration tests between authentication and dataset modules"""

    def test_user_dataset_ownership(self, test_client):
        """Test that datasets are correctly associated with users"""
        with test_client.application.app_context():
            user = User.query.filter_by(email="test@example.com").first()

            # Create dataset owned by user
            metadata = DSMetaData(
                title="User Ownership Test",
                description="Testing user-dataset relationship",
                publication_type=PublicationType.NONE,
            )
            db.session.add(metadata)
            db.session.commit()

            dataset = DataSet(user_id=user.id, ds_meta_data_id=metadata.id)
            db.session.add(dataset)
            db.session.commit()

            # Verify ownership
            assert dataset.user_id == user.id
            user_datasets = DataSet.query.filter_by(user_id=user.id).all()
            assert len(user_datasets) > 0
            assert any(ds.id == dataset.id for ds in user_datasets)

            # Cleanup
            db.session.delete(dataset)
            db.session.delete(metadata)
            db.session.commit()

    def test_login_and_create_dataset_workflow(self, test_client):
        """Test complete workflow: login -> create dataset -> verify"""
        # Login
        response = test_client.post(
            "/login", data=dict(email="test@example.com", password="test1234"), follow_redirects=True
        )
        assert response.request.path != url_for("auth.login")

        with test_client.application.app_context():
            user = User.query.filter_by(email="test@example.com").first()

            # Create dataset while logged in
            metadata = DSMetaData(
                title="Logged-in User Dataset",
                description="Created by authenticated user",
                publication_type=PublicationType.NONE,
            )
            db.session.add(metadata)
            db.session.commit()

            dataset = DataSet(user_id=user.id, ds_meta_data_id=metadata.id)
            db.session.add(dataset)
            db.session.commit()

            # Verify dataset exists
            assert dataset.id is not None

            # Cleanup
            db.session.delete(dataset)
            db.session.delete(metadata)
            db.session.commit()

        # Logout
        test_client.get("/logout", follow_redirects=True)


@pytest.mark.integration
class TestDatasetPublicationTypeIntegration:
    """Integration tests for different publication types"""

    def test_create_datasets_with_all_publication_types(self, test_client):
        """Test creating datasets with each publication type"""
        with test_client.application.app_context():
            user = User.query.filter_by(email="test@example.com").first()

            publication_types = [
                PublicationType.NONE,
                PublicationType.ANNOTATION_COLLECTION,
                PublicationType.BOOK,
                PublicationType.BOOK_SECTION,
                PublicationType.CONFERENCE_PAPER,
                PublicationType.DATA_MANAGEMENT_PLAN,
            ]

            created_datasets = []

            for pub_type in publication_types:
                metadata = DSMetaData(
                    title=f"Dataset with {pub_type.value}",
                    description=f"Testing {pub_type.value} type",
                    publication_type=pub_type,
                )
                db.session.add(metadata)
                db.session.commit()

                dataset = DataSet(user_id=user.id, ds_meta_data_id=metadata.id)
                db.session.add(dataset)
                db.session.commit()

                created_datasets.append((dataset, metadata))

                # Verify publication type
                assert dataset.ds_meta_data.publication_type == pub_type

            # Cleanup
            for dataset, metadata in created_datasets:
                db.session.delete(dataset)
                db.session.delete(metadata)
            db.session.commit()


@pytest.mark.integration
def test_dataset_search_integration(test_client):
    """Test dataset search functionality across the application"""
    with test_client.application.app_context():
        user = User.query.filter_by(email="test@example.com").first()

        # Create searchable dataset
        metadata = DSMetaData(
            title="Searchable Machine Learning Dataset",
            description="A dataset about machine learning and AI",
            publication_type=PublicationType.NONE,
            tags="machine-learning, ai, test",
        )
        db.session.add(metadata)
        db.session.commit()

        dataset = DataSet(user_id=user.id, ds_meta_data_id=metadata.id)
        db.session.add(dataset)
        db.session.commit()

    # Search for dataset (outside app_context to avoid conflicts)
    response = test_client.get("/explore?query=machine+learning")
    assert response.status_code == 200

    # Cleanup
    with test_client.application.app_context():
        db.session.delete(dataset)
        db.session.delete(metadata)
        db.session.commit()
