import logging

from flask import render_template

from app.modules.dataset.repositories import (
    DSDownloadRecordRepository,
    DSViewRecordRepository,
    MaterialsDatasetRepository,
)
from app.modules.public import public_bp

logger = logging.getLogger(__name__)


@public_bp.route("/")
def index():
    logger.info("Access index")
    materials_dataset_repository = MaterialsDatasetRepository()
    download_repository = DSDownloadRecordRepository()
    view_repository = DSViewRecordRepository()

    # Statistics: materials datasets
    datasets_counter = materials_dataset_repository.count_synchronized()
    latest_materials_datasets = materials_dataset_repository.get_synchronized_latest(limit=5)

    # Statistics: total downloads and views
    total_dataset_downloads = download_repository.count()
    total_dataset_views = view_repository.count()

    return render_template(
        "public/index.html",
        latest_materials_datasets=latest_materials_datasets,
        datasets_counter=datasets_counter,
        materials_datasets_counter=datasets_counter,
        feature_models_counter=0,
        total_dataset_downloads=total_dataset_downloads,
        total_dataset_views=total_dataset_views,
        total_feature_model_views=0,
        total_feature_model_downloads=0,
    )
