from flask import Blueprint, jsonify
from flask_restplus import Api
import flask_jwt_extended as jwt
from jwt.exceptions import ExpiredSignatureError, DecodeError

from .resources.npi import npi_ns
from .resources.auth import auth_ns
from .resources.pharmacy import pharmacy_ns
from .resources.physician import physician_ns
from .resources.procedure import procedure_ns
from .resources.insurance_payer import insurance_ns
from .resources.pricing_directory import pricing_ns
from .models.npi import register_npi_models
from .models.auth import register_auth_models
from .models.insurance_payer import register_insurance_payer_info_models
from .models.pharmacy import register_ca_pharmacy_list_models
from .models.physician import register_physician_list_models
from .models.procedure import register_procedure_models
from .models.pricing_directory import register_pricing_directory_models
from .authorizations import authorizations_access_token, authorizations
from app.exceptions import InvalidRefererError


v1_blueprint = Blueprint('v1_blueprint', __name__, url_prefix='/api/v1')

api_v1 = Api(v1_blueprint,
             title='NPI API',
             version='1.0',
             description='')


register_auth_models(auth_ns)
register_npi_models(npi_ns)
register_ca_pharmacy_list_models(pharmacy_ns)
register_physician_list_models(physician_ns)
register_procedure_models(procedure_ns)
register_insurance_payer_info_models(insurance_ns)
register_pricing_directory_models(pricing_ns)

api_v1.add_namespace(auth_ns)
api_v1.add_namespace(npi_ns)
api_v1.add_namespace(pharmacy_ns)
api_v1.add_namespace(physician_ns)
api_v1.add_namespace(procedure_ns)
api_v1.add_namespace(insurance_ns)
api_v1.add_namespace(pricing_ns)


@v1_blueprint.errorhandler(jwt.exceptions.FreshTokenRequired)
@v1_blueprint.errorhandler(ExpiredSignatureError)
def handle_expired_signature_error(error):
    return jsonify({'message': 'Token expired'}), 401


@v1_blueprint.errorhandler(jwt.exceptions.InvalidHeaderError)
def handle_invalid_header_error(error):
    return jsonify({'message': "Bad Authorization header. Expected value 'Bearer <JWT>'"}), 401


@v1_blueprint.errorhandler(jwt.exceptions.WrongTokenError)
@v1_blueprint.errorhandler(DecodeError)
def handle_invalid_token_error(error):
    print(f"error: {error}")
    return jsonify({'message': 'Token incorrect, supplied or malformed'}), 401


@v1_blueprint.errorhandler(jwt.exceptions.NoAuthorizationError)
def handle_missing_token_error(error):
    print(f"error: {error}")
    return jsonify({'message': 'Missing Authorization Header'}), 401


@v1_blueprint.errorhandler(InvalidRefererError)
def handle_invalid_header_error(error):
    print(f"error: {error}")
    return jsonify({'msg': str(error)}), 401
