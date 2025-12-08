import os
import secrets


class ConfigManager:
    def __init__(self, app):
        self.app = app

    def load_config(self, config_name=None):
        if config_name is None:
            config_name = os.getenv("FLASK_ENV", "development")

        if config_name == "testing":
            self.app.config.from_object(TestingConfig)
        elif config_name == "production":
            self.app.config.from_object(ProductionConfig)
        else:
            self.app.config.from_object(DevelopmentConfig)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TIMEZONE = "Europe/Madrid"
    TEMPLATES_AUTO_RELOAD = True
    UPLOAD_FOLDER = "uploads"

    # Detect DATABASE_URL (Render) or construir manualmente
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or (
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER', 'default_user')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'default_password')}@"
        f"{os.getenv('POSTGRES_HOSTNAME', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DATABASE', 'default_db')}"
    )


class DevelopmentConfig(Config):
    DEBUG = True
    # Opcional: valores locales por defecto
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or (
        "postgresql+psycopg2://local_user:local_pass@localhost:5432/local_db"
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or (
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER', 'default_user')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'default_password')}@"
        f"{os.getenv('POSTGRES_HOSTNAME', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_TEST_DATABASE', 'default_test_db')}"
    )
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
