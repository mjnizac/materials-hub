from core.blueprints.base_blueprint import BaseBlueprint

fakenodo_bp = BaseBlueprint('fakenodo', __name__, template_folder='templates')

# Asegura que models.py se importe (registra listeners o el modelo)
from . import models
