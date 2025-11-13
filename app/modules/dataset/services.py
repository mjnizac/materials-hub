import hashlib
import logging
import os
import shutil
import uuid
from typing import Optional

from flask import request

from app.modules.auth.services import AuthenticationService
from app.modules.dataset.models import DataSet, DSMetaData, DSViewRecord
from app.modules.dataset.repositories import (
    AuthorRepository,
    DataSetRepository,
    DOIMappingRepository,
    DSDownloadRecordRepository,
    DSMetaDataRepository,
    DSViewRecordRepository,
)
from app.modules.featuremodel.repositories import FeatureModelRepository, FMMetaDataRepository
from app.modules.hubfile.repositories import (
    HubfileDownloadRecordRepository,
    HubfileRepository,
    HubfileViewRecordRepository,
)
from core.services.BaseService import BaseService

logger = logging.getLogger(__name__)


def calculate_checksum_and_size(file_path):
    file_size = os.path.getsize(file_path)
    with open(file_path, "rb") as file:
        content = file.read()
        hash_md5 = hashlib.md5(content).hexdigest()
        return hash_md5, file_size


class DataSetService(BaseService):
    def __init__(self):
        super().__init__(DataSetRepository())
        self.feature_model_repository = FeatureModelRepository()
        self.author_repository = AuthorRepository()
        self.dsmetadata_repository = DSMetaDataRepository()
        self.fmmetadata_repository = FMMetaDataRepository()
        self.dsdownloadrecord_repository = DSDownloadRecordRepository()
        self.hubfiledownloadrecord_repository = HubfileDownloadRecordRepository()
        self.hubfilerepository = HubfileRepository()
        self.dsviewrecord_repostory = DSViewRecordRepository()
        self.hubfileviewrecord_repository = HubfileViewRecordRepository()

    def move_feature_models(self, dataset: DataSet):
        current_user = AuthenticationService().get_authenticated_user()
        source_dir = current_user.temp_folder()

        working_dir = os.getenv("WORKING_DIR", "")
        dest_dir = os.path.join(working_dir, "uploads", f"user_{current_user.id}", f"dataset_{dataset.id}")

        os.makedirs(dest_dir, exist_ok=True)

        for feature_model in dataset.feature_models:
            uvl_filename = feature_model.fm_meta_data.uvl_filename
            shutil.move(os.path.join(source_dir, uvl_filename), dest_dir)

    def get_synchronized(self, current_user_id: int) -> DataSet:
        return self.repository.get_synchronized(current_user_id)

    def get_unsynchronized(self, current_user_id: int) -> DataSet:
        return self.repository.get_unsynchronized(current_user_id)

    def get_unsynchronized_dataset(self, current_user_id: int, dataset_id: int) -> DataSet:
        return self.repository.get_unsynchronized_dataset(current_user_id, dataset_id)

    def latest_synchronized(self):
        return self.repository.latest_synchronized()

    def count_synchronized_datasets(self):
        return self.repository.count_synchronized_datasets()

    def count_feature_models(self):
        return self.feature_model_service.count_feature_models()

    def count_authors(self) -> int:
        return self.author_repository.count()

    def count_dsmetadata(self) -> int:
        return self.dsmetadata_repository.count()

    def total_dataset_downloads(self) -> int:
        return self.dsdownloadrecord_repository.total_dataset_downloads()

    def total_dataset_views(self) -> int:
        return self.dsviewrecord_repostory.total_dataset_views()

    def get_recommendations(self, dataset_id: int, limit: int = 3):
        """
        CAMBIO: Obtiene datasets recomendados basados en similitud de tags,
        tipo de publicación y autor.

        Args:
            dataset_id: ID del dataset actual
            limit: Número máximo de recomendaciones (default: 3)

        Returns:
            Lista de DataSet ordenados por relevancia
        """
        try:
            # Obtener el dataset actual
            current_dataset = self.repository.get_or_404(dataset_id)

            # Verificar que tenga metadata y tags
            if not current_dataset.ds_meta_data or not current_dataset.ds_meta_data.tags:
                # Si no tiene tags, retornar datasets recientes
                return DataSet.query.filter(
                    DataSet.id != dataset_id,
                    DataSet.ds_meta_data_id.isnot(None)
                ).order_by(DataSet.created_at.desc()).limit(limit).all()

            # Obtener tags del dataset actual
            current_tags = set(tag.strip().lower() for tag in current_dataset.ds_meta_data.tags.split(','))

            # Obtener todos los demás datasets
            all_datasets = DataSet.query.filter(
                DataSet.id != dataset_id,
                DataSet.ds_meta_data_id.isnot(None)
            ).all()

            # Calcular puntuación de similitud para cada dataset
            recommendations = []
            for dataset in all_datasets:
                score = 0

                # Verificar que tenga metadata válida
                if not dataset.ds_meta_data:
                    continue

                # 1. Similitud de tags (peso: 3 puntos por cada tag común)
                if dataset.ds_meta_data.tags:
                    dataset_tags = set(tag.strip().lower() for tag in dataset.ds_meta_data.tags.split(','))
                    common_tags = current_tags.intersection(dataset_tags)
                    score += len(common_tags) * 3

                # 2. Mismo tipo de publicación (peso: 2 puntos)
                if (hasattr(dataset.ds_meta_data, 'publication_type') and
                        hasattr(current_dataset.ds_meta_data, 'publication_type') and
                        dataset.ds_meta_data.publication_type == current_dataset.ds_meta_data.publication_type):
                    score += 2

                # 3. Mismo autor (peso: 1 punto)
                if dataset.user_id == current_dataset.user_id:
                    score += 1

                # Solo añadir si tiene alguna puntuación
                if score > 0:
                    recommendations.append((dataset, score))

            # Ordenar por puntuación descendente
            recommendations.sort(key=lambda x: x[1], reverse=True)

            # Obtener los mejores resultados
            result = [rec[0] for rec in recommendations[:limit]]

            # Si no hay suficientes recomendaciones, completar con datasets recientes
            if len(result) < limit:
                recent_datasets = DataSet.query.filter(
                    DataSet.id != dataset_id,
                    DataSet.ds_meta_data_id.isnot(None)
                ).order_by(DataSet.created_at.desc()).limit(limit - len(result)).all()

                # Añadir solo los que no estén ya en result
                result_ids = {d.id for d in result}
                for dataset in recent_datasets:
                    if dataset.id not in result_ids:
                        result.append(dataset)
                        if len(result) >= limit:
                            break

            return result[:limit]

        except Exception as e:
            logger.exception(f"Error getting recommendations for dataset {dataset_id}: {e}")
            # En caso de error, retornar lista vacía
            return []

    def get_all_except(self, dataset_id: int):
        """
        Obtiene todos los datasets excepto el especificado.

        Args:
            dataset_id: ID del dataset a excluir

        Returns:
            Lista de DataSet
        """
        return DataSet.query.filter(
            DataSet.id != dataset_id,
            DataSet.ds_meta_data_id.isnot(None)
        ).all()

    def filter_by_authors(self, datasets, current_dataset):
        """
        Filtra datasets que comparten autores con el dataset actual.

        Args:
            datasets: Lista de datasets a filtrar
            current_dataset: Dataset de referencia

        Returns:
            Lista filtrada de datasets
        """
        if not current_dataset.ds_meta_data or not current_dataset.ds_meta_data.authors:
            return []

        current_authors = {a.name.strip().lower() for a in current_dataset.ds_meta_data.authors}

        return [
            ds for ds in datasets
            if ds.ds_meta_data
            and ds.ds_meta_data.authors
            and any(a.name.strip().lower() in current_authors for a in ds.ds_meta_data.authors)
        ]

    def filter_by_tags(self, datasets, current_dataset):
        """
        Filtra datasets que comparten tags con el dataset actual.

        Args:
            datasets: Lista de datasets a filtrar
            current_dataset: Dataset de referencia

        Returns:
            Lista filtrada de datasets
        """
        if not current_dataset.ds_meta_data or not current_dataset.ds_meta_data.tags:
            return []

        current_tags = {t.strip().lower() for t in current_dataset.ds_meta_data.tags.split(",")}

        return [
            ds for ds in datasets
            if ds.ds_meta_data
            and ds.ds_meta_data.tags
            and any(t.strip().lower() in current_tags for t in ds.ds_meta_data.tags.split(","))
        ]

    def filter_by_community(self, datasets, current_dataset):
        """
        Filtra datasets que pertenecen a la misma comunidad.

        Args:
            datasets: Lista de datasets a filtrar
            current_dataset: Dataset de referencia

        Returns:
            Lista filtrada de datasets
        """
        if not hasattr(current_dataset, 'community_id') or not current_dataset.community_id:
            return []

        return [
            ds for ds in datasets
            if hasattr(ds, 'community_id') and ds.community_id == current_dataset.community_id
        ]

    def create_from_form(self, form, current_user) -> DataSet:
        main_author = {
            "name": f"{current_user.profile.surname}, {current_user.profile.name}",
            "affiliation": current_user.profile.affiliation,
            "orcid": current_user.profile.orcid,
        }
        try:
            logger.info(f"Creating dsmetadata...: {form.get_dsmetadata()}")
            dsmetadata = self.dsmetadata_repository.create(**form.get_dsmetadata())
            for author_data in [main_author] + form.get_authors():
                author = self.author_repository.create(commit=False, ds_meta_data_id=dsmetadata.id, **author_data)
                dsmetadata.authors.append(author)

            dataset = self.create(commit=False, user_id=current_user.id, ds_meta_data_id=dsmetadata.id)

            for feature_model in form.feature_models:
                uvl_filename = feature_model.uvl_filename.data
                fmmetadata = self.fmmetadata_repository.create(commit=False, **feature_model.get_fmmetadata())
                for author_data in feature_model.get_authors():
                    author = self.author_repository.create(commit=False, fm_meta_data_id=fmmetadata.id, **author_data)
                    fmmetadata.authors.append(author)

                fm = self.feature_model_repository.create(
                    commit=False, data_set_id=dataset.id, fm_meta_data_id=fmmetadata.id
                )

                # associated files in feature model
                file_path = os.path.join(current_user.temp_folder(), uvl_filename)
                checksum, size = calculate_checksum_and_size(file_path)

                file = self.hubfilerepository.create(
                    commit=False, name=uvl_filename, checksum=checksum, size=size, feature_model_id=fm.id
                )
                fm.files.append(file)
            self.repository.session.commit()
        except Exception as exc:
            logger.info(f"Exception creating dataset from form...: {exc}")
            self.repository.session.rollback()
            raise exc
        return dataset

    def update_dsmetadata(self, id, **kwargs):
        return self.dsmetadata_repository.update(id, **kwargs)

    def get_uvlhub_doi(self, dataset: DataSet) -> str:
        domain = os.getenv("DOMAIN", "localhost")
        return f"http://{domain}/doi/{dataset.ds_meta_data.dataset_doi}"

    def get_top_global(self, metric: str = "downloads", limit: int = 10, days: int = 30):
        """
        Devuelve el top global según métrica ('downloads'|'views'), límite y rango de días (7|30).
        """
        metric = (metric or "downloads").lower()
        if metric == "views":
            return self.repository.get_top_views_global(limit=limit, days=days)
        return self.repository.get_top_downloads_global(limit=limit, days=days)


