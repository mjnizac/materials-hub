from flask_restful import Api

from core.blueprints.base_blueprint import BaseBlueprint

dataset_bp = BaseBlueprint("dataset", __name__, template_folder="templates")


api = Api(dataset_bp)

# Importación diferida para evitar ciclos de importación
from app.modules.dataset.api import init_blueprint_api
init_blueprint_api(api)
