from flask_restful import Api

from core.blueprints.base_blueprint import BaseBlueprint

dataset_bp = BaseBlueprint("dataset", __name__, template_folder="templates")
dataset_api = Api(dataset_bp)


def normalize_value(val):
    """
    Normalize values for comparison in templates.
    Treats numeric values equivalently (e.g., '300' == '300.0')
    """
    if val is None or val == "" or val == "None":
        return ""

    val_str = str(val).strip()

    # Try to normalize numeric values
    try:
        num_val = float(val_str)
        # If it's a whole number, return as integer string
        if num_val == int(num_val):
            return str(int(num_val))
        else:
            return str(num_val)
    except (ValueError, TypeError):
        # Not a number, return as-is
        return val_str


# Register template filter
dataset_bp.add_app_template_filter(normalize_value, "normalize_value")


def init_api():
    """Inicializa la API después de que todos los módulos se hayan cargado"""
    from app.modules.dataset.api import init_blueprint_api  # noqa: E402

    init_blueprint_api(dataset_api)
