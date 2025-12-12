import csv
import hashlib
import logging
import os
import uuid
from typing import Optional

from flask import request

from app.modules.dataset.models import DSMetaData, DSViewRecord, MaterialsDataset
from app.modules.dataset.repositories import (
    AuthorRepository,
    DOIMappingRepository,
    DSDownloadRecordRepository,
    DSMetaDataRepository,
    DSViewRecordRepository,
)

# UVL removed: from app.modules.featuremodel.repositories
from core.services.BaseService import BaseService

logger = logging.getLogger(__name__)


def calculate_checksum_and_size(file_path):
    file_size = os.path.getsize(file_path)
    with open(file_path, "rb") as file:
        content = file.read()
        hash_md5 = hashlib.md5(content).hexdigest()
        return hash_md5, file_size


# UVL removed: class DataSetService(BaseService):
#     def __init__(self):
#         super().__init__(())
#         self.feature_model_repository = FeatureModelRepository()
#         self.author_repository = AuthorRepository()
#         self.dsmetadata_repository = DSMetaDataRepository()
#         self.fmmetadata_repository = FMMetaDataRepository()
#         self.dsdownloadrecord_repository = DSDownloadRecordRepository()

#         # Importación diferida para evitar ciclos de importación
#         from app.modules.hubfile.repositories import (
#             HubfileDownloadRecordRepository,
#             HubfileRepository,
#             HubfileViewRecordRepository,
#         )

#         self.hubfiledownloadrecord_repository = HubfileDownloadRecordRepository()
#         self.hubfilerepository = HubfileRepository()
#         self.dsviewrecord_repostory = DSViewRecordRepository()
#         self.hubfileviewrecord_repository = HubfileViewRecordRepository()

#     def move_feature_models(self, dataset: MaterialsDataset):
#         current_user = AuthenticationService().get_authenticated_user()
#         source_dir = current_user.temp_folder()

#         working_dir = os.getenv("WORKING_DIR", "")
#         dest_dir = os.path.join(working_dir, "uploads", f"user_{current_user.id}", f"dataset_{dataset.id}")

#         os.makedirs(dest_dir, exist_ok=True)

#         for feature_model in dataset.feature_models:
#             uvl_filename = feature_model.fm_meta_data.uvl_filename
#             shutil.move(os.path.join(source_dir, uvl_filename), dest_dir)

#     def get_synchronized(self, current_user_id: int) -> DataSet:
#         return self.repository.get_synchronized(current_user_id)

#     def get_unsynchronized(self, current_user_id: int) -> DataSet:
#         return self.repository.get_unsynchronized(current_user_id)

#     def get_unsynchronized_dataset(self, current_user_id: int, dataset_id: int) -> DataSet:
#         return self.repository.get_unsynchronized_dataset(current_user_id, dataset_id)

#     def latest_synchronized(self):
#         return self.repository.latest_synchronized()

#     def count_synchronized_datasets(self):
#         return self.repository.count_synchronized_datasets()

#     def count_feature_models(self):
#         return self.feature_model_service.count_feature_models()

#     def count_authors(self) -> int:
#         return self.author_repository.count()

#     def count_dsmetadata(self) -> int:
#         return self.dsmetadata_repository.count()

#     def total_dataset_downloads(self) -> int:
#         return self.dsdownloadrecord_repository.total_dataset_downloads()

#     def total_dataset_views(self) -> int:
#         return self.dsviewrecord_repostory.total_dataset_views()

#     def get_recommendations(self, dataset_id: int, limit: int = 3):
#         """
#         CAMBIO: Obtiene datasets recomendados basados en similitud de tags,
#         tipo de publicación y autor.

#         Args:
#             dataset_id: ID del dataset actual
#             limit: Número máximo de recomendaciones (default: 3)

#         Returns:
#             Lista de DataSet ordenados por relevancia
#         """
#         try:
#             # Obtener el dataset actual
#             current_dataset = self.repository.get_or_404(dataset_id)

