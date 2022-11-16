import os
import datetime
from logging.config import dictConfig
from secret_to_env import set_secret_to_env
from neo4j import GraphDatabase, basic_auth

set_secret_to_env()


class Config:

    APP_NAME = os.environ.get('APP_NAME', 'NPI API')

    # will be used to encrypt session key
    SECRET_KEY = os.environ.get('SECRET_KEY', "SECRET_KEY")

    TRUTH_VALUES = [True, 1, '1', 'True', 'true', 'TRUE']

    PROPAGATE_EXCEPTIONS = os.getenv("PROPAGATE_EXCEPTIONS", True) in TRUTH_VALUES

    # project directory (absolute path), path containing config.py file
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    STATIC_FILE_PATH = os.path.join(BASE_DIR, "app/static")

    DB_USER = os.getenv("DB_USER", "ahsan_dev").strip()
    DB_PASS = os.getenv("DB_PASS", "").strip()
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1").strip()
    DB_NAME = os.getenv("DB_NAME", "directory_dev").strip()

    AUTH_DB_USER = os.getenv("AUTH_DB_USER", DB_USER).strip()
    AUTH_DB_PASS = os.getenv("AUTH_DB_PASS", DB_PASS).strip()
    AUTH_DB_NAME = os.getenv("AUTH_DB_NAME", DB_NAME).strip()
    AUTH_DB_HOST = os.getenv("AUTH_DB_HOST", DB_HOST).strip()

    NEO4j_DB_USER = os.getenv("NEO4J_DB_USER").strip()
    NEO4j_DB_PASS = os.getenv("NEO4J_DB_PASS").strip()
    NEO4j_DB_NAME = os.getenv("NEO4J_DB_NAME").strip()
    NEO4j_DB_HOST = os.getenv("NEO4J_DB_HOST").strip()


    # NEO4J_DATABASE_URI = "bolt://{NEO4J_USERNAME}:{NEO4J_PASSWORD}@{localhost}:{7687}"
    NEO4J_DATABASE_URI = "bolt://{NEO4j_DB_USER}:{NEO4j_DB_PASS}@{NEO4j_DB_HOST}"

    driver = GraphDatabase.driver("bolt://52.72.13.205:47929", auth=basic_auth("neo4j", "neo4j"))


    # SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR}/dummy.db"

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_BINDS = {
        'npi': SQLALCHEMY_DATABASE_URI,
        'auth': f"mysql+pymysql://{AUTH_DB_USER}:{AUTH_DB_PASS}@{AUTH_DB_HOST}/{AUTH_DB_NAME}"
    }

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', os.getenv('JWT_SECRET_KEY_LOCAL', 'super-secret-key'))

    AUTH_KEY_SALT = os.getenv('AUTH_KEY_SALT', os.getenv('AUTH_KEY_SALT_LOCAL', 'super-secret-key'))

    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=60 * 24)
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=30 * 3)

    APP_API_TOKENS = os.getenv("APP_API_TOKENS", "api-auth-token").split(",")

    AUTH_TABLE_NAME = os.getenv("AUTH_TABLE_NAME", "clinic_support_user_info")

    AUTH_KEY_TABLE_NAME = os.getenv("AUTH_KEY_TABLE_NAME", "auth_api_key")

    CLINIC_TABLE_NAME = os.getenv("CLINIC_TABLE_NAME", "clinic_user_info")

    US_PROCEDURE_PRICING_DIRECTORY = os.getenv("US_PROCEDURE_PRICING_DIRECTORY", "us_procedure_pricing_directory")

    REFRESH_TOKEN_RECORD_TABLE = os.getenv("REFRESH_TOKEN_RECORD_TABLE", "form_builder_refresh_token_record")

    PHARMACY_LIST_TABLE_NAME = os.getenv("PHARMACY_LIST_TABLE_NAME", "ca_pharmacy_list")

    PHYSICIAN_TABLE_CA = os.getenv("PHYSICIAN_TABLE_CA", "unified_stored_physicians_ca")

    PHYSICIAN_TABLE_US = os.getenv("PHYSICIAN_TABLE_US", "npi")

    CPT_INFO_AKUMIN = os.getenv("CPT_INFO_AKUMIN", "cpt_info_akumin")
    INSURANCE_TABLE = os.getenv("INSURANCE_TABLE", "insurance_info")

    ENABLE_GCLOUD_LOGGING = os.getenv("ENABLE_GCLOUD_LOGGING", True) in TRUTH_VALUES

    ENABLE_REFERER_CHECK = os.getenv("ENABLE_REFERER_CHECK", False) in TRUTH_VALUES

    VALID_REFERER_LIST = [_.strip() for _ in
                          os.getenv("VALID_REFERER_LIST",
                                    "*.blockhealth.co,*.phelix.ai,127.0.0.1,localhost").split(",")]

    ENABLE_SENTRY_TRACKING = os.getenv("ENABLE_SENTRY_TRACKING", True) in TRUTH_VALUES

    SENTRY_SECURITY_TOKEN = os.getenv("SENTRY_SECURITY_TOKEN", "").strip()

    SENTRY_PROJECT_ID = os.getenv("SENTRY_PROJECT_ID", "").strip()

    LOGGIN = {
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {
            'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            },
            # TODO: have to remove file handler
            'file': {
                'class': 'logging.FileHandler',
                'formatter': 'default',
                'filename': '/tmp/flask_app.log',
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi', 'file']
        }
    }

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    # will be used to encrypt session key
    SECRET_KEY = os.environ.get('SECRET_KEY', '115f35ce-fc2a-4ba5-94a6-22e512f1b312')


try:
    from production_config import ProductionConfig as MainProductionConfig

    class ProductionConfig(Config, MainProductionConfig):
        pass
except ImportError:
    class ProductionConfig(DevelopmentConfig):
        DEBUG = False


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig,
    'production': ProductionConfig
}