class AuthorService(BaseService):
    def __init__(self):
        super().__init__(AuthorRepository())


class DSDownloadRecordService(BaseService):
    def __init__(self):
        super().__init__(DSDownloadRecordRepository())


class DSMetaDataService(BaseService):
    def __init__(self):
        super().__init__(DSMetaDataRepository())

    def update(self, id, **kwargs):
        return self.repository.update(id, **kwargs)

    def filter_by_doi(self, doi: str) -> Optional[DSMetaData]:
        return self.repository.filter_by_doi(doi)


class DSViewRecordService(BaseService):
    def __init__(self):
        super().__init__(DSViewRecordRepository())

    def the_record_exists(self, dataset: DataSet, user_cookie: str):
        return self.repository.the_record_exists(dataset, user_cookie)

    def create_new_record(self, dataset: DataSet, user_cookie: str) -> DSViewRecord:
        return self.repository.create_new_record(dataset, user_cookie)

    def create_cookie(self, dataset: DataSet) -> str:

        user_cookie = request.cookies.get("view_cookie")
        if not user_cookie:
            user_cookie = str(uuid.uuid4())

        existing_record = self.the_record_exists(dataset=dataset, user_cookie=user_cookie)

        if not existing_record:
            self.create_new_record(dataset=dataset, user_cookie=user_cookie)

        return user_cookie


class DOIMappingService(BaseService):
    def __init__(self):
        super().__init__(DOIMappingRepository())

    def get_new_doi(self, old_doi: str) -> str:
        doi_mapping = self.repository.get_new_doi(old_doi)
        if doi_mapping:
            return doi_mapping.dataset_doi_new
        else:
            return None


class SizeService:

    def __init__(self):
        pass

    def get_human_readable_size(self, size: int) -> str:
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024**2:
            return f"{round(size / 1024, 2)} KB"
        elif size < 1024**3:
            return f"{round(size / (1024 ** 2), 2)} MB"
        else:
            return f"{round(size / (1024 ** 3), 2)} GB"
