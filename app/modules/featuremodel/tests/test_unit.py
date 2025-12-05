"""
Unit tests for featuremodel module.
"""

import pytest

from app import db
from app.modules.dataset.models import PublicationType
from app.modules.featuremodel.models import FeatureModel, FMMetaData, FMMetrics
from app.modules.featuremodel.repositories import FeatureModelRepository, FMMetaDataRepository
from app.modules.featuremodel.services import FeatureModelService


@pytest.mark.unit
def test_feature_model_creation(test_client):
    """Test FeatureModel can be created and saved"""
    fm_metadata = FMMetaData(
        uvl_filename="test.uvl",
        title="Test Feature Model",
        description="Test description",
        publication_type=PublicationType.NONE,
    )
    db.session.add(fm_metadata)
    db.session.commit()

    feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
    db.session.add(feature_model)
    db.session.commit()

    assert feature_model.id is not None
    assert feature_model.fm_meta_data_id == fm_metadata.id


@pytest.mark.unit
def test_feature_model_repr(test_client):
    """Test FeatureModel __repr__ method"""
    fm_metadata = FMMetaData(
        uvl_filename="test.uvl", title="Test", description="Test", publication_type=PublicationType.NONE
    )
    db.session.add(fm_metadata)
    db.session.commit()

    feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
    db.session.add(feature_model)
    db.session.commit()

    assert repr(feature_model) == f"FeatureModel<{feature_model.id}>"


@pytest.mark.unit
def test_fm_metadata_creation(test_client):
    """Test FMMetaData can be created and saved"""
    fm_metadata = FMMetaData(
        uvl_filename="test.uvl",
        title="Test Feature Model",
        description="Test description",
        publication_type=PublicationType.NONE,
        tags="test,feature",
    )
    db.session.add(fm_metadata)
    db.session.commit()

    assert fm_metadata.id is not None
    assert fm_metadata.title == "Test Feature Model"
    assert fm_metadata.tags == "test,feature"


@pytest.mark.unit
def test_fm_metadata_repr(test_client):
    """Test FMMetaData __repr__ method"""
    fm_metadata = FMMetaData(
        uvl_filename="test.uvl", title="My Feature Model", description="Test", publication_type=PublicationType.NONE
    )
    db.session.add(fm_metadata)
    db.session.commit()

    assert repr(fm_metadata) == "FMMetaData<My Feature Model"


@pytest.mark.unit
def test_fm_metrics_creation(test_client):
    """Test FMMetrics can be created and saved"""
    metrics = FMMetrics(solver="SAT", not_solver="UNSAT")
    db.session.add(metrics)
    db.session.commit()

    assert metrics.id is not None
    assert metrics.solver == "SAT"
    assert metrics.not_solver == "UNSAT"


@pytest.mark.unit
def test_fm_metrics_repr(test_client):
    """Test FMMetrics __repr__ method"""
    metrics = FMMetrics(solver="SAT", not_solver="UNSAT")
    db.session.add(metrics)
    db.session.commit()

    assert repr(metrics) == "FMMetrics<solver=SAT, not_solver=UNSAT>"


@pytest.mark.unit
def test_feature_model_repository_initialization():
    """Test FeatureModelRepository initializes correctly"""
    repository = FeatureModelRepository()
    assert repository is not None
    assert repository.model == FeatureModel


@pytest.mark.unit
def test_feature_model_repository_count_feature_models(test_client):
    """Test count_feature_models method"""
    repository = FeatureModelRepository()

    # Get initial count
    initial_count = repository.count_feature_models()

    # Create feature models
    for i in range(3):
        fm_metadata = FMMetaData(
            uvl_filename=f"test{i}.uvl", title=f"Test {i}", description="Test", publication_type=PublicationType.NONE
        )
        db.session.add(fm_metadata)
        db.session.commit()

        feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
        db.session.add(feature_model)
        db.session.commit()

    # Count should have increased
    final_count = repository.count_feature_models()
    assert final_count >= initial_count + 3


@pytest.mark.unit
def test_fm_metadata_repository_initialization():
    """Test FMMetaDataRepository initializes correctly"""
    repository = FMMetaDataRepository()
    assert repository is not None
    assert repository.model == FMMetaData


@pytest.mark.unit
def test_feature_model_service_initialization():
    """Test FeatureModelService initializes correctly"""
    service = FeatureModelService()
    assert service is not None
    assert isinstance(service.repository, FeatureModelRepository)


@pytest.mark.unit
def test_feature_model_service_count_feature_models(test_client):
    """Test FeatureModelService count_feature_models method"""
    service = FeatureModelService()

    initial_count = service.count_feature_models()

    # Create a feature model
    fm_metadata = FMMetaData(
        uvl_filename="count_test.uvl", title="Count Test", description="Test", publication_type=PublicationType.NONE
    )
    db.session.add(fm_metadata)
    db.session.commit()

    feature_model = FeatureModel(fm_meta_data_id=fm_metadata.id)
    db.session.add(feature_model)
    db.session.commit()

    final_count = service.count_feature_models()
    assert final_count >= initial_count + 1


@pytest.mark.unit
def test_fm_metadata_with_metrics(test_client):
    """Test FMMetaData with FMMetrics relationship"""
    metrics = FMMetrics(solver="Z3", not_solver="None")
    db.session.add(metrics)
    db.session.commit()

    fm_metadata = FMMetaData(
        uvl_filename="metrics_test.uvl",
        title="Metrics Test",
        description="Test with metrics",
        publication_type=PublicationType.NONE,
        fm_metrics_id=metrics.id,
    )
    db.session.add(fm_metadata)
    db.session.commit()

    assert fm_metadata.fm_metrics_id == metrics.id
    assert fm_metadata.fm_metrics == metrics
