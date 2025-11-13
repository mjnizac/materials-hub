import json
import logging
import os
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from zipfile import ZipFile

from flask import (
    abort,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required

from app.modules.dataset import dataset_bp
from app.modules.dataset.forms import DataSetForm
from app.modules.dataset.models import DSDownloadRecord
from app.modules.dataset.services import (
    AuthorService,
    DataSetService,
    DOIMappingService,
    DSDownloadRecordService,
    DSMetaDataService,
    DSViewRecordService,
)
from app.modules.zenodo.services import ZenodoService

logger = logging.getLogger(__name__)
dataset_service = DataSetService()
author_service = AuthorService()
dsmetadata_service = DSMetaDataService()
zenodo_service = ZenodoService()
doi_mapping_service = DOIMappingService()
ds_view_record_service = DSViewRecordService()


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
            logger.info("Creating dataset...")
            dataset = dataset_service.create_from_form(form=form, current_user=current_user)
            logger.info(f"Created dataset: {dataset}")
            dataset_service.move_feature_models(dataset)
        except Exception as exc:
            logger.exception(f"Exception while create dataset data in local {exc}")
            return jsonify({"Exception while create dataset data in local: ": str(exc)}), 400

        data = {}
        try:
            zenodo_response_json = zenodo_service.create_new_deposition(dataset)
            response_data = json.dumps(zenodo_response_json)
            data = json.loads(response_data)
        except Exception as exc:
            data = {}
            logger.exception(f"Exception while create dataset data in Zenodo {exc}")

        if data.get("conceptrecid"):
            deposition_id = data.get("id")

            dataset_service.update_dsmetadata(dataset.ds_meta_data_id, deposition_id=deposition_id)

            try:
                for feature_model in dataset.feature_models:
                    zenodo_service.upload_file(dataset, deposition_id, feature_model)

                zenodo_service.publish_deposition(deposition_id)
                deposition_doi = zenodo_service.get_doi(deposition_id)
                dataset_service.update_dsmetadata(dataset.ds_meta_data_id, dataset_doi=deposition_doi)
            except Exception as e:
                msg = f"Error uploading feature models or updating DOI: {e}"
                return jsonify({"message": msg}), 200

        file_path = current_user.temp_folder()
        if os.path.exists(file_path) and os.path.isdir(file_path):
            shutil.rmtree(file_path)

        return jsonify({"message": "Everything works!"}), 200

    return render_template("dataset/upload_dataset.html", form=form)


@dataset_bp.route("/dataset/list", methods=["GET", "POST"])
@login_required
def list_dataset():
    return render_template(
        "dataset/list_datasets.html",
        datasets=dataset_service.get_synchronized(current_user.id),
        local_datasets=dataset_service.get_unsynchronized(current_user.id),
    )


@dataset_bp.route("/dataset/file/upload", methods=["POST"])
@login_required
def upload():
    file = request.files["file"]
    temp_folder = current_user.temp_folder()

    if not file or not file.filename.endswith(".uvl"):
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

    return jsonify({
        "message": "UVL uploaded and validated successfully",
        "filename": new_filename,
    }), 200


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
    dataset = dataset_service.get_or_404(dataset_id)

    file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"dataset_{dataset_id}.zip")

    with ZipFile(zip_path, "w") as zipf:
        for subdir, dirs, files in os.walk(file_path):
            for file in files:
                full_path = os.path.join(subdir, file)
                relative_path = os.path.relpath(full_path, file_path)
                zipf.write(full_path, arcname=os.path.join(os.path.basename(zip_path[:-4]), relative_path))

    user_cookie = request.cookies.get("download_cookie")
    if not user_cookie:
        user_cookie = str(uuid.uuid4())
        resp = make_response(send_from_directory(temp_dir, f"dataset_{dataset_id}.zip", as_attachment=True))
        resp.set_cookie("download_cookie", user_cookie)
    else:
        resp = send_from_directory(temp_dir, f"dataset_{dataset_id}.zip", as_attachment=True)

    existing_record = DSDownloadRecord.query.filter_by(
        user_id=current_user.id if current_user.is_authenticated else None,
        dataset_id=dataset_id,
        download_cookie=user_cookie,
    ).first()

    if not existing_record:
        DSDownloadRecordService().create(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset_id,
            download_date=datetime.now(timezone.utc),
            download_cookie=user_cookie,
        )

    return resp


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

    dataset = ds_meta_data.data_set
    recommended_datasets = dataset_service.get_recommendations(dataset.id, limit=5)

    user_cookie = ds_view_record_service.create_cookie(dataset=dataset)

    resp = make_response(render_template(
        "dataset/view_dataset.html",
        dataset=dataset,
        recommended_datasets=recommended_datasets
    ))
    resp.set_cookie("view_cookie", user_cookie)
    return resp