#             # Verificar que tenga metadata y tags
#             if not current_dataset.ds_meta_data or not current_dataset.ds_meta_data.tags:
#                 # Si no tiene tags, retornar datasets recientes
#                 return (
#                     DataSet.query.filter(DataSet.id != dataset_id, DataSet.ds_meta_data_id.isnot(None))
#                     .order_by(DataSet.created_at.desc())
#                     .limit(limit)
#                     .all()
#                 )

#             # Obtener tags del dataset actual
#             current_tags = set(tag.strip().lower() for tag in current_dataset.ds_meta_data.tags.split(","))

#             # Obtener todos los demás datasets
#             all_datasets = DataSet.query.filter(DataSet.id != dataset_id, DataSet.ds_meta_data_id.isnot(None)).all()

#             # Calcular puntuación de similitud para cada dataset
#             recommendations = []
#             for dataset in all_datasets:
#                 score = 0

#                 # Verificar que tenga metadata válida
#                 if not dataset.ds_meta_data:
#                     continue

#                 # 1. Similitud de tags (peso: 3 puntos por cada tag común)
#                 if dataset.ds_meta_data.tags:
#                     dataset_tags = set(tag.strip().lower() for tag in dataset.ds_meta_data.tags.split(","))
#                     common_tags = current_tags.intersection(dataset_tags)
#                     score += len(common_tags) * 3

#                 # 2. Mismo tipo de publicación (peso: 2 puntos)
#                 if (
#                     hasattr(dataset.ds_meta_data, "publication_type")
#                     and hasattr(current_dataset.ds_meta_data, "publication_type")
#                     and dataset.ds_meta_data.publication_type == current_dataset.ds_meta_data.publication_type
#                 ):
#                     score += 2

#                 # 3. Mismo autor (peso: 1 punto)
#                 if dataset.user_id == current_dataset.user_id:
#                     score += 1

#                 # Solo añadir si tiene alguna puntuación
#                 if score > 0:
#                     recommendations.append((dataset, score))

#             # Ordenar por puntuación descendente
#             recommendations.sort(key=lambda x: x[1], reverse=True)

#             # Obtener los mejores resultados
#             result = [rec[0] for rec in recommendations[:limit]]

#             # Si no hay suficientes recomendaciones, completar con datasets recientes
#             if len(result) < limit:
#                 recent_datasets = (
#                     DataSet.query.filter(DataSet.id != dataset_id, DataSet.ds_meta_data_id.isnot(None))
#                     .order_by(DataSet.created_at.desc())
#                     .limit(limit - len(result))
#                     .all()
#                 )

#                 # Añadir solo los que no estén ya en result
#                 result_ids = {d.id for d in result}
#                 for dataset in recent_datasets:
#                     if dataset.id not in result_ids:
#                         result.append(dataset)
#                         if len(result) >= limit:
#                             break

#             return result[:limit]

#         except Exception as e:
#             logger.exception(f"Error getting recommendations for dataset {dataset_id}: {e}")
#             # En caso de error, retornar lista vacía
#             return []

#     def get_all_except(self, dataset_id: int):
#         """
#         Obtiene todos los datasets excepto el especificado.

#         Args:
#             dataset_id: ID del dataset a excluir

#         Returns:
#             Lista de DataSet
#         """
#         return DataSet.query.filter(DataSet.id != dataset_id, DataSet.ds_meta_data_id.isnot(None)).all()

#     def filter_by_authors(self, datasets, current_dataset):
#         """
#         Filtra datasets que comparten autores con el dataset actual.

#         Args:
#             datasets: Lista de datasets a filtrar
#             current_dataset: Dataset de referencia

#         Returns:
#             Lista filtrada de datasets
#         """
#         if not current_dataset.ds_meta_data or not current_dataset.ds_meta_data.authors:
#             return []

#         current_authors = {a.name.strip().lower() for a in current_dataset.ds_meta_data.authors}

#         return [
#             ds
#             for ds in datasets
#             if ds.ds_meta_data
#             and ds.ds_meta_data.authors
#             and any(a.name.strip().lower() in current_authors for a in ds.ds_meta_data.authors)
#         ]

#     def filter_by_tags(self, datasets, current_dataset):
#         """
#         Filtra datasets que comparten tags con el dataset actual.

