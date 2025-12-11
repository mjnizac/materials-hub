import csv
import json
import logging
import os
import shutil
import time
import uuid
from datetime import datetime, timezone

from flask import (
    abort,
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from app.modules.dataset import dataset_bp
from app.modules.dataset.forms import DataSetForm, MaterialRecordForm
from app.modules.dataset.models import DSDownloadRecord, DSViewRecord, PublicationType
from app.modules.dataset.repositories import (
    DatasetVersionRepository,
    MaterialRecordRepository,
    MaterialsDatasetRepository,
)
from app.modules.dataset.services import (
    AuthorService,
    DatasetVersionService,
    DOIMappingService,
    DSMetaDataService,
    DSViewRecordService,
    MaterialsDatasetService,
)
from app.modules.fakenodo.services import FakenodoService
from app.modules.zenodo.services import ZenodoService
from core.configuration.configuration import USE_FAKENODO

logger = logging.getLogger(__name__)
author_service = AuthorService()
dsmetadata_service = DSMetaDataService()
fakenodo_service = FakenodoService()
zenodo_service = ZenodoService()
doi_mapping_service = DOIMappingService()
ds_view_record_service = DSViewRecordService()

# MaterialsDataset services
materials_dataset_service = MaterialsDatasetService()
materials_dataset_repository = MaterialsDatasetRepository()
material_record_repository = MaterialRecordRepository()
dataset_version_repository = DatasetVersionRepository()
dataset_version_service = DatasetVersionService()


# ==============================
# HELPER FUNCTIONS
# ==============================
def regenerate_csv_for_dataset(dataset_id):
    """Regenerate CSV file for a MaterialsDataset with current records"""
    from app import db

    # Expire all cached objects to ensure we read fresh data from database
    db.session.expire_all()

    dataset = materials_dataset_repository.get_by_id(dataset_id)
    if not dataset:
        return False

    # Get all records for this dataset, ordered by ID for consistency
    records = material_record_repository.get_by_dataset(dataset_id)
    # Sort by ID to ensure consistent order across regenerations
    records = sorted(records, key=lambda r: r.id)

    if not dataset.csv_file_path:
        # Create new CSV file path if doesn't exist
        csv_dir = "uploads/materials_csv"
        os.makedirs(csv_dir, exist_ok=True)
        csv_filename = f"materials_dataset_{dataset_id}.csv"
        csv_path = os.path.join(csv_dir, csv_filename)
        dataset.csv_file_path = csv_path
        db.session.commit()
    else:
        csv_path = dataset.csv_file_path
        # Ensure absolute path
        if not os.path.isabs(csv_path):
            csv_path = os.path.abspath(csv_path)

    # Write CSV file
    try:
        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "record_id",  # Add ID as first column for tracking
                "material_name",
                "chemical_formula",
                "structure_type",
                "composition_method",
                "property_name",
                "property_value",
                "property_unit",
                "temperature",
                "pressure",
                "data_source",
                "uncertainty",
                "description",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for record in records:
                writer.writerow(
                    {
                        "record_id": record.id,  # Include record ID
                        "material_name": record.material_name,
                        "chemical_formula": record.chemical_formula or "",
                        "structure_type": record.structure_type or "",
                        "composition_method": record.composition_method or "",
                        "property_name": record.property_name,
                        "property_value": record.property_value,
                        "property_unit": record.property_unit or "",
                        "temperature": record.temperature if record.temperature is not None else "",
                        "pressure": record.pressure if record.pressure is not None else "",
                        "data_source": record.data_source.value if record.data_source else "",
                        "uncertainty": record.uncertainty if record.uncertainty is not None else "",
                        "description": record.description or "",
                    }
                )
        return True
    except Exception as e:
        logger.exception(f"Error regenerating CSV file: {e}")
        return False


def create_version_snapshot(dataset_id, user_id=None, change_description="Dataset modified"):
    """
    Create a version snapshot before making changes to dataset.

    Args:
        dataset_id: ID of the MaterialsDataset
        user_id: ID of user making the change (optional)
        change_description: Description of what changed

    Returns:
        DatasetVersion object or None if error
    """
    from app import db

    try:
        # Get fresh dataset from database
        dataset = materials_dataset_repository.get_by_id(dataset_id)
        if not dataset:
            logger.error(f"Dataset {dataset_id} not found for versioning")
            return None

        # Refresh to ensure we have the latest data from database
        db.session.refresh(dataset)
        db.session.refresh(dataset.ds_meta_data)

        # Get next version number
        next_version = dataset_version_repository.get_next_version_number(dataset_id)

        # Create versions directory if it doesn't exist
        versions_dir = "uploads/materials_csv/versions"
        os.makedirs(versions_dir, exist_ok=True)

        # Copy current CSV to versioned path
        if not dataset.csv_file_path:
            raise Exception(f"Dataset {dataset_id} has no CSV file path")

        if not os.path.exists(dataset.csv_file_path):
            raise Exception(f"CSV file not found at path: {dataset.csv_file_path}")

        csv_filename = f"materials_dataset_{dataset_id}_v{next_version}.csv"
        csv_snapshot_path = os.path.join(versions_dir, csv_filename)

        # Make path absolute if it's relative
        if not os.path.isabs(csv_snapshot_path):
            csv_snapshot_path = os.path.abspath(csv_snapshot_path)

        shutil.copy2(dataset.csv_file_path, csv_snapshot_path)
        logger.info(f"Copied CSV to snapshot: {csv_snapshot_path}")

        # Create metadata snapshot
        metadata_snapshot = {
            "title": dataset.ds_meta_data.title,
            "description": dataset.ds_meta_data.description,
            "publication_type": dataset.ds_meta_data.publication_type.value,
            "publication_doi": dataset.ds_meta_data.publication_doi,
            "dataset_doi": dataset.ds_meta_data.dataset_doi,
            "tags": dataset.ds_meta_data.tags,
            "authors": [
                {"name": author.name, "affiliation": author.affiliation, "orcid": author.orcid}
                for author in dataset.ds_meta_data.authors
            ],
        }

        desc_preview = metadata_snapshot["description"][:50] if metadata_snapshot.get("description") else ""
        logger.info(
            f"Creating version {next_version} snapshot with metadata: "
            f"title='{metadata_snapshot['title']}', description='{desc_preview}...'"
        )

        # Get current records count
        records_count = material_record_repository.count_by_dataset(dataset_id)

        # Create changelog
        changelog = {
            "action": change_description,
            "timestamp": datetime.utcnow().isoformat(),
            "records_count": records_count,
        }

        # Create version record
        version = dataset_version_repository.create(
            materials_dataset_id=dataset_id,
            version_number=next_version,
            created_by_user_id=user_id,
            csv_snapshot_path=csv_snapshot_path,
            metadata_snapshot=metadata_snapshot,
            changelog=changelog,
            records_count=records_count,
        )

        logger.info(f"Created version {next_version} for dataset {dataset_id}")
        return version

    except Exception as e:
        logger.exception(f"Error creating version snapshot for dataset {dataset_id}: {e}")
        db.session.rollback()
        # Re-raise the exception so caller can handle it
        raise Exception(f"Failed to create version snapshot: {str(e)}")


# ==============================
# CREACIÓN Y GESTIÓN DE DATASETS
# ==============================
@dataset_bp.route("/dataset/upload", methods=["GET", "POST"])
@login_required
def create_dataset():
    form = DataSetForm()
    if request.method == "POST":

        if not form.validate_on_submit():
            return jsonify({"message": form.errors}), 400

        try:
            logger.info("Creating MaterialsDataset...")

            # Always create MaterialsDataset
            dataset = materials_dataset_service.create_from_form(form=form, current_user=current_user)

            logger.info(f"Created dataset: {dataset}")
        except Exception as exc:
            logger.exception(f"Exception while create dataset data in local {exc}")
            return jsonify({"Exception while create dataset data in local: ": str(exc)}), 400

        if USE_FAKENODO:
            data = {}
            try:
                fakenodo_response_json = fakenodo_service.create_new_deposition(dataset)
                response_data = json.dumps(fakenodo_response_json)
                data = json.loads(response_data)
            except Exception as exc:
                data = {}
                fakenodo_response_json = {}
                logger.exception(f"Exception while create dataset data in Fakenodo {exc}")

            if data.get("conceptrecid"):
                deposition_id = data.get("id")

                # update dataset with deposition id in Fakenodo
                from app.modules.dataset.services import DSMetaDataService

                dsmetadata_service = DSMetaDataService()
                dsmetadata_service.update(dataset.ds_meta_data_id, deposition_id=deposition_id)

                try:
                    # For MaterialsDataset, just publish without uploading files yet
                    # Files (CSV) will be uploaded later via the upload_materials_csv route
                    fakenodo_service.publish_deposition(deposition_id)

                    # update DOI
                    deposition_doi = fakenodo_service.get_doi(deposition_id)
                    dsmetadata_service.update(dataset.ds_meta_data_id, dataset_doi=deposition_doi)
                except Exception as e:
                    msg = f"it has not been possible to publish in Fakenodo and update the DOI: {e}"
                    return jsonify({"message": msg}), 200
        else:
            # send dataset as deposition to Zenodo
            data = {}
            try:
                zenodo_response_json = zenodo_service.create_new_deposition(dataset)
                response_data = json.dumps(zenodo_response_json)
                data = json.loads(response_data)
            except Exception as exc:
                data = {}
                zenodo_response_json = {}
                logger.exception(f"Exception while create dataset data in Zenodo {exc}")

            if data.get("conceptrecid"):
                deposition_id = data.get("id")

                # update dataset with deposition id in Zenodo
                from app.modules.dataset.services import DSMetaDataService

                dsmetadata_service = DSMetaDataService()
                dsmetadata_service.update(dataset.ds_meta_data_id, deposition_id=deposition_id)

                try:
                    # For MaterialsDataset, just publish without uploading files yet
                    zenodo_service.publish_deposition(deposition_id)

                    # update DOI
                    deposition_doi = zenodo_service.get_doi(deposition_id)
                    dsmetadata_service.update(dataset.ds_meta_data_id, dataset_doi=deposition_doi)
                except Exception as e:
                    msg = f"it has not been possible to publish in Zenodo and update the DOI: {e}"
                    return jsonify({"message": msg}), 200

        file_path = current_user.temp_folder()
        if os.path.exists(file_path) and os.path.isdir(file_path):
            shutil.rmtree(file_path)

        # Always redirect to CSV upload for MaterialsDataset
        return (
            jsonify(
                {
                    "message": "Materials dataset created successfully!",
                    "redirect_url": url_for("dataset.upload_materials_csv", dataset_id=dataset.id),
                }
            ),
            200,
        )

    return render_template("dataset/upload_dataset.html", form=form, use_fakenodo=USE_FAKENODO)


@dataset_bp.route("/dataset/list", methods=["GET", "POST"])
@login_required
def list_dataset():
    """List all MaterialsDatasets for the current user"""
    # Only show datasets that have CSV files uploaded (complete datasets)
    all_datasets = materials_dataset_repository.get_by_user(current_user.id)
    datasets = [d for d in all_datasets if d.csv_file_path]
    return render_template("dataset/list_materials_datasets.html", datasets=datasets)


@dataset_bp.route("/dataset/file/upload", methods=["POST"])
@login_required
def upload():
    file = request.files["file"]
    temp_folder = current_user.temp_folder()

    if not file or not file.filename.endswith(".csv"):
        return jsonify({"message": "No valid file"}), 400

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    file_path = os.path.join(temp_folder, file.filename)

    if os.path.exists(file_path):
        base_name, extension = os.path.splitext(file.filename)
        i = 1
        while os.path.exists(os.path.join(temp_folder, f"{base_name} ({i}){extension}")):
            i += 1
        new_filename = f"{base_name} ({i}){extension}"
        file_path = os.path.join(temp_folder, new_filename)
    else:
        new_filename = file.filename

    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({"message": str(e)}), 500

    return (
        jsonify(
            {
                "message": "UVL uploaded and validated successfully",
                "filename": new_filename,
            }
        ),
        200,
    )


@dataset_bp.route("/dataset/file/delete", methods=["POST"])
def delete():
    data = request.get_json()
    filename = data.get("file")
    temp_folder = current_user.temp_folder()
    filepath = os.path.join(temp_folder, filename)

    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({"message": "File deleted successfully"})

    return jsonify({"error": "File not found"})


@dataset_bp.route("/dataset/download/<int:dataset_id>", methods=["GET"])
def download_dataset(dataset_id):
    """Download CSV file for MaterialsDataset"""
    logger.info(f"Attempting to download dataset {dataset_id}")
    dataset = materials_dataset_repository.get_by_id(dataset_id)

    if not dataset:
        logger.error(f"MaterialsDataset {dataset_id} not found")
        abort(404, description="MaterialsDataset not found")

    logger.info(f"Dataset found. CSV path: {dataset.csv_file_path}")

    if not dataset.csv_file_path:
        logger.error(f"Dataset {dataset_id} has no CSV file path")
        abort(404, description="No CSV file associated with this dataset")

    # Convert to absolute path if relative
    csv_path = dataset.csv_file_path
    if not os.path.isabs(csv_path):
        csv_path = os.path.abspath(csv_path)
        logger.info(f"Converted to absolute path: {csv_path}")

    if not os.path.exists(csv_path):
        logger.error(f"CSV file not found at path: {csv_path}")
        abort(404, description="CSV file not found at expected location")

    csv_dir = os.path.dirname(csv_path)
    csv_filename = os.path.basename(csv_path)
    logger.info(f"Sending file: {csv_filename} from directory: {csv_dir}")

    # Record download
    cookie = request.cookies.get("download_cookie")
    if not cookie:
        cookie = str(uuid.uuid4())

    user_id = current_user.id if current_user.is_authenticated else None

    download_record = DSDownloadRecord(
        user_id=user_id,
        dataset_id=dataset_id,
        download_date=datetime.now(timezone.utc),
        download_cookie=cookie,
    )

    from app import db

    db.session.add(download_record)
    db.session.commit()

    response = make_response(send_from_directory(csv_dir, csv_filename, as_attachment=True))
    response.set_cookie("download_cookie", cookie, max_age=60 * 60 * 24 * 365 * 2)  # 2 years

    return response


# ==============================
# VISUALIZACIÓN DE DATASETS Y RECOMENDACIONES
# ==============================
@dataset_bp.route("/doi/<path:doi>/", methods=["GET"])
def subdomain_index(doi):
    new_doi = doi_mapping_service.get_new_doi(doi)
    if new_doi:
        return redirect(url_for("dataset.subdomain_index", doi=new_doi), code=302)

    ds_meta_data = dsmetadata_service.filter_by_doi(doi)
    if not ds_meta_data:
        abort(404)

    # Get MaterialsDataset
    dataset = ds_meta_data.materials_dataset
    if not dataset:
        abort(404)

    return redirect(url_for("dataset.view_materials_dataset", dataset_id=dataset.id))


@dataset_bp.route("/datasets/top", methods=["GET"])
@login_required
def view_top_global():
    metric = request.args.get("metric", "downloads").lower()
    days = request.args.get("days", 30, type=int)
    limit = request.args.get("limit", 10, type=int)

    if metric not in {"downloads", "views"}:
        metric = "downloads"
    if days not in {7, 30}:
        days = 30
    if not limit or limit < 1:
        limit = 10

    datasets = materials_dataset_service.get_top_global(metric=metric, limit=limit, days=days)

    return render_template(
        "dataset/top_global.html",
        datasets=datasets,
        metric=metric,
        days=days,
        limit=limit,
    )


# ==================== MaterialsDataset Routes ====================


@dataset_bp.route("/materials/<int:dataset_id>", methods=["GET"])
def view_materials_dataset(dataset_id):
    """View details of a MaterialsDataset (public view)"""
    from app import db

    # Expire all cached objects to ensure fresh data from database
    db.session.expire_all()

    dataset = materials_dataset_repository.get_by_id(dataset_id)

    if not dataset:
        abort(404)

    # If dataset has no CSV and user is the owner, redirect to upload page
    if not dataset.csv_file_path:
        if current_user.is_authenticated and current_user.id == dataset.user_id:
            flash("Please upload a CSV file to complete your dataset.", "warning")
            return redirect(url_for("dataset.upload_materials_csv", dataset_id=dataset.id))
        else:
            # Non-owners cannot view incomplete datasets
            abort(404, description="This dataset is incomplete and cannot be viewed")

    # Record view
    view_cookie = request.cookies.get("view_cookie")
    if not view_cookie:
        view_cookie = str(uuid.uuid4())

    user_id = current_user.id if current_user.is_authenticated else None

    # Check if this view already exists to avoid duplicates
    from app import db

    existing_view = db.session.query(DSViewRecord).filter_by(dataset_id=dataset_id, view_cookie=view_cookie).first()

    if not existing_view:
        view_record = DSViewRecord(
            user_id=user_id,
            dataset_id=dataset_id,
            view_date=datetime.now(timezone.utc),
            view_cookie=view_cookie,
        )
        db.session.add(view_record)
        try:
            db.session.commit()
        except IntegrityError as e:
            # IMPORTANTE: no romper la vista, solo avisar y hacer rollback
            db.session.rollback()
            logger.warning(
                "No se pudo guardar DSViewRecord (FK contra data_set). "
                "Probablemente es un MaterialsDataset sin entrada en data_set. "
                f"dataset_id={dataset_id}, error={e}"
            )

    # Get pagination parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    # Get records for this dataset
    all_records = material_record_repository.get_by_dataset(dataset_id)

    # Manual pagination
    total = len(all_records)
    start = (page - 1) * per_page
    end = start + per_page
    records = all_records[start:end]
    total_pages = (total + per_page - 1) // per_page

    # Get recommended datasets
    recommended_datasets = materials_dataset_service.get_recommendations(dataset_id, limit=5)

    response = make_response(
        render_template(
            "dataset/view_materials_dataset.html",
            dataset=dataset,
            records=records,
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            recommended_datasets=recommended_datasets,
        )
    )
    response.set_cookie("view_cookie", view_cookie, max_age=60 * 60 * 24 * 365 * 2)  # 2 years

    return response


@dataset_bp.route("/materials/<int:dataset_id>/upload", methods=["GET", "POST"])
@login_required
def upload_materials_csv(dataset_id):
    """Upload CSV file to a MaterialsDataset"""
    dataset = materials_dataset_repository.get_by_id(dataset_id)

    if not dataset:
        abort(404)

    # Check if user owns this dataset
    if dataset.user_id != current_user.id:
        abort(403)

    if request.method == "POST":
        # Check if file is in request
        if "file" not in request.files:
            return jsonify({"message": "No file part in the request"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"message": "No file selected"}), 400

        if file and file.filename.endswith(".csv"):
            # Save file temporarily
            from werkzeug.utils import secure_filename

            filename = secure_filename(file.filename)
            working_dir = os.getenv("WORKING_DIR", "")
            temp_dir = os.path.join(working_dir, "temp")
            os.makedirs(temp_dir, exist_ok=True)

            temp_path = os.path.join(temp_dir, filename)
            file.save(temp_path)

            # Parse CSV and create records
            result = materials_dataset_service.create_material_records_from_csv(dataset, temp_path)

            # Update csv_file_path if successful
            if result["success"]:
                from app import db

                dataset.csv_file_path = temp_path
                db.session.commit()

                # Create initial version snapshot
                create_version_snapshot(dataset_id, current_user.id, "Initial version - CSV uploaded")

            # Clean up temp file if parsing failed
            if not result["success"] and os.path.exists(temp_path):
                os.remove(temp_path)

            if result["success"]:
                return (
                    jsonify(
                        {
                            "message": "CSV uploaded and parsed successfully",
                            "records_created": result["records_created"],
                            "dataset_id": dataset.id,
                        }
                    ),
                    200,
                )
            else:
                return jsonify({"message": "CSV parsing failed", "error": result["error"]}), 400
        else:
            return jsonify({"message": "File must be a CSV"}), 400

    return render_template("dataset/upload_materials_csv.html", dataset=dataset)


@dataset_bp.route("/materials/<int:dataset_id>/statistics", methods=["GET"])
def materials_dataset_statistics(dataset_id):
    """View statistics for a MaterialsDataset (public view)"""
    dataset = materials_dataset_repository.get_by_id(dataset_id)

    if not dataset:
        abort(404)

    # If dataset has no CSV, redirect to upload page or show error
    if not dataset.csv_file_path:
        if current_user.is_authenticated and current_user.id == dataset.user_id:
            flash("Please upload a CSV file to complete your dataset before viewing statistics.", "warning")
            return redirect(url_for("dataset.upload_materials_csv", dataset_id=dataset.id))
        else:
            abort(404, description="This dataset is incomplete and has no statistics available")

    return render_template("dataset/materials_statistics.html", dataset=dataset)


@dataset_bp.route("/materials/<int:dataset_id>/search", methods=["GET"])
def search_materials(dataset_id):
    """Search materials in a dataset (public view)"""
    dataset = materials_dataset_repository.get_by_id(dataset_id)

    if not dataset:
        abort(404)

    search_term = request.args.get("q", "", type=str)

    if search_term:
        records = material_record_repository.search_materials(dataset_id, search_term)
    else:
        records = []

    return render_template("dataset/search_materials.html", dataset=dataset, records=records, search_term=search_term)


@dataset_bp.route("/materials/<int:dataset_id>/recommendations")
def materials_dataset_recommendations(dataset_id):
    """API to return filtered and paginated recommended materials datasets (AJAX)."""
    page = request.args.get("page", 1, type=int)
    filter_type = request.args.get("filter_type", None, type=str)

    current_dataset = materials_dataset_repository.get_by_id(dataset_id)
    if not current_dataset:
        abort(404)

    query = materials_dataset_service.get_all_except(dataset_id)

    # Apply filters using service methods
    if filter_type == "authors":
        query = materials_dataset_service.filter_by_authors(query, current_dataset)
    elif filter_type == "tags":
        query = materials_dataset_service.filter_by_tags(query, current_dataset)
    elif filter_type == "properties":
        query = materials_dataset_service.filter_by_properties(query, current_dataset)

    # Pagination
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page
    paginated = query[start:end]
    total_pages = (len(query) + per_page - 1) // per_page

    html = render_template("dataset/materials_recommendations_table.html", recommended_datasets=paginated)

    return jsonify({"html": html, "page": page, "total_pages": total_pages})


@dataset_bp.route("/materials/<int:dataset_id>/view_csv", methods=["GET"])
def view_materials_csv(dataset_id):
    """View CSV file content for a MaterialsDataset as structured data"""
    dataset = materials_dataset_repository.get_by_id(dataset_id)

    if not dataset:
        abort(404)

    if not dataset.csv_file_path or not os.path.exists(dataset.csv_file_path):
        return jsonify({"error": "CSV file not found"}), 404

    try:
        with open(dataset.csv_file_path, "r", encoding="utf-8") as f:
            csv_reader = csv.DictReader(f)
            headers = csv_reader.fieldnames
            rows = [row for row in csv_reader]

        return jsonify({"headers": headers, "rows": rows, "total": len(rows)})
    except Exception as e:
        logger.exception(f"Error reading CSV file: {e}")
        return jsonify({"error": f"Error reading file: {str(e)}"}), 500


@dataset_bp.route("/materials/<int:dataset_id>/records/add", methods=["GET", "POST"])
@login_required
def add_material_record(dataset_id):
    """Add a new MaterialRecord to a MaterialsDataset"""
    from app import db
    from app.modules.dataset.models import DataSource, MaterialRecord

    dataset = materials_dataset_repository.get_by_id(dataset_id)
    if not dataset:
        abort(404, description="MaterialsDataset not found")

    # Check if user owns this dataset
    if dataset.user_id != current_user.id:
        abort(403, description="You don't have permission to modify this dataset")

    form = MaterialRecordForm()

    # Check if we're coming from the edit view
    return_to_edit = request.args.get("return_to") == "edit"

    if form.validate_on_submit():
        try:
            # If coming from edit view, save as temporary record (don't commit to DB yet)
            if return_to_edit:
                import json

                # Create temporary record data (not saved to DB)
                temp_record = {
                    "temp_id": f"temp_{int(time.time() * 1000)}",  # Unique temporary ID
                    "material_name": form.material_name.data,
                    "chemical_formula": form.chemical_formula.data,
                    "structure_type": form.structure_type.data,
                    "composition_method": form.composition_method.data,
                    "property_name": form.property_name.data,
                    "property_value": float(form.property_value.data),
                    "property_unit": form.property_unit.data,
                    "temperature": float(form.temperature.data) if form.temperature.data else None,
                    "pressure": float(form.pressure.data) if form.pressure.data else None,
                    "data_source": form.data_source.data if form.data_source.data else None,
                    "uncertainty": float(form.uncertainty.data) if form.uncertainty.data else None,
                    "description": form.description.data,
                }

                # Return intermediate template that saves to sessionStorage and redirects
                return render_template(
                    "dataset/save_temp_record.html", dataset=dataset, temp_record=json.dumps(temp_record)
                )

            # Normal flow: save directly to database
            new_record = MaterialRecord(
                materials_dataset_id=dataset_id,
                material_name=form.material_name.data,
                chemical_formula=form.chemical_formula.data,
                structure_type=form.structure_type.data,
                composition_method=form.composition_method.data,
                property_name=form.property_name.data,
                property_value=form.property_value.data,
                property_unit=form.property_unit.data,
                temperature=form.temperature.data,
                pressure=form.pressure.data,
                data_source=DataSource(form.data_source.data) if form.data_source.data else None,
                uncertainty=form.uncertainty.data,
                description=form.description.data,
            )

            db.session.add(new_record)
            db.session.commit()

            # Regenerate CSV file
            regenerate_csv_for_dataset(dataset_id)

            # Create version snapshot
            user_id = current_user.id
            db.session.remove()
            create_version_snapshot(dataset_id, user_id, "Added new material record")

            flash("Material record added successfully!", "success")
            return redirect(url_for("dataset.view_materials_dataset", dataset_id=dataset_id))

        except Exception as e:
            db.session.rollback()
            logger.exception(f"Error adding material record: {e}")
            flash(f"Error adding record: {str(e)}", "error")

    return render_template("dataset/material_record_form.html", form=form, dataset=dataset, action="Add", record=None)


@dataset_bp.route("/materials/<int:dataset_id>/records/<int:record_id>/edit", methods=["GET", "POST"])
@login_required
def edit_material_record(dataset_id, record_id):
    """Edit an existing MaterialRecord"""
    from app import db
    from app.modules.dataset.models import DataSource, MaterialRecord

    dataset = materials_dataset_repository.get_by_id(dataset_id)
    if not dataset:
        abort(404, description="MaterialsDataset not found")

    # Check if user owns this dataset
    if dataset.user_id != current_user.id:
        abort(403, description="You don't have permission to modify this dataset")

    record = db.session.query(MaterialRecord).filter_by(id=record_id, materials_dataset_id=dataset_id).first()
    if not record:
        abort(404, description="Material record not found")

    form = MaterialRecordForm(obj=record)

    # Check if we're coming from the edit view
    return_to_edit = request.args.get("return_to") == "edit"

    # Debug logging
    if request.method == "POST":
        with open("/tmp/selenium_edit_debug.log", "a") as f:
            f.write(f"POST to edit: record_id={record_id}, form_valid={form.validate_on_submit()}\n")
            if not form.validate():
                f.write(f"  Form errors: {form.errors}\n")

    if form.validate_on_submit():
        # Debug logging to file
        with open("/tmp/selenium_edit_debug.log", "a") as f:
            f.write(
                "EDIT CALLED: record_id={}, old_value={}, new_value={}\n".format(
                    record_id,
                    record.property_value,
                    form.property_value.data,
                )
            )
        try:
            # Update record
            record.material_name = form.material_name.data
            record.chemical_formula = form.chemical_formula.data
            record.structure_type = form.structure_type.data
            record.composition_method = form.composition_method.data
            record.property_name = form.property_name.data
            record.property_value = form.property_value.data
            record.property_unit = form.property_unit.data
            record.temperature = form.temperature.data
            record.pressure = form.pressure.data
            record.data_source = DataSource(form.data_source.data) if form.data_source.data else None
            record.uncertainty = form.uncertainty.data
            record.description = form.description.data

            # Commit changes to database
            db.session.commit()

            # Regenerate CSV file with fresh data
            regenerate_csv_for_dataset(dataset_id)

            # Only create version if NOT returning to edit view
            # When returning to edit, version will be created when "Save All Changes" is clicked
            if not return_to_edit:
                user_id = current_user.id
                db.session.remove()
                create_version_snapshot(dataset_id, user_id, f"Edited material record {record_id}")

            flash("Material record updated successfully!", "success")

            # Return to edit view or normal view depending on where we came from
            if return_to_edit:
                return redirect(url_for("dataset.edit_materials_dataset", dataset_id=dataset_id))
            else:
                return redirect(url_for("dataset.view_materials_dataset", dataset_id=dataset_id))

        except Exception as e:
            db.session.rollback()
            logger.exception(f"Error updating material record: {e}")
            flash(f"Error updating record: {str(e)}", "error")

    # Pre-populate form with existing data
    if request.method == "GET" and record.data_source:
        form.data_source.data = record.data_source.value

    return render_template(
        "dataset/material_record_form.html", form=form, dataset=dataset, action="Edit", record=record
    )


@dataset_bp.route("/materials/<int:dataset_id>/records/<int:record_id>/delete", methods=["POST"])
@login_required
def delete_material_record(dataset_id, record_id):
    """Delete a MaterialRecord"""
    from app import db
    from app.modules.dataset.models import MaterialRecord

    dataset = materials_dataset_repository.get_by_id(dataset_id)
    if not dataset:
        abort(404, description="MaterialsDataset not found")

    # Check if user owns this dataset
    if dataset.user_id != current_user.id:
        abort(403, description="You don't have permission to modify this dataset")

    record = db.session.query(MaterialRecord).filter_by(id=record_id, materials_dataset_id=dataset_id).first()
    if not record:
        abort(404, description="Material record not found")

    try:
        db.session.delete(record)
        db.session.commit()

        # Regenerate CSV file
        regenerate_csv_for_dataset(dataset_id)

        # Create version snapshot AFTER deleting
        create_version_snapshot(dataset_id, current_user.id, f"Deleted material record {record_id}")

        flash("Material record deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error deleting material record: {e}")
        flash(f"Error deleting record: {str(e)}", "error")

    return redirect(url_for("dataset.view_materials_dataset", dataset_id=dataset_id))


@dataset_bp.route("/materials/<int:dataset_id>/edit", methods=["GET", "POST"])
@login_required
def edit_materials_dataset(dataset_id):
    """Edit MaterialsDataset metadata (title, description, tags, etc.)"""
    from app import db

    try:
        dataset = materials_dataset_repository.get_by_id(dataset_id)

        if not dataset:
            abort(404, description="MaterialsDataset not found")

        if dataset.user_id != current_user.id:
            abort(403, description="You don't have permission to edit this dataset")

    except Exception as e:
        logger.exception(f"Error loading dataset {dataset_id} for editing: {e}")
        flash(f"Error loading dataset: {str(e)}", "error")
        return redirect(url_for("dataset.list_dataset"))

    if request.method == "GET":
        try:
            # Instantiate form without processing to avoid validation
            form = DataSetForm(formdata=None)

            # Populate form with current values
            form.title.data = dataset.ds_meta_data.title
            form.desc.data = dataset.ds_meta_data.description
            form.publication_type.data = dataset.ds_meta_data.publication_type.value
            form.publication_doi.data = dataset.ds_meta_data.publication_doi
            form.tags.data = dataset.ds_meta_data.tags

            # Note: Authors are not editable in this form (shown as read-only in template)

            # Get all records for this dataset
            records = material_record_repository.get_by_dataset(dataset_id)
            total_records = len(records)

            return render_template(
                "dataset/edit_materials_dataset.html",
                form=form,
                dataset=dataset,
                records=records,
                total_records=total_records,
            )

        except Exception as e:
            logger.exception(f"Error preparing edit form for dataset {dataset_id}: {e}")
            flash(f"Error loading edit form: {str(e)}", "error")
            return redirect(url_for("dataset.view_materials_dataset", dataset_id=dataset_id))

    # POST request
    form = DataSetForm()

    if form.validate_on_submit():
        try:
            changes_made = []
            records_changed = False

            # Update metadata (authors are not updated in this form)
            metadata_changed = False
            if dataset.ds_meta_data.title != form.title.data:
                logger.info(f"Title changed from '{dataset.ds_meta_data.title}' to '{form.title.data}'")
                dataset.ds_meta_data.title = form.title.data
                metadata_changed = True
                changes_made.append("title")
            if dataset.ds_meta_data.description != form.desc.data:
                logger.info("Description changed")
                dataset.ds_meta_data.description = form.desc.data
                metadata_changed = True
                changes_made.append("description")
            if dataset.ds_meta_data.publication_type != PublicationType(form.publication_type.data):
                logger.info("Publication type changed")
                dataset.ds_meta_data.publication_type = PublicationType(form.publication_type.data)
                metadata_changed = True
                changes_made.append("publication_type")
            if dataset.ds_meta_data.publication_doi != form.publication_doi.data:
                logger.info("Publication DOI changed")
                dataset.ds_meta_data.publication_doi = form.publication_doi.data
                metadata_changed = True
                changes_made.append("publication_doi")
            if dataset.ds_meta_data.tags != form.tags.data:
                logger.info("Tags changed")
                dataset.ds_meta_data.tags = form.tags.data
                metadata_changed = True
                changes_made.append("tags")

            logger.info(
                f"Metadata changed: {metadata_changed}, Records changed: {records_changed}, " f"Changes: {changes_made}"
            )

            # Process record deletions
            records_to_delete = request.form.get("records_to_delete", "[]")
            try:
                import json

                from app.modules.dataset.models import MaterialRecord

                records_to_delete_list = json.loads(records_to_delete)

                if records_to_delete_list:
                    for record_id in records_to_delete_list:
                        record = (
                            db.session.query(MaterialRecord)
                            .filter_by(id=record_id, materials_dataset_id=dataset_id)
                            .first()
                        )
                        if record:
                            db.session.delete(record)
                            records_changed = True
                    changes_made.append(f"{len(records_to_delete_list)} records deleted")
            except json.JSONDecodeError:
                logger.warning("Invalid records_to_delete JSON")

            # Check if any records were edited (tracked in sessionStorage and sent via form)
            records_to_edit = request.form.get("records_to_edit", "[]")
            try:
                records_to_edit_list = json.loads(records_to_edit)
                if records_to_edit_list:
                    records_changed = True
                    changes_made.append(f"{len(records_to_edit_list)} records edited")
            except json.JSONDecodeError:
                logger.warning("Invalid records_to_edit JSON")

            # Process temporary records to add (created during edit session)
            records_to_add = request.form.get("records_to_add", "[]")
            try:
                from app.modules.dataset.models import DataSource

                records_to_add_list = json.loads(records_to_add)

                if records_to_add_list:
                    for temp_record in records_to_add_list:
                        # Create new MaterialRecord from temporary data
                        new_record = MaterialRecord(
                            materials_dataset_id=dataset_id,
                            material_name=temp_record.get("material_name"),
                            chemical_formula=temp_record.get("chemical_formula"),
                            structure_type=temp_record.get("structure_type"),
                            composition_method=temp_record.get("composition_method"),
                            property_name=temp_record.get("property_name"),
                            property_value=temp_record.get("property_value"),
                            property_unit=temp_record.get("property_unit"),
                            temperature=temp_record.get("temperature"),
                            pressure=temp_record.get("pressure"),
                            data_source=(
                                DataSource(temp_record["data_source"]) if temp_record.get("data_source") else None
                            ),
                            uncertainty=temp_record.get("uncertainty"),
                            description=temp_record.get("description"),
                        )
                        db.session.add(new_record)
                        records_changed = True

                    changes_made.append(f"{len(records_to_add_list)} records added")
                    logger.info(f"Added {len(records_to_add_list)} temporary records to dataset {dataset_id}")
            except json.JSONDecodeError:
                logger.warning("Invalid records_to_add JSON")
            except Exception as e:
                logger.exception(f"Error adding temporary records: {e}")

            # Commit all changes to database
            db.session.commit()

            # Regenerate CSV if records changed or metadata changed
            # (need fresh CSV for version snapshot even if only metadata changed)
            if records_changed or metadata_changed:
                regenerate_csv_for_dataset(dataset_id)

            # Expire all cached objects to ensure fresh data for snapshot
            db.session.expire_all()

            # Create single version snapshot AFTER all changes
            if metadata_changed or records_changed:
                change_description = "Edited dataset: " + ", ".join(changes_made)
                create_version_snapshot(dataset_id, current_user.id, change_description)
                flash("Dataset updated successfully! All changes saved in a single version.", "success")
            else:
                flash("No changes were made.", "info")

            change_msg = change_description if (metadata_changed or records_changed) else "no changes"
            logger.info(f"Updated MaterialsDataset {dataset_id}: {change_msg}")

        except Exception as e:
            db.session.rollback()
            logger.exception(f"Error updating MaterialsDataset: {e}")
            flash(f"Error updating dataset: {str(e)}", "error")
            # Re-fetch records for template
            records = material_record_repository.get_by_dataset(dataset_id)
            total_records = len(records)
            return render_template(
                "dataset/edit_materials_dataset.html",
                form=form,
                dataset=dataset,
                records=records,
                total_records=total_records,
            )

        return redirect(url_for("dataset.view_materials_dataset", dataset_id=dataset_id))

    # If form validation fails, re-fetch records for template
    records = material_record_repository.get_by_dataset(dataset_id)
    total_records = len(records)
    return render_template(
        "dataset/edit_materials_dataset.html", form=form, dataset=dataset, records=records, total_records=total_records
    )


@dataset_bp.route("/materials/<int:dataset_id>/delete", methods=["POST"])
@login_required
def delete_materials_dataset(dataset_id):
    """Delete a MaterialsDataset completely (records, CSV file, and dataset)"""
    from app import db

    dataset = materials_dataset_repository.get_by_id(dataset_id)

    if not dataset:
        abort(404, description="MaterialsDataset not found")

    if dataset.user_id != current_user.id:
        abort(403, description="You don't have permission to delete this dataset")

    try:
        # Delete CSV file from filesystem if it exists
        if dataset.csv_file_path:
            csv_path = dataset.csv_file_path
            if not os.path.isabs(csv_path):
                csv_path = os.path.abspath(csv_path)

            if os.path.exists(csv_path):
                os.remove(csv_path)
                logger.info(f"Deleted CSV file: {csv_path}")

        # Delete dataset (cascade will delete material_records, download_records, view_records)
        dataset_title = dataset.ds_meta_data.title
        db.session.delete(dataset)
        db.session.commit()

        flash(f'Dataset "{dataset_title}" has been deleted successfully!', "success")
        logger.info(f"Deleted MaterialsDataset {dataset_id}")

    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error deleting MaterialsDataset: {e}")
        flash(f"Error deleting dataset: {str(e)}", "error")
        return redirect(url_for("dataset.materials_dataset_statistics", dataset_id=dataset_id))

    return redirect(url_for("dataset.list_dataset"))


# ==============================
# VERSION MANAGEMENT ROUTES
# ==============================
@dataset_bp.route("/materials/<int:dataset_id>/versions", methods=["GET"])
def list_versions(dataset_id):
    """List all versions for a dataset"""
    dataset = materials_dataset_repository.get_by_id(dataset_id)
    if not dataset:
        abort(404, description="MaterialsDataset not found")

    versions = dataset_version_service.list_versions(dataset_id)

    # Check if requesting JSON (API) or HTML
    if request.accept_mimetypes.best == "application/json":
        return jsonify(
            {
                "dataset_id": dataset_id,
                "dataset_title": dataset.ds_meta_data.title,
                "versions": [v.to_dict() for v in versions],
            }
        )

    return render_template("dataset/version_list.html", dataset=dataset, versions=versions)


@dataset_bp.route("/materials/<int:dataset_id>/versions/compare", methods=["GET"])
def compare_versions(dataset_id):
    """Compare two versions of a dataset"""
    dataset = materials_dataset_repository.get_by_id(dataset_id)
    if not dataset:
        abort(404, description="MaterialsDataset not found")

    version_id_1 = request.args.get("version_1", type=int)
    version_id_2 = request.args.get("version_2", type=int)
    comparison_type = request.args.get("type", "all")  # 'files', 'metadata', 'all'

    if not version_id_1 or not version_id_2:
        flash("Please select two versions to compare", "warning")
        return redirect(url_for("dataset.list_versions", dataset_id=dataset_id))

    version1 = dataset_version_service.get_version(version_id_1)
    version2 = dataset_version_service.get_version(version_id_2)

    if not version1 or not version2:
        abort(404, description="One or both versions not found")

    # Perform comparisons
    file_comparison = None
    metadata_comparison = None
    csv_diff = None

    if comparison_type in ["files", "all"]:
        file_comparison = dataset_version_service.compare_files(version_id_1, version_id_2)
        csv_diff = dataset_version_service.get_csv_diff(version_id_1, version_id_2)

    if comparison_type in ["metadata", "all"]:
        metadata_comparison = dataset_version_service.compare_metadata(version_id_1, version_id_2)

    # Check if requesting JSON (API) or HTML
    if request.accept_mimetypes.best == "application/json":
        return jsonify(
            {
                "dataset_id": dataset_id,
                "version_1": version1.to_dict(),
                "version_2": version2.to_dict(),
                "file_comparison": file_comparison,
                "metadata_comparison": metadata_comparison,
                "csv_diff": csv_diff,
            }
        )

    return render_template(
        "dataset/version_comparison.html",
        dataset=dataset,
        version1=version1,
        version2=version2,
        file_comparison=file_comparison,
        metadata_comparison=metadata_comparison,
        csv_diff=csv_diff,
    )


@dataset_bp.route("/materials/<int:dataset_id>/versions/<int:version_id>/download", methods=["GET"])
def download_version(dataset_id, version_id):
    """Download CSV file for a specific version"""
    dataset = materials_dataset_repository.get_by_id(dataset_id)
    if not dataset:
        abort(404, description="MaterialsDataset not found")

    version = dataset_version_service.get_version(version_id)
    if not version:
        abort(404, description="Version not found")

    if not version.csv_snapshot_path or not os.path.exists(version.csv_snapshot_path):
        flash("CSV file for this version not found", "error")
        return redirect(url_for("dataset.list_versions", dataset_id=dataset_id))

    directory = os.path.dirname(version.csv_snapshot_path)
    filename = os.path.basename(version.csv_snapshot_path)

    return send_from_directory(
        directory,
        filename,
        as_attachment=True,
        download_name=f"{dataset.ds_meta_data.title}_v{version.version_number}.csv",
    )
