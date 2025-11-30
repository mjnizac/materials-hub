import logging
import hashlib
import uuid
import os

from app import db
from app.modules.dataset.models import DataSet
from app.modules.fakenodo.models import Deposition
from app.modules.featuremodel.models import FeatureModel
from core.configuration.configuration import uploads_folder_name
from dotenv import load_dotenv
from flask_login import current_user

from core.services.BaseService import BaseService

load_dotenv()
logger = logging.getLogger(__name__)

class FakenodoService(BaseService):

    def __init__(self):
        # Pasar None como repository si BaseService lo permite, o un dummy repository
        super().__init__(repository=None)

    def create_new_deposition(self, dataset: DataSet) -> dict:
        """
        Crea una Deposition local en la BD con estado 'draft' y devuelve un dict con id.
        """
        try:
            # Si dataset.ds_meta_data ya es un dict/JSON, úsalo directamente.
            dep_metadata = getattr(dataset, "ds_meta_data", {}) or {}
            dep = Deposition(
                dep_metadata=dep_metadata,
                status="draft",
                doi=None,
            )
            db.session.add(dep)
            db.session.commit()

            return {"conceptrecid": True, "id": dep.id}
        except Exception as e:
            logger.exception("Error creating new deposition: %s", e)
            db.session.rollback()
            raise

    def upload_file(self, dataset: DataSet, deposition_id: int, feature_model: FeatureModel, user=None) -> dict:
        """
        Implementación mínima: registra información del archivo en la deposición local.
        No realiza subida externa en este fakenodo.
        """
        try:
            # intentar obtener nombre del archivo desde el feature_model metadata
            try:
                uvl_filename = feature_model.fm_meta_data.get("uvl_filename") if getattr(feature_model, "fm_meta_data", None) else None
            except Exception:
                uvl_filename = None

            user_id = current_user.id if user is None and current_user and getattr(current_user, "is_authenticated", False) else getattr(user, "id", None)
            # aquí podrías mover/guardar el fichero real si lo deseas; por ahora devolvemos info mínima
            return {"deposition_id": deposition_id, "filename": uvl_filename, "user_id": user_id}
        except Exception as e:
            logger.exception("Error uploading file to deposition %s: %s", deposition_id, e)
            raise

    def publish_deposition(self, deposition_id: int) -> dict:
        """
        Marca la deposición como publicada y le asigna un DOI simulado.
        """
        try:
            dep = Deposition.query.get(deposition_id)
            if not dep:
                raise ValueError("Deposition not found")

            if not dep.doi:
                dep.doi = f"10.1234/fake.{uuid.uuid4().hex}"
            dep.status = "published"
            db.session.add(dep)
            db.session.commit()

            return {"id": dep.id, "status": dep.status, "doi": dep.doi}
        except Exception as e:
            logger.exception("Error publishing deposition %s: %s", deposition_id, e)
            db.session.rollback()
            raise

    def get_deposition(self, deposition_id: int) -> dict:
        dep = Deposition.query.get(deposition_id)
        if not dep:
            return {}
        return {"id": dep.id, "dep_metadata": dep.dep_metadata, "status": dep.status, "doi": dep.doi}

    def get_doi(self, deposition_id: int) -> str:
        dep = Deposition.query.get(deposition_id)
        return dep.doi if dep else None

def calculate_checksum(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