#         Args:
#             datasets: Lista de datasets a filtrar
#             current_dataset: Dataset de referencia

#         Returns:
#             Lista filtrada de datasets
#         """
#         if not current_dataset.ds_meta_data or not current_dataset.ds_meta_data.tags:
#             return []

#         current_tags = {t.strip().lower() for t in current_dataset.ds_meta_data.tags.split(",")}

#         return [
#             ds
#             for ds in datasets
#             if ds.ds_meta_data
#             and ds.ds_meta_data.tags
#             and any(t.strip().lower() in current_tags for t in ds.ds_meta_data.tags.split(","))
#         ]

#     def filter_by_community(self, datasets, current_dataset):
#         """
#         Filtra datasets que pertenecen a la misma comunidad.

#         Args:
#             datasets: Lista de datasets a filtrar
#             current_dataset: Dataset de referencia

#         Returns:
#             Lista filtrada de datasets
#         """
#         if not hasattr(current_dataset, "community_id") or not current_dataset.community_id:
#             return []

#         return [
#             ds for ds in datasets if hasattr(ds, "community_id") and ds.community_id == current_dataset.community_id
#         ]

#     def create_from_form(self, form, current_user) -> DataSet:
#         main_author = {
#             "name": f"{current_user.profile.surname}, {current_user.profile.name}",
#             "affiliation": current_user.profile.affiliation,
#             "orcid": current_user.profile.orcid,
#         }
#         try:
#             logger.info(f"Creating dsmetadata...: {form.get_dsmetadata()}")
#             dsmetadata = self.dsmetadata_repository.create(**form.get_dsmetadata())
#             for author_data in [main_author] + form.get_authors():
#                 author = self.author_repository.create(commit=False, ds_meta_data_id=dsmetadata.id, **author_data)
#                 dsmetadata.authors.append(author)

#             dataset = self.create(commit=False, user_id=current_user.id, ds_meta_data_id=dsmetadata.id)

#             for feature_model in form.feature_models:
#                 uvl_filename = feature_model.uvl_filename.data
#                 fmmetadata = self.fmmetadata_repository.create(commit=False, **feature_model.get_fmmetadata())
#                 for author_data in feature_model.get_authors():
#                     author = self.author_repository.create(commit=False, fm_meta_data_id=fmmetadata.id, **author_data)
#                     fmmetadata.authors.append(author)

#                 fm = self.feature_model_repository.create(
#                     commit=False, data_set_id=dataset.id, fm_meta_data_id=fmmetadata.id
#                 )

#                 # associated files in feature model
#                 file_path = os.path.join(current_user.temp_folder(), uvl_filename)
#                 checksum, size = calculate_checksum_and_size(file_path)

#                 file = self.hubfilerepository.create(
#                     commit=False, name=uvl_filename, checksum=checksum, size=size, feature_model_id=fm.id
#                 )
#                 fm.files.append(file)
#             self.repository.session.commit()
#         except Exception as exc:
#             logger.info(f"Exception creating dataset from form...: {exc}")
#             self.repository.session.rollback()
#             raise exc
#         return dataset

#     def update_dsmetadata(self, id, **kwargs):
#         return self.dsmetadata_repository.update(id, **kwargs)

#     def get_uvlhub_doi(self, dataset: MaterialsDataset) -> str:
#         domain = os.getenv("DOMAIN", "localhost")
#         return f"http://{domain}/doi/{dataset.ds_meta_data.dataset_doi}"

