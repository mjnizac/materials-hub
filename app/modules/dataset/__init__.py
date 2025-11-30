from flask_restful import Api

from core.blueprints.base_blueprint import BaseBlueprint

dataset_bp = BaseBlueprint("dataset", __name__, template_folder="templates")
dataset_api = Api(dataset_bp)


def init_api():
    """Inicializa la API después de que todos los módulos se hayan cargado"""
    from app.modules.dataset.api import init_blueprint_api  # noqa: E402

    init_blueprint_api(dataset_api)
