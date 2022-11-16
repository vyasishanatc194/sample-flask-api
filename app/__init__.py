import os
import logging
import sentry_sdk
import google.cloud.logging

from flask import Flask
from flask_cors import CORS
from logging.config import dictConfig
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from werkzeug.middleware.proxy_fix import ProxyFix
from sentry_sdk.integrations.flask import FlaskIntegration

from config import config as app_config
from app.models import db
from .npi_app import NpiQuery


npi_query = NpiQuery()


def create_app(config=None):
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=2, x_host=1)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    config_name = config
    if not isinstance(config, str):
        # default configuration class name
        config_name = os.getenv('FLASK_CONFIG', 'default')
    app.config.from_object(app_config[config_name])
    dictConfig(app.config["LOGGIN"])
    if app.config.get("ENABLE_GCLOUD_LOGGING"):
        cloud_logger = google.cloud.logging.Client()
        cloud_logger.setup_logging(log_level=logging.INFO, name="npi_api")
        logging.info(f"cloud_logger: {cloud_logger}\n")
    if app.config.get("ENABLE_SENTRY_TRACKING"):
        sentry_sdk.init(
            dsn=f"https://{app.config.get('SENTRY_SECURITY_TOKEN')}@o647371.ingest.sentry.io/"
                f"{app.config.get('SENTRY_PROJECT_ID')}",
            integrations=[FlaskIntegration()],

            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production.
            traces_sample_rate=1.0
        )
    CORS(app)
    db.init_app(app)
    npi_query.init(db)
    jwt = JWTManager(app)
    from .v1 import v1_blueprint
    from .v2 import v2_blueprint
    app.register_blueprint(v1_blueprint)
    app.register_blueprint(v2_blueprint)
    return app
