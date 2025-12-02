import os

from flask import request
from flask_restful import Resource
from werkzeug.utils import secure_filename

from app import db
from app.modules.dataset.models import MaterialsDataset
from app.modules.dataset.repositories import MaterialRecordRepository, MaterialsDatasetRepository
from core.resources.generic_resource import create_resource
from core.serialisers.serializer import Serializer

# Existing serializers for UVL datasets
file_fields = {"file_id": "id", "file_name": "name", "size": "get_formatted_size"}
file_serializer = Serializer(file_fields)

dataset_fields = {
    "dataset_id": "id",
    "created": "created_at",
    "name": "name",
    "doi": "get_uvlhub_doi",
    "files": "files",
}

dataset_serializer = Serializer(dataset_fields, related_serializers={"files": file_serializer})

# UVL removed: DataSetResource = create_resource(DataSet, dataset_serializer)

# MaterialsDataset serializers
material_record_fields = {
    "id": "id",
    "material_name": "material_name",
    "chemical_formula": "chemical_formula",
    "structure_type": "structure_type",
    "composition_method": "composition_method",
    "property_name": "property_name",
    "property_value": "property_value",
    "property_unit": "property_unit",
    "temperature": "temperature",
    "pressure": "pressure",
    "data_source": "data_source",
    "uncertainty": "uncertainty",
    "description": "description",
}

material_record_serializer = Serializer(material_record_fields)

materials_dataset_fields = {
    "id": "id",
    "created_at": "created_at",
    "csv_file_path": "csv_file_path",
    "materials_count": "get_materials_count",
    "unique_materials": "get_unique_materials",
    "unique_properties": "get_unique_properties",
}

materials_dataset_serializer = Serializer(materials_dataset_fields)

MaterialsDatasetResource = create_resource(MaterialsDataset, materials_dataset_serializer)


# Custom endpoint classes for MaterialsDataset operations
class MaterialsDatasetUploadResource(Resource):
    """Endpoint for uploading CSV files to MaterialsDataset"""

    def __init__(self):
        # Importación diferida para evitar ciclos de importación
        from app.modules.dataset.services import MaterialsDatasetService

        self.service = MaterialsDatasetService()
        self.repository = MaterialsDatasetRepository()

    def post(self, id):
        """Upload and parse CSV file for a MaterialsDataset"""
        # Get the MaterialsDataset
        materials_dataset = self.repository.get_by_id(id)
        if not materials_dataset:
            return {"message": "MaterialsDataset not found"}, 404

        # Check if file is in request
        if "file" not in request.files:
            return {"message": "No file part in the request"}, 400

        file = request.files["file"]
        if file.filename == "":
            return {"message": "No file selected"}, 400

        if file and file.filename.endswith(".csv"):
            # Save file temporarily
            filename = secure_filename(file.filename)
            working_dir = os.getenv("WORKING_DIR", "")
            temp_dir = os.path.join(working_dir, "temp")
            os.makedirs(temp_dir, exist_ok=True)

            temp_path = os.path.join(temp_dir, filename)
            file.save(temp_path)

            # Parse CSV and create records
            result = self.service.create_material_records_from_csv(materials_dataset, temp_path)

            # Update csv_file_path if successful
            if result["success"]:
                materials_dataset.csv_file_path = temp_path
                db.session.commit()

            # Clean up temp file if parsing failed
            if not result["success"] and os.path.exists(temp_path):
                os.remove(temp_path)

            if result["success"]:
                return {
                    "message": "CSV uploaded and parsed successfully",
                    "records_created": result["records_created"],
                    "dataset_id": materials_dataset.id,
                }, 200
            else:
                return {"message": "CSV parsing failed", "error": result["error"]}, 400
        else:
            return {"message": "File must be a CSV"}, 400


class MaterialRecordsResource(Resource):
    """Endpoint for getting MaterialRecords of a dataset"""

    def __init__(self):
        self.repository = MaterialRecordRepository()

    def get(self, dataset_id):
        """Get all material records for a dataset with optional pagination"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 100, type=int)

        # Get all records for the dataset
        records = self.repository.get_by_dataset(dataset_id)

        # Manual pagination
        total = len(records)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_records = records[start:end]

        return {
            "records": [record.to_dict() for record in paginated_records],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }, 200


class MaterialRecordsSearchResource(Resource):
    """Endpoint for searching MaterialRecords"""

    def __init__(self):
        self.repository = MaterialRecordRepository()

    def get(self, dataset_id):
        """Search material records by name or formula"""
        search_term = request.args.get("q", "", type=str)

        if not search_term:
            return {"message": "Search query parameter 'q' is required"}, 400

        records = self.repository.search_materials(dataset_id, search_term)

        return {
            "records": [record.to_dict() for record in records],
            "total": len(records),
            "search_term": search_term,
        }, 200


class MaterialsDatasetStatisticsResource(Resource):
    """Endpoint for getting statistics of a MaterialsDataset"""

    def __init__(self):
        self.repository = MaterialsDatasetRepository()

    def get(self, id):
        """Get statistics for a materials dataset"""
        materials_dataset = self.repository.get_by_id(id)
        if not materials_dataset:
            return {"message": "MaterialsDataset not found"}, 404

        return {
            "dataset_id": materials_dataset.id,
            "total_records": materials_dataset.get_materials_count(),
            "unique_materials": materials_dataset.get_unique_materials(),
            "unique_properties": materials_dataset.get_unique_properties(),
            "materials_count": len(materials_dataset.get_unique_materials()),
            "properties_count": len(materials_dataset.get_unique_properties()),
            "csv_file_path": materials_dataset.csv_file_path,
        }, 200


def init_blueprint_api(api_instance):
    """Function to register resources with the provided Flask-RESTful Api instance."""
    # Existing UVL dataset endpoints
    # UVL removed: api_instance.add_resource(DataSetResource, "/api/v1/datasets/", endpoint="datasets")
    # UVL removed: api_instance.add_resource(DataSetResource, "/api/v1/datasets/<int:id>", endpoint="dataset")

    # MaterialsDataset CRUD endpoints
    api_instance.add_resource(MaterialsDatasetResource, "/api/v1/materials-datasets/", endpoint="materials_datasets")
    api_instance.add_resource(
        MaterialsDatasetResource, "/api/v1/materials-datasets/<int:id>", endpoint="materials_dataset"
    )

    # MaterialsDataset custom endpoints
    api_instance.add_resource(
        MaterialsDatasetUploadResource,
        "/api/v1/materials-datasets/<int:id>/upload",
        endpoint="api_materials_dataset_upload",
    )
    api_instance.add_resource(
        MaterialsDatasetStatisticsResource,
        "/api/v1/materials-datasets/<int:id>/statistics",
        endpoint="api_materials_dataset_statistics",
    )

    # MaterialRecord endpoints
    api_instance.add_resource(
        MaterialRecordsResource, "/api/v1/materials-datasets/<int:dataset_id>/records", endpoint="api_material_records"
    )
    api_instance.add_resource(
        MaterialRecordsSearchResource,
        "/api/v1/materials-datasets/<int:dataset_id>/records/search",
        endpoint="api_material_records_search",
    )
