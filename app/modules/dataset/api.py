import os

from flask import request
from flask_restful import Resource
from werkzeug.utils import secure_filename

from app import db
from app.modules.dataset.models import MaterialsDataset
from app.modules.dataset.repositories import MaterialRecordRepository, MaterialsDatasetRepository
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


class MaterialsDatasetResource(Resource):
    """CRUD operations for MaterialsDataset"""

    def __init__(self):
        self.repository = MaterialsDatasetRepository()

    def get(self, id=None):
        """Get MaterialsDataset(s)
        ---
        tags:
          - MaterialsDataset
        summary: Get dataset(s)
        description: Retrieve a single MaterialsDataset by ID or list all datasets
        parameters:
          - name: id
            in: path
            type: integer
            required: false
            description: ID of the MaterialsDataset (omit to list all)
        responses:
          200:
            description: MaterialsDataset or list of datasets
            schema:
              type: object
              properties:
                id:
                  type: integer
                created_at:
                  type: string
                  format: date-time
                csv_file_path:
                  type: string
                materials_count:
                  type: integer
                unique_materials:
                  type: array
                  items:
                    type: string
                unique_properties:
                  type: array
                  items:
                    type: string
          404:
            description: MaterialsDataset not found
        """
        if id:
            dataset = self.repository.get_by_id(id)
            if not dataset:
                return {"message": "MaterialsDataset not found"}, 404
            return materials_dataset_serializer.serialize(dataset), 200
        else:
            datasets = MaterialsDataset.query.all()
            return {"items": [materials_dataset_serializer.serialize(d) for d in datasets]}, 200

    def post(self):
        """Create a new MaterialsDataset
        ---
        tags:
          - MaterialsDataset
        summary: Create dataset
        description: Create a new MaterialsDataset
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                csv_file_path:
                  type: string
                  description: Path to CSV file
                  example: /uploads/materials.csv
        responses:
          201:
            description: MaterialsDataset created successfully
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: MaterialsDataset created successfully
                id:
                  type: integer
                  example: 1
          400:
            description: No input data provided
        """
        data = request.get_json()
        if not data:
            return {"message": "No input data provided"}, 400

        dataset = MaterialsDataset(**data)
        db.session.add(dataset)
        db.session.commit()
        return {"message": "MaterialsDataset created successfully", "id": dataset.id}, 201

    def put(self, id):
        """Update a MaterialsDataset
        ---
        tags:
          - MaterialsDataset
        summary: Update dataset
        description: Update an existing MaterialsDataset
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID of the MaterialsDataset
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                csv_file_path:
                  type: string
                  description: Path to CSV file
        responses:
          200:
            description: MaterialsDataset updated successfully
          404:
            description: MaterialsDataset not found
        """
        dataset = self.repository.get_by_id(id)
        if not dataset:
            return {"message": "MaterialsDataset not found"}, 404

        data = request.get_json()
        for key, value in data.items():
            if hasattr(dataset, key):
                setattr(dataset, key, value)
        db.session.commit()
        return materials_dataset_serializer.serialize(dataset), 200

    def delete(self, id):
        """Delete a MaterialsDataset
        ---
        tags:
          - MaterialsDataset
        summary: Delete dataset
        description: Delete an existing MaterialsDataset
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID of the MaterialsDataset
        responses:
          204:
            description: MaterialsDataset deleted successfully
          404:
            description: MaterialsDataset not found
        """
        dataset = self.repository.get_by_id(id)
        if not dataset:
            return {"message": "MaterialsDataset not found"}, 404

        db.session.delete(dataset)
        db.session.commit()
        return {"message": "MaterialsDataset deleted successfully"}, 204