#     def get_top_global(self, metric: str = "downloads", limit: int = 10, days: int = 30):
#         """
#         Devuelve el top global según métrica ('downloads'|'views'), límite y rango de días (7|30).
#         """
#         metric = (metric or "downloads").lower()
#         if metric == "views":
#             return self.repository.get_top_views_global(limit=limit, days=days)
#         return self.repository.get_top_downloads_global(limit=limit, days=days)


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

    def the_record_exists(self, dataset: MaterialsDataset, user_cookie: str):
        return self.repository.the_record_exists(dataset, user_cookie)

    def create_new_record(self, dataset: MaterialsDataset, user_cookie: str) -> DSViewRecord:
        return self.repository.create_new_record(dataset, user_cookie)

    def create_cookie(self, dataset: MaterialsDataset) -> str:

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
    REQUIRED_COLUMNS = ["material_name", "property_name", "property_value"]

    OPTIONAL_COLUMNS = [
        "chemical_formula",
        "structure_type",
        "composition_method",
        "property_unit",
        "temperature",
        "pressure",
        "data_source",
        "uncertainty",
        "description",
    ]

    def __init__(self):
        from app.modules.dataset.repositories import (
            AuthorRepository,
            DSMetaDataRepository,
            MaterialRecordRepository,
            MaterialsDatasetRepository,
        )

        self.materials_dataset_repository = MaterialsDatasetRepository()
        self.material_record_repository = MaterialRecordRepository()
        self.author_repository = AuthorRepository()
        self.dsmetadata_repository = DSMetaDataRepository()

    def create_from_form(self, form, current_user):
        """Create a MaterialsDataset from a form submission"""
        import logging

        logger = logging.getLogger(__name__)

        main_author = {
            "name": f"{current_user.profile.surname}, {current_user.profile.name}",
            "affiliation": current_user.profile.affiliation,
            "orcid": current_user.profile.orcid,
        }

        try:
            logger.info(f"Creating MaterialsDataset metadata...: {form.get_dsmetadata()}")
            dsmetadata = self.dsmetadata_repository.create(**form.get_dsmetadata())

            for author_data in [main_author] + form.get_authors():
                author = self.author_repository.create(commit=False, ds_meta_data_id=dsmetadata.id, **author_data)
                dsmetadata.authors.append(author)

            # Create MaterialsDataset (without CSV initially)
            from app import db

            dataset = self.materials_dataset_repository.create(
                commit=False, user_id=current_user.id, ds_meta_data_id=dsmetadata.id, csv_file_path=None
            )

            db.session.commit()

            logger.info(f"Created MaterialsDataset: {dataset}")
            return dataset

        except Exception as e:
            from app import db

            db.session.rollback()
            logger.exception(f"Error creating MaterialsDataset: {e}")
            raise

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
            "valid": is_valid,
            "missing_required": missing_required,
            "extra_columns": extra_columns,
            "message": self._build_validation_message(missing_required, extra_columns),
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

    def parse_csv_file(self, csv_file_path: str, encoding: str = "utf-8") -> dict:
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
        result = {"success": False, "data": [], "validation": None, "error": None, "rows_parsed": 0}

        try:
            # Check if file exists
            if not os.path.exists(csv_file_path):
                result["error"] = f"CSV file not found: {csv_file_path}"
                return result

            # Read and validate CSV
            with open(csv_file_path, "r", encoding=encoding) as csv_file:
                csv_reader = csv.DictReader(csv_file)

                # Validate columns
                columns = csv_reader.fieldnames
                validation = self.validate_csv_columns(columns)
                result["validation"] = validation

                if not validation["valid"]:
                    result["error"] = validation["message"]
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

                result["data"] = rows_data
                result["rows_parsed"] = len(rows_data)
                result["success"] = True

        except UnicodeDecodeError:
            result["error"] = f"Encoding error. Try different encoding (current: {encoding})"
        except Exception as e:
            result["error"] = f"Error parsing CSV: {str(e)}"
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
        if not row.get("material_name", "").strip():
            raise ValueError(f"Row {row_num}: material_name is required")
        if not row.get("property_name", "").strip():
            raise ValueError(f"Row {row_num}: property_name is required")
        if not row.get("property_value", "").strip():
            raise ValueError(f"Row {row_num}: property_value is required")

        parsed_data = {
            # Required fields
            "material_name": row["material_name"].strip(),
            "property_name": row["property_name"].strip(),
            "property_value": row["property_value"].strip(),
            # Optional string fields
            "chemical_formula": row.get("chemical_formula", "").strip() or None,
            "structure_type": row.get("structure_type", "").strip() or None,
            "composition_method": row.get("composition_method", "").strip() or None,
            "property_unit": row.get("property_unit", "").strip() or None,
            "description": row.get("description", "").strip() or None,
        }

        # Parse temperature (Integer)
        temp_value = row.get("temperature", "").strip()
        if temp_value:
            try:
                parsed_data["temperature"] = int(temp_value)
            except ValueError:
                logger.warning(f"Row {row_num}: Invalid temperature value '{temp_value}', setting to None")
                parsed_data["temperature"] = None
        else:
            parsed_data["temperature"] = None

        # Parse pressure (Integer)
        pressure_value = row.get("pressure", "").strip()
        if pressure_value:
            try:
                parsed_data["pressure"] = int(pressure_value)
            except ValueError:
                logger.warning(f"Row {row_num}: Invalid pressure value '{pressure_value}', setting to None")
                parsed_data["pressure"] = None
        else:
            parsed_data["pressure"] = None

        # Parse uncertainty (Integer)
        uncertainty_value = row.get("uncertainty", "").strip()
        if uncertainty_value:
            try:
                parsed_data["uncertainty"] = int(uncertainty_value)
            except ValueError:
                logger.warning(f"Row {row_num}: Invalid uncertainty value '{uncertainty_value}', setting to None")
                parsed_data["uncertainty"] = None
        else:
            parsed_data["uncertainty"] = None

        # Parse data_source (Enum)
        data_source_value = row.get("data_source", "").strip().upper()
        if data_source_value:
            try:
                parsed_data["data_source"] = DataSource[data_source_value]
            except KeyError:
                valid_sources = ", ".join([e.name for e in DataSource])
                logger.warning(
                    f"Row {row_num}: Invalid data_source '{data_source_value}'. "
                    f"Valid options: {valid_sources}. Setting to None"
                )
                parsed_data["data_source"] = None
        else:
            parsed_data["data_source"] = None

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

        if not parse_result["success"]:
            return {"success": False, "records_created": 0, "error": parse_result["error"]}

        # Create MaterialRecord instances
        records_created = 0
        try:
            for row_data in parse_result["data"]:
                material_record = MaterialRecord(materials_dataset_id=materials_dataset.id, **row_data)
                db.session.add(material_record)
                records_created += 1

            db.session.commit()

            return {"success": True, "records_created": records_created, "error": None}

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating MaterialRecords: {str(e)}", exc_info=True)
            return {"success": False, "records_created": 0, "error": f"Database error: {str(e)}"}

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
                return (
                    MaterialsDataset.query.filter(
                        MaterialsDataset.id != materials_dataset_id, MaterialsDataset.ds_meta_data_id.isnot(None)
                    )
                    .order_by(MaterialsDataset.created_at.desc())
                    .limit(limit)
                    .all()
                )

            # Get tags from current dataset
            current_tags = set(tag.strip().lower() for tag in current_dataset.ds_meta_data.tags.split(","))

            # Get all other materials datasets
            all_datasets = MaterialsDataset.query.filter(
                MaterialsDataset.id != materials_dataset_id, MaterialsDataset.ds_meta_data_id.isnot(None)
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
                    dataset_tags = set(tag.strip().lower() for tag in dataset.ds_meta_data.tags.split(","))
                    common_tags = current_tags.intersection(dataset_tags)
                    score += len(common_tags) * 3

                # 2. Same publication type (weight: 2 points)
                if (
                    hasattr(dataset.ds_meta_data, "publication_type")
                    and hasattr(current_dataset.ds_meta_data, "publication_type")
                    and dataset.ds_meta_data.publication_type == current_dataset.ds_meta_data.publication_type
                ):
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
                recent_datasets = (
                    MaterialsDataset.query.filter(
                        MaterialsDataset.id != materials_dataset_id, MaterialsDataset.ds_meta_data_id.isnot(None)
                    )
                    .order_by(MaterialsDataset.created_at.desc())
                    .limit(limit - len(result))
                    .all()
                )

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
            MaterialsDataset.id != materials_dataset_id, MaterialsDataset.ds_meta_data_id.isnot(None)
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
            ds
            for ds in datasets
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
            ds
            for ds in datasets
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
            ds
            for ds in datasets
            if any(prop.strip().lower() in current_properties for prop in ds.get_unique_properties())
        ]

    def get_top_global(self, metric: str = "downloads", limit: int = 10, days: int = 30):
        """
        Devuelve el top global de MaterialsDataset según métrica ('downloads'|'views'), límite y rango de días (7|30).
        """
        metric = (metric or "downloads").lower()
        if metric == "views":
            return self.materials_dataset_repository.get_top_views_global(limit=limit, days=days)
        return self.materials_dataset_repository.get_top_downloads_global(limit=limit, days=days)