@dataset_bp.route("/dataset/<int:dataset_id>/recommendations")
def dataset_recommendations(dataset_id):
    """API para devolver datasets recomendados filtrados y paginados (AJAX)."""
    page = request.args.get("page", 1, type=int)
    filter_type = request.args.get("filter_type", None, type=str)

    current_dataset = dataset_service.get_or_404(dataset_id)
    query = dataset_service.get_all_except(dataset_id)

    # Aplicar filtros usando los métodos del service
    if filter_type == "authors":
        query = dataset_service.filter_by_authors(query, current_dataset)
    elif filter_type == "tags":
        query = dataset_service.filter_by_tags(query, current_dataset)
    elif filter_type == "communities":
        query = dataset_service.filter_by_community(query, current_dataset)

    # Paginación
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page
    paginated = query[start:end]
    total_pages = (len(query) + per_page - 1) // per_page

    html = render_template(
        "dataset/recommendations_table.html",
        recommended_datasets=paginated
    )

    return jsonify({
        "html": html,
        "page": page,
        "total_pages": total_pages
    })


@dataset_bp.route("/doi/<path:doi>/recommendations")
def dataset_recommendations_by_doi(doi):
    """Devuelve datasets recomendados filtrados y paginados cuando se usa DOI."""
    ds_meta_data = dsmetadata_service.filter_by_doi(doi)
    if not ds_meta_data:
        abort(404)

    dataset = ds_meta_data.data_set
    dataset_id = dataset.id

    page = request.args.get("page", 1, type=int)
    filter_type = request.args.get("filter_type", None, type=str)

    current_dataset = dataset_service.get_or_404(dataset_id)
    query = dataset_service.get_all_except(dataset_id)

    # Aplicar filtros usando los métodos del service
    if filter_type == "authors":
        query = dataset_service.filter_by_authors(query, current_dataset)
    elif filter_type == "tags":
        query = dataset_service.filter_by_tags(query, current_dataset)
    elif filter_type == "communities":
        query = dataset_service.filter_by_community(query, current_dataset)

    # Paginación
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page
    paginated = query[start:end]
    total_pages = (len(query) + per_page - 1) // per_page

    html = render_template(
        "dataset/recommendations_table.html",
        recommended_datasets=paginated
    )

    return jsonify({
        "html": html,
        "page": page,
        "total_pages": total_pages
    })


@dataset_bp.route("/dataset/unsynchronized/<int:dataset_id>/", methods=["GET"])
@login_required
def get_unsynchronized_dataset(dataset_id):
    dataset = dataset_service.get_unsynchronized_dataset(current_user.id, dataset_id)
    if not dataset:
        abort(404)

    recommended_datasets = dataset_service.get_recommendations(dataset_id, limit=3)

    return render_template(
        "dataset/view_dataset.html",
        dataset=dataset,
        recommended_datasets=recommended_datasets
    )


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

    datasets = dataset_service.get_top_global(metric=metric, limit=limit, days=days)

    return render_template(
        "dataset/top_global.html",
        datasets=datasets,
        metric=metric,
        days=days,
        limit=limit,
    )