# Custom endpoint classes for MaterialsDataset operations
class MaterialsDatasetUploadResource(Resource):
    """Endpoint for uploading CSV files to MaterialsDataset"""

    def __init__(self):
        # Importación diferida para evitar ciclos de importación
        from app.modules.dataset.services import MaterialsDatasetService

        self.service = MaterialsDatasetService()
        self.repository = MaterialsDatasetRepository()

    def post(self, id):
        """Upload and parse CSV file for a MaterialsDataset
        ---
        tags:
          - MaterialsDataset
        summary: Upload CSV file with material records
        description: Upload a CSV file containing material property data and create material records
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID of the MaterialsDataset
          - name: file
            in: formData
            type: file
            required: true
            description: CSV file with material records
        consumes:
          - multipart/form-data
        responses:
          200:
            description: CSV uploaded and parsed successfully
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: CSV uploaded and parsed successfully
                records_created:
                  type: integer
                  example: 42
                dataset_id:
                  type: integer
                  example: 1
          400:
            description: Bad request (invalid file or parsing error)
            schema:
              type: object
              properties:
                message:
                  type: string
                error:
                  type: string
          404:
            description: MaterialsDataset not found
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: MaterialsDataset not found
        """
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
        """Get all material records for a dataset with optional pagination
        ---
        tags:
          - MaterialRecords
        summary: List material records
        description: Get all material records for a specific dataset with pagination support
        parameters:
          - name: dataset_id
            in: path
            type: integer
            required: true
            description: ID of the MaterialsDataset
          - name: page
            in: query
            type: integer
            default: 1
            description: Page number
          - name: per_page
            in: query
            type: integer
            default: 100
            description: Number of records per page
        responses:
          200:
            description: List of material records
            schema:
              type: object
              properties:
                records:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      material_name:
                        type: string
                      chemical_formula:
                        type: string
                      property_name:
                        type: string
                      property_value:
                        type: number
                      property_unit:
                        type: string
                      temperature:
                        type: number
                      pressure:
                        type: number
                total:
                  type: integer
                  example: 150
                page:
                  type: integer
                  example: 1
                per_page:
                  type: integer
                  example: 100
                total_pages:
                  type: integer
                  example: 2
        """
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
        """Search material records by name or formula
        ---
        tags:
          - MaterialRecords
        summary: Search material records
        description: Search for material records by material name or chemical formula
        parameters:
          - name: dataset_id
            in: path
            type: integer
            required: true
            description: ID of the MaterialsDataset
          - name: q
            in: query
            type: string
            required: true
            description: Search query (material name or chemical formula)
            example: Silicon
        responses:
          200:
            description: Search results
            schema:
              type: object
              properties:
                records:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      material_name:
                        type: string
                      chemical_formula:
                        type: string
                      property_name:
                        type: string
                      property_value:
                        type: number
                total:
                  type: integer
                  example: 5
                search_term:
                  type: string
                  example: Silicon
          400:
            description: Missing search query parameter
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Search query parameter 'q' is required
        """
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
        """Get statistics for a materials dataset
        ---
        tags:
          - MaterialsDataset
        summary: Get dataset statistics
        description: Retrieve comprehensive statistics about a materials dataset
        parameters:
          - name: id
            in: path
            type: integer
            required: true
            description: ID of the MaterialsDataset
        responses:
          200:
            description: Dataset statistics
            schema:
              type: object
              properties:
                dataset_id:
                  type: integer
                  example: 1
                total_records:
                  type: integer
                  description: Total number of material records
                  example: 150
                unique_materials:
                  type: array
                  items:
                    type: string
                  description: List of unique material names
                  example: ["Silicon", "Graphene", "Diamond"]
                unique_properties:
                  type: array
                  items:
                    type: string
                  description: List of unique property names
                  example: ["density", "melting_point", "thermal_conductivity"]
                materials_count:
                  type: integer
                  description: Count of unique materials
                  example: 3
                properties_count:
                  type: integer
                  description: Count of unique properties
                  example: 3
                csv_file_path:
                  type: string
                  description: Path to the CSV file
                  example: /uploads/materials_dataset_1.csv
          404:
            description: MaterialsDataset not found
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: MaterialsDataset not found
        """
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