class DatasetVersionService:
    def __init__(self):
        from app.modules.dataset.repositories import DatasetVersionRepository, MaterialRecordRepository

        self.version_repository = DatasetVersionRepository()
        self.record_repository = MaterialRecordRepository()

    def list_versions(self, dataset_id: int):
        """List all versions for a dataset"""
        return self.version_repository.get_by_dataset(dataset_id)

    def get_version(self, version_id: int):
        """Get specific version details"""
        return self.version_repository.get_by_id(version_id)

    def compare_files(self, version_id_1: int, version_id_2: int):
        """
        Compare CSV files between two versions.

        Returns:
            dict with added_records, deleted_records, modified_records, unchanged_records_count
        """
        import csv

        version1 = self.version_repository.get_by_id(version_id_1)
        version2 = self.version_repository.get_by_id(version_id_2)

        if not version1 or not version2:
            return None

        # First, check if both CSVs have record_id column
        def has_record_id_column(csv_path):
            """Check if CSV file has record_id column"""
            if not csv_path or not os.path.exists(csv_path):
                return False

            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                return "record_id" in reader.fieldnames if reader.fieldnames else False

        # Determine comparison strategy
        v1_has_id = has_record_id_column(version1.csv_snapshot_path)
        v2_has_id = has_record_id_column(version2.csv_snapshot_path)

        # ALWAYS use simple comparison - no hybrid mode
        # If both have record_id, use id-based keys
        # If neither has record_id OR only one has it, use line-based keys
        # This ensures keys are compatible for comparison
        use_id_based = v1_has_id and v2_has_id

        logger.info(
            f"Comparing versions {version_id_1} and {version_id_2}: "
            f"v1_has_id={v1_has_id}, v2_has_id={v2_has_id}, use_id_based={use_id_based}"
        )

        # Read both CSV files
        def read_csv_as_dict(csv_path, use_id_keys=True):
            """
            Read CSV and create a dictionary of records.
            If use_id_keys=True and record_id exists, use record_id as key.
            Otherwise, use a simple counter (content matching happens later).
            """
            records = {}
            if not csv_path or not os.path.exists(csv_path):
                return records

            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                counter = 0
                for row in reader:
                    record_id = row.get("record_id", "").strip()

                    if use_id_keys and record_id:
                        # Use record_id as key when both versions have it
                        key = f"id:{record_id}"
                    else:
                        # Use counter as temporary key
                        # The content-based matching will handle proper pairing
                        key = f"row:{counter}"

                    records[key] = row
                    counter += 1
            return records

        records1 = read_csv_as_dict(version1.csv_snapshot_path, use_id_based)
        records2 = read_csv_as_dict(version2.csv_snapshot_path, use_id_based)

        logger.info(f"Read {len(records1)} records from version {version_id_1}")
        logger.info(f"Read {len(records2)} records from version {version_id_2}")

        # Helper function to normalize values for comparison
        def normalize_value(val):
            """
            Normalize values for comparison:
            - Treat None, '', 'None' as equivalent empty values
            - Treat numeric values equivalently (e.g., '300' == '300.0')
            """
            if val is None or val == "" or val == "None":
                return ""

            val_str = str(val).strip()

            # Try to normalize numeric values (e.g., '300' and '300.0' should be equal)
            try:
                # Convert to float to handle both integers and decimals
                num_val = float(val_str)
                # Check if it's actually an integer value (no decimal part)
                if num_val == int(num_val):
                    # Return as integer string to match both '300' and '300.0'
                    return str(int(num_val))
                else:
                    # Return as float string, but normalize the representation
                    # This handles cases like '0.5' vs '0.50'
                    return str(num_val)
            except (ValueError, TypeError):
                # Not a number, return as-is
                return val_str

        def records_are_equal(rec1, rec2):
            """Compare two records with normalization, excluding record_id"""
            rec1_normalized = {k: normalize_value(v) for k, v in rec1.items() if k != "record_id"}
            rec2_normalized = {k: normalize_value(v) for k, v in rec2.items() if k != "record_id"}

            # Debug logging for numeric comparison issues
            if rec1_normalized != rec2_normalized:
                for key in set(rec1_normalized.keys()) | set(rec2_normalized.keys()):
                    val1 = rec1_normalized.get(key)
                    val2 = rec2_normalized.get(key)
                    if val1 != val2:
                        orig1 = rec1.get(key)
                        orig2 = rec2.get(key)
                        logger.debug(
                            f"Difference in '{key}': '{val1}' vs '{val2}' " f"(original: '{orig1}' vs '{orig2}')"
                        )

            return rec1_normalized == rec2_normalized

        # Comparison logic
        if use_id_based:
            # Simple ID-based comparison: records are matched by record_id
            keys1 = set(records1.keys())
            keys2 = set(records2.keys())

            added_keys = keys2 - keys1
            deleted_keys = keys1 - keys2
            common_keys = keys1 & keys2

            added_records = [records2[k] for k in added_keys]
            deleted_records = [records1[k] for k in deleted_keys]

            modified_records = []
            unchanged_count = 0

            for key in common_keys:
                if not records_are_equal(records1[key], records2[key]):
                    modified_records.append({"old": records1[key], "new": records2[key]})
                else:
                    unchanged_count += 1

        else:
            # Content-based comparison: match records by identifying fields
            # When record_id is not available in both versions, use content matching
            # Build maps by record_id (when available) and by content key
            id_map1 = {}  # record_id -> (key, record)
            id_map2 = {}
            content_map1 = {}  # content_key -> [(key, record)]
            content_map2 = {}

            def get_content_key(record):
                """
                Generate content-based key using ALL identifying fields.
                Excludes only the editable measurement values (property_value, uncertainty, description).
                This ensures unique matching even when temp/pressure are empty.
                """

                def norm(val):
                    if val is None or val == "" or val == "None":
                        return ""
                    val_str = str(val).strip()
                    # Normalize numeric values
                    try:
                        num = float(val_str)
                        return str(int(num)) if num == int(num) else str(num)
                    except (ValueError, TypeError):
                        return val_str

                # Include ALL identifying fields for uniqueness
                # Exclude ONLY: property_value (measured value), uncertainty, description
                return "{}||{}||{}||{}||{}||{}||{}||{}".format(
                    norm(record.get("material_name", "")),
                    norm(record.get("chemical_formula", "")),
                    norm(record.get("structure_type", "")),
                    norm(record.get("composition_method", "")),
                    norm(record.get("property_name", "")),
                    norm(record.get("property_unit", "")),
                    norm(record.get("temperature", "")),
                    norm(record.get("pressure", "")),
                )

            # Build indices
            for key, record in records1.items():
                record_id = record.get("record_id", "").strip()
                if record_id:
                    id_map1[record_id] = (key, record)

                content_key = get_content_key(record)
                if content_key:
                    if content_key not in content_map1:
                        content_map1[content_key] = []
                    content_map1[content_key].append((key, record))

            for key, record in records2.items():
                record_id = record.get("record_id", "").strip()
                if record_id:
                    id_map2[record_id] = (key, record)

                content_key = get_content_key(record)
                if content_key:
                    if content_key not in content_map2:
                        content_map2[content_key] = []
                    content_map2[content_key].append((key, record))

            # Log map sizes for debugging
            logger.info(
                f"Built maps: id_map1={len(id_map1)}, id_map2={len(id_map2)}, "
                f"content_map1={len(content_map1)}, content_map2={len(content_map2)}"
            )

            # Match records: prefer ID matching, fall back to content matching
            matched_pairs = []
            unmatched_keys1 = set(records1.keys())
            unmatched_keys2 = set(records2.keys())

            # First pass: match by record_id when both have it
            id_matched_count = 0
            for record_id, (key1, rec1) in id_map1.items():
                if record_id in id_map2:
                    key2, rec2 = id_map2[record_id]
                    matched_pairs.append((key1, key2))
                    unmatched_keys1.discard(key1)
                    unmatched_keys2.discard(key2)
                    id_matched_count += 1

            logger.info(f"ID-based matching: {id_matched_count} records matched by record_id")

            # Second pass: match remaining by content key
            content_matched_count = 0
            for content_key, pairs1 in content_map1.items():
                if content_key in content_map2:
                    pairs2 = content_map2[content_key]

                    # Match unmatched records in order
                    unmatched_pairs1 = [(k, r) for k, r in pairs1 if k in unmatched_keys1]
                    unmatched_pairs2 = [(k, r) for k, r in pairs2 if k in unmatched_keys2]

                    for i in range(min(len(unmatched_pairs1), len(unmatched_pairs2))):
                        key1, _ = unmatched_pairs1[i]
                        key2, _ = unmatched_pairs2[i]
                        matched_pairs.append((key1, key2))
                        unmatched_keys1.discard(key1)
                        unmatched_keys2.discard(key2)
                        content_matched_count += 1

            logger.info(f"Content-based matching: {content_matched_count} additional records matched")

            # Process results
            added_records = [records2[k] for k in unmatched_keys2]
            deleted_records = [records1[k] for k in unmatched_keys1]

            modified_records = []
            unchanged_count = 0

            for key1, key2 in matched_pairs:
                # Compare records using normalized comparison (treats None, '', 'None' as equivalent)
                if not records_are_equal(records1[key1], records2[key2]):
                    modified_records.append({"old": records1[key1], "new": records2[key2]})
                else:
                    unchanged_count += 1

        result = {
            "added_records": added_records,
            "deleted_records": deleted_records,
            "modified_records": modified_records,
            "unchanged_records_count": unchanged_count,
            "total_v1": len(records1),
            "total_v2": len(records2),
        }

        logger.info(
            f"Comparison results: {len(added_records)} added, {len(deleted_records)} deleted, "
            f"{len(modified_records)} modified, {unchanged_count} unchanged"
        )

        return result

    def compare_metadata(self, version_id_1: int, version_id_2: int):
        """
        Compare metadata between two versions.

        Returns:
            dict with field-by-field comparison
        """
        version1 = self.version_repository.get_by_id(version_id_1)
        version2 = self.version_repository.get_by_id(version_id_2)

        if not version1 or not version2:
            return None

        meta1 = version1.metadata_snapshot
        meta2 = version2.metadata_snapshot

        comparison = {}

        # Compare each metadata field
        all_keys = set(meta1.keys()) | set(meta2.keys())

        for key in all_keys:
            val1 = meta1.get(key)
            val2 = meta2.get(key)

            if key == "authors":
                # Special handling for authors list
                changed = val1 != val2
                comparison[key] = {"old": val1, "new": val2, "changed": changed}
            else:
                comparison[key] = {"old": val1, "new": val2, "changed": val1 != val2}

        return comparison

    def get_csv_diff(self, version_id_1: int, version_id_2: int):
        """
        Generate unified diff for CSV content using difflib.

        Returns:
            str: unified diff output
        """
        import difflib

        version1 = self.version_repository.get_by_id(version_id_1)
        version2 = self.version_repository.get_by_id(version_id_2)

        if not version1 or not version2:
            return None

        # Read file contents
        def read_file_lines(path):
            if not path or not os.path.exists(path):
                return []
            with open(path, "r", encoding="utf-8") as f:
                return f.readlines()

        lines1 = read_file_lines(version1.csv_snapshot_path)
        lines2 = read_file_lines(version2.csv_snapshot_path)

        # Generate unified diff
        diff = difflib.unified_diff(
            lines1,
            lines2,
            fromfile=f"Version {version1.version_number}",
            tofile=f"Version {version2.version_number}",
            lineterm="",
        )

        return "\n".join(diff)
