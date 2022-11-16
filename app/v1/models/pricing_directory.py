from flask_restplus import Model, fields
from decimal import Decimal

pricing_directory_model = Model('us_procedure_pricing_directory', {
    'id': fields.Integer(description="Database Table ID of Procedure pricing", required=False, example=75),
    'profile_group': fields.String(description="Profile Group", required=True),
    'profile_name': fields.String(description="Profile Name", required=True),
    'procedure_code': fields.String(description="Procedure Code", required=True),
    'global_fee': fields.Fixed(decimals=2)
})


def register_pricing_directory_models(ns):
    ns.models[pricing_directory_model.name] = pricing_directory_model
