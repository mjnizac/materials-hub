import csv
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


class MaterialsDatasetService:
    """Service for handling MaterialsDataset operations including CSV parsing"""

    # Expected CSV columns (exact names)
    REQUIRED_COLUMNS = [
        'material_name',
        'property_name',
        'property_value'
    ]

    OPTIONAL_COLUMNS = [
        'chemical_formula',
        'structure_type',
        'composition_method',
        'property_unit',
        'temperature',
        'pressure',
        'data_source',
        'uncertainty',
        'description'
    ]

    def __init__(self):
        from app.modules.dataset.repositories import MaterialsDatasetRepository, MaterialRecordRepository
        self.materials_dataset_repository = MaterialsDatasetRepository()
        self.material_record_repository = MaterialRecordRepository()

    def validate_csv_columns(self, csv_columns: list) -> dict:
        """
        Validates that CSV has required columns and identifies optional ones.

        Args:
            csv_columns: List of column names from CSV header

        Returns:
            dict with 'valid' (bool), 'missing_required' (list), 'extra_columns' (list)
        """
        csv_columns_set = set(csv_columns)
        required_set = set(self.REQUIRED_COLUMNS)
        optional_set = set(self.OPTIONAL_COLUMNS)
        all_valid_columns = required_set | optional_set

        # Check for missing required columns
        missing_required = list(required_set - csv_columns_set)

        # Check for extra/unknown columns
        extra_columns = list(csv_columns_set - all_valid_columns)

        is_valid = len(missing_required) == 0

        return {
            'valid': is_valid,
            'missing_required': missing_required,
            'extra_columns': extra_columns,
            'message': self._build_validation_message(missing_required, extra_columns)
        }

    def _build_validation_message(self, missing: list, extra: list) -> str:
        """Build a human-readable validation message"""
        messages = []

        if missing:
            messages.append(f"Missing required columns: {', '.join(missing)}")

        if extra:
            messages.append(f"Unknown columns (will be ignored): {', '.join(extra)}")

        if not messages:
            return "CSV structure is valid"

        return "; ".join(messages)

    def parse_csv_file(self, csv_file_path: str, encoding: str = 'utf-8') -> dict:
        """
        Parses a CSV file and returns data ready to create MaterialRecords.

        Args:
            csv_file_path: Path to the CSV file
            encoding: File encoding (default: utf-8)

        Returns:
            dict with:
                - 'success': bool
                - 'data': list of dicts (rows) if successful
                - 'validation': validation result
                - 'error': error message if failed
                - 'rows_parsed': number of rows parsed
        """
        result = {
            'success': False,
            'data': [],
            'validation': None,
            'error': None,
            'rows_parsed': 0
        }

        try:
            # Check if file exists
            if not os.path.exists(csv_file_path):
                result['error'] = f"CSV file not found: {csv_file_path}"
                return result

            # Read and validate CSV
            with open(csv_file_path, 'r', encoding=encoding) as csv_file:
                csv_reader = csv.DictReader(csv_file)

                # Validate columns
                columns = csv_reader.fieldnames
                validation = self.validate_csv_columns(columns)
                result['validation'] = validation

                if not validation['valid']:
                    result['error'] = validation['message']
                    return result

                # Parse rows
                rows_data = []
                for row_num, row in enumerate(csv_reader, start=2):  # start=2 because row 1 is header
                    try:
                        parsed_row = self._parse_csv_row(row, row_num)
                        rows_data.append(parsed_row)
                    except ValueError as e:
                        logger.warning(f"Skipping row {row_num}: {str(e)}")
                        continue

                result['data'] = rows_data
                result['rows_parsed'] = len(rows_data)
                result['success'] = True

        except UnicodeDecodeError:
            result['error'] = f"Encoding error. Try different encoding (current: {encoding})"
        except Exception as e:
            result['error'] = f"Error parsing CSV: {str(e)}"
            logger.error(f"CSV parsing error: {str(e)}", exc_info=True)

        return result

    def _parse_csv_row(self, row: dict, row_num: int) -> dict:
        """
        Parses a single CSV row and converts data types.

        Args:
            row: Dictionary from csv.DictReader
            row_num: Row number for error messages

        Returns:
            dict with parsed and typed data

        Raises:
            ValueError: If required fields are missing or invalid
        """
        from app.modules.dataset.models import DataSource

        # Check required fields
        if not row.get('material_name', '').strip():
            raise ValueError(f"Row {row_num}: material_name is required")
        if not row.get('property_name', '').strip():
            raise ValueError(f"Row {row_num}: property_name is required")
        if not row.get('property_value', '').strip():
            raise ValueError(f"Row {row_num}: property_value is required")

        parsed_data = {
            # Required fields
            'material_name': row['material_name'].strip(),
            'property_name': row['property_name'].strip(),
            'property_value': row['property_value'].strip(),

            # Optional string fields
            'chemical_formula': row.get('chemical_formula', '').strip() or None,
            'structure_type': row.get('structure_type', '').strip() or None,
            'composition_method': row.get('composition_method', '').strip() or None,
            'property_unit': row.get('property_unit', '').strip() or None,
            'description': row.get('description', '').strip() or None,
        }

        # Parse temperature (Integer)
        temp_value = row.get('temperature', '').strip()
        if temp_value:
            try:
                parsed_data['temperature'] = int(temp_value)
            except ValueError:
                logger.warning(f"Row {row_num}: Invalid temperature value '{temp_value}', setting to None")
                parsed_data['temperature'] = None
        else:
            parsed_data['temperature'] = None

        # Parse pressure (Integer)
        pressure_value = row.get('pressure', '').strip()
        if pressure_value:
            try:
                parsed_data['pressure'] = int(pressure_value)
            except ValueError:
                logger.warning(f"Row {row_num}: Invalid pressure value '{pressure_value}', setting to None")
                parsed_data['pressure'] = None
        else:
            parsed_data['pressure'] = None

        # Parse uncertainty (Integer)
        uncertainty_value = row.get('uncertainty', '').strip()
        if uncertainty_value:
            try:
                parsed_data['uncertainty'] = int(uncertainty_value)
            except ValueError:
                logger.warning(f"Row {row_num}: Invalid uncertainty value '{uncertainty_value}', setting to None")
                parsed_data['uncertainty'] = None
        else:
            parsed_data['uncertainty'] = None

        # Parse data_source (Enum)
        data_source_value = row.get('data_source', '').strip().upper()
        if data_source_value:
            try:
                parsed_data['data_source'] = DataSource[data_source_value]
            except KeyError:
                valid_sources = ', '.join([e.name for e in DataSource])
                logger.warning(
                    f"Row {row_num}: Invalid data_source '{data_source_value}'. "
                    f"Valid options: {valid_sources}. Setting to None"
                )
                parsed_data['data_source'] = None
        else:
            parsed_data['data_source'] = None

        return parsed_data

    def create_material_records_from_csv(self, materials_dataset, csv_file_path: str) -> dict:
        """
        Parses CSV file and creates MaterialRecord instances linked to the MaterialsDataset.

        Args:
            materials_dataset: MaterialsDataset instance to link records to
            csv_file_path: Path to the CSV file

        Returns:
            dict with:
                - 'success': bool
                - 'records_created': int
                - 'error': str (if failed)
        """
        from app import db
        from app.modules.dataset.models import MaterialRecord

        # Parse the CSV
        parse_result = self.parse_csv_file(csv_file_path)

        if not parse_result['success']:
            return {
                'success': False,
                'records_created': 0,
                'error': parse_result['error']
            }

        # Create MaterialRecord instances
        records_created = 0
        try:
            for row_data in parse_result['data']:
                material_record = MaterialRecord(
                    materials_dataset_id=materials_dataset.id,
                    **row_data
                )
                db.session.add(material_record)
                records_created += 1

            db.session.commit()

            return {
                'success': True,
                'records_created': records_created,
                'error': None
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating MaterialRecords: {str(e)}", exc_info=True)
            return {
                'success': False,
                'records_created': 0,
                'error': f"Database error: {str(e)}"
            }

    def get_recommendations(self, materials_dataset_id: int, limit: int = 3):
        """
        Gets recommended materials datasets based on tag similarity,
        publication type, and author.

        Args:
            materials_dataset_id: ID of the current materials dataset
            limit: Maximum number of recommendations (default: 3)

        Returns:
            List of MaterialsDataset ordered by relevance
        """
        from app.modules.dataset.models import MaterialsDataset

        try:
            # Get current dataset
            current_dataset = self.materials_dataset_repository.get_by_id(materials_dataset_id)
            if not current_dataset:
                return []

            # Check if it has metadata and tags
            if not current_dataset.ds_meta_data or not current_dataset.ds_meta_data.tags:
                # If no tags, return recent datasets
                return MaterialsDataset.query.filter(
                    MaterialsDataset.id != materials_dataset_id,
                    MaterialsDataset.ds_meta_data_id.isnot(None)
                ).order_by(MaterialsDataset.created_at.desc()).limit(limit).all()

            # Get tags from current dataset
            current_tags = set(tag.strip().lower() for tag in current_dataset.ds_meta_data.tags.split(','))

            # Get all other materials datasets
            all_datasets = MaterialsDataset.query.filter(
                MaterialsDataset.id != materials_dataset_id,
                MaterialsDataset.ds_meta_data_id.isnot(None)
            ).all()

            # Calculate similarity score for each dataset
            recommendations = []
            for dataset in all_datasets:
                score = 0

                # Check valid metadata
                if not dataset.ds_meta_data:
                    continue

                # 1. Tag similarity (weight: 3 points per common tag)
                if dataset.ds_meta_data.tags:
                    dataset_tags = set(tag.strip().lower() for tag in dataset.ds_meta_data.tags.split(','))
                    common_tags = current_tags.intersection(dataset_tags)
                    score += len(common_tags) * 3

                # 2. Same publication type (weight: 2 points)
                if (hasattr(dataset.ds_meta_data, 'publication_type') and
                        hasattr(current_dataset.ds_meta_data, 'publication_type') and
                        dataset.ds_meta_data.publication_type == current_dataset.ds_meta_data.publication_type):
                    score += 2

                # 3. Same author (weight: 1 point)
                if dataset.user_id == current_dataset.user_id:
                    score += 1

                # Only add if has some score
                if score > 0:
                    recommendations.append((dataset, score))

            # Sort by score descending
            recommendations.sort(key=lambda x: x[1], reverse=True)

            # Get top results
            result = [rec[0] for rec in recommendations[:limit]]

            # If not enough recommendations, complete with recent datasets
            if len(result) < limit:
                recent_datasets = MaterialsDataset.query.filter(
                    MaterialsDataset.id != materials_dataset_id,
                    MaterialsDataset.ds_meta_data_id.isnot(None)
                ).order_by(MaterialsDataset.created_at.desc()).limit(limit - len(result)).all()

                # Add only those not already in result
                result_ids = {d.id for d in result}
                for dataset in recent_datasets:
                    if dataset.id not in result_ids:
                        result.append(dataset)
                        if len(result) >= limit:
                            break

            return result[:limit]

        except Exception as e:
            logger.exception(f"Error getting recommendations for materials dataset {materials_dataset_id}: {e}")
            # In case of error, return empty list
            return []

    def get_all_except(self, materials_dataset_id: int):
        """
        Gets all materials datasets except the specified one.

        Args:
            materials_dataset_id: ID of the materials dataset to exclude

        Returns:
            List of MaterialsDataset
        """
        from app.modules.dataset.models import MaterialsDataset

        return MaterialsDataset.query.filter(
            MaterialsDataset.id != materials_dataset_id,
            MaterialsDataset.ds_meta_data_id.isnot(None)
        ).all()

    def filter_by_authors(self, datasets, current_dataset):
        """
        Filters materials datasets that share authors with current dataset.

        Args:
            datasets: List of materials datasets to filter
            current_dataset: Reference materials dataset

        Returns:
            Filtered list of materials datasets
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
        Filters materials datasets that share tags with current dataset.

        Args:
            datasets: List of materials datasets to filter
            current_dataset: Reference materials dataset

        Returns:
            Filtered list of materials datasets
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

    def filter_by_properties(self, datasets, current_dataset):
        """
        Filters materials datasets that measure similar properties.

        Args:
            datasets: List of materials datasets to filter
            current_dataset: Reference materials dataset

        Returns:
            Filtered list of materials datasets
        """
        current_properties = {prop.strip().lower() for prop in current_dataset.get_unique_properties()}

        if not current_properties:
            return []

        return [
            ds for ds in datasets
            if any(prop.strip().lower() in current_properties for prop in ds.get_unique_properties())
        ]
