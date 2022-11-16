from flask import Blueprint
from flask_restplus import Api


from .resources.pharmacy import pharmacy_ns
from .resources.physician import physician_ns

from app.v1.models.pharmacy import register_ca_pharmacy_list_models
from app.v1.models.physician import register_physician_list_models


v2_blueprint = Blueprint('v2_blueprint', __name__, url_prefix='/api/v2')
api_v2 = Api(v2_blueprint,
             title='Directory API External',
             version='2.0',
             description='')


register_ca_pharmacy_list_models(pharmacy_ns)
register_physician_list_models(physician_ns)

api_v2.add_namespace(pharmacy_ns)
api_v2.add_namespace(physician_ns)