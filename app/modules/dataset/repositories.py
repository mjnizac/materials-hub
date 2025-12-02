import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from flask_login import current_user
from sqlalchemy import and_, desc, func

from app.modules.dataset.models import (
    Author,
    DOIMapping,
    DSDownloadRecord,
    DSMetaData,
    DSViewRecord,
    MaterialRecord,
    MaterialsDataset,
)
from core.repositories.BaseRepository import BaseRepository

logger = logging.getLogger(__name__)


class AuthorRepository(BaseRepository):
    def __init__(self):
        super().__init__(Author)


class DSDownloadRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSDownloadRecord)

    def total_dataset_downloads(self) -> int:
        max_id = self.model.query.with_entities(func.max(self.model.id)).scalar()
        return max_id if max_id is not None else 0


class DSMetaDataRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSMetaData)

    def filter_by_doi(self, doi: str) -> Optional[DSMetaData]:
        return self.model.query.filter_by(dataset_doi=doi).first()


class DSViewRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSViewRecord)

    def total_dataset_views(self) -> int:
        max_id = self.model.query.with_entities(func.max(self.model.id)).scalar()
        return max_id if max_id is not None else 0

    def the_record_exists(self, dataset: MaterialsDataset, user_cookie: str):
        return self.model.query.filter_by(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset.id,
            view_cookie=user_cookie,
        ).first()

    def create_new_record(self, dataset: MaterialsDataset, user_cookie: str) -> DSViewRecord:
        return self.create(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset.id,
            view_date=datetime.now(timezone.utc),
            view_cookie=user_cookie,
        )


class DOIMappingRepository(BaseRepository):
    def __init__(self):
        super().__init__(DOIMapping)

    def get_new_doi(self, old_doi: str) -> str:
        return self.model.query.filter_by(dataset_doi_old=old_doi).first()


class MaterialsDatasetRepository(BaseRepository):
    def __init__(self):
        super().__init__(MaterialsDataset)

    def get_by_user(self, user_id: int):
        """Get all materials datasets for a specific user"""
        return self.model.query.filter_by(user_id=user_id).order_by(desc(self.model.created_at)).all()

    def get_synchronized(self, current_user_id: int):
        """Get synchronized materials datasets (with DOI)"""
        return (
            self.model.query.join(DSMetaData)
            .filter(MaterialsDataset.user_id == current_user_id, DSMetaData.dataset_doi.isnot(None))
            .order_by(self.model.created_at.desc())
            .all()
        )

    def get_unsynchronized(self, current_user_id: int):
        """Get unsynchronized materials datasets (without DOI)"""
        return (
            self.model.query.join(DSMetaData)
            .filter(MaterialsDataset.user_id == current_user_id, DSMetaData.dataset_doi.is_(None))
            .order_by(self.model.created_at.desc())
            .all()
        )

    def count_by_user(self, user_id: int) -> int:
        """Count materials datasets for a user"""
        return self.model.query.filter_by(user_id=user_id).count()

    def count_all(self) -> int:
        """Count all materials datasets"""
        return self.model.query.count()

    def count_synchronized(self) -> int:
        """Count synchronized materials datasets (with DOI)"""
        return self.model.query.join(DSMetaData).filter(DSMetaData.dataset_doi.isnot(None)).count()

    def get_synchronized_latest(self, limit: int = 5):
        """Get latest synchronized materials datasets (with DOI)"""
        return (
            self.model.query.join(DSMetaData)
            .filter(DSMetaData.dataset_doi.isnot(None))
            .order_by(desc(self.model.created_at))
            .limit(limit)
            .all()
        )

    def get_all(self):
        """Get all materials datasets ordered by creation date (newest first)"""
        return self.model.query.order_by(desc(self.model.created_at)).all()

    def get_top_downloads_global(self, limit: int = 10, days: int = 30):
        """
        Top global por descargas en los últimos 'days' días para MaterialsDataset.
        Incluye datasets con 0 descargas en el rango (outer join).
        """
        from app.modules.dataset.models import DSDownloadRecord, DSMetaData, MaterialsDataset

        since = datetime.now(timezone.utc) - timedelta(days=days)

        q = (
            self.model.query.join(DSMetaData, DSMetaData.id == MaterialsDataset.ds_meta_data_id)
            .outerjoin(
                DSDownloadRecord,
                and_(
                    DSDownloadRecord.dataset_id == MaterialsDataset.id,
                    DSDownloadRecord.download_date >= since,
                ),
            )
            .with_entities(
                MaterialsDataset.id.label("dataset_id"),
                DSMetaData.title.label("title"),
                DSMetaData.dataset_doi.label("doi"),
                func.coalesce(func.count(DSDownloadRecord.id), 0).label("downloads"),
            )
            .filter(DSMetaData.dataset_doi.isnot(None))
            .group_by(MaterialsDataset.id, DSMetaData.title, DSMetaData.dataset_doi)
            .order_by(func.coalesce(func.count(DSDownloadRecord.id), 0).desc())
            .limit(limit)
        )
        return q.all()

    def get_top_views_global(self, limit: int = 10, days: int = 30):
        """
        Top global por vistas en los últimos 'days' días para MaterialsDataset.
        Incluye datasets con 0 vistas en el rango (outer join).
        """
        from app.modules.dataset.models import DSMetaData, DSViewRecord, MaterialsDataset

        since = datetime.now(timezone.utc) - timedelta(days=days)

        q = (
            self.model.query.join(DSMetaData, DSMetaData.id == MaterialsDataset.ds_meta_data_id)
            .outerjoin(
                DSViewRecord,
                and_(
                    DSViewRecord.dataset_id == MaterialsDataset.id,
                    DSViewRecord.view_date >= since,
                ),
            )
            .with_entities(
                MaterialsDataset.id.label("dataset_id"),
                DSMetaData.title.label("title"),
                DSMetaData.dataset_doi.label("doi"),
                func.coalesce(func.count(DSViewRecord.id), 0).label("views"),
            )
            .filter(DSMetaData.dataset_doi.isnot(None))
            .group_by(MaterialsDataset.id, DSMetaData.title, DSMetaData.dataset_doi)
            .order_by(func.coalesce(func.count(DSViewRecord.id), 0).desc())
            .limit(limit)
        )
        return q.all()


class MaterialRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(MaterialRecord)

    def get_by_dataset(self, dataset_id: int):
        """Get all material records for a specific dataset"""
        return self.model.query.filter_by(materials_dataset_id=dataset_id).all()

    def get_by_material_name(self, dataset_id: int, material_name: str):
        """Get all records for a specific material in a dataset"""
        return self.model.query.filter_by(materials_dataset_id=dataset_id, material_name=material_name).all()

    def get_by_property_name(self, dataset_id: int, property_name: str):
        """Get all records for a specific property in a dataset"""
        return self.model.query.filter_by(materials_dataset_id=dataset_id, property_name=property_name).all()

    def search_materials(self, dataset_id: int, search_term: str):
        """Search materials by name or chemical formula"""
        return self.model.query.filter(
            self.model.materials_dataset_id == dataset_id,
            (self.model.material_name.ilike(f"%{search_term}%"))
            | (self.model.chemical_formula.ilike(f"%{search_term}%")),
        ).all()

    def filter_by_temperature_range(self, dataset_id: int, min_temp: int = None, max_temp: int = None):
        """Filter records by temperature range"""
        query = self.model.query.filter_by(materials_dataset_id=dataset_id)

        if min_temp is not None:
            query = query.filter(self.model.temperature >= min_temp)
        if max_temp is not None:
            query = query.filter(self.model.temperature <= max_temp)

        return query.all()

    def get_unique_materials(self, dataset_id: int):
        """Get unique material names in a dataset"""
        return (
            self.model.query.filter_by(materials_dataset_id=dataset_id)
            .with_entities(self.model.material_name)
            .distinct()
            .all()
        )

    def get_unique_properties(self, dataset_id: int):
        """Get unique property names in a dataset"""
        return (
            self.model.query.filter_by(materials_dataset_id=dataset_id)
            .with_entities(self.model.property_name)
            .distinct()
            .all()
        )

    def count_by_dataset(self, dataset_id: int) -> int:
        """Count records in a dataset"""
        return self.model.query.filter_by(materials_dataset_id=dataset_id).count()
