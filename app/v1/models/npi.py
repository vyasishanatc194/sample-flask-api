from flask_restplus import Model, fields, errors
import app.constants as C


npi_query_model = Model('NpiQueryModel', {
    C.MODEL_FIELD_QUERY: fields.String(description="NPI Query String", required=True,
                                       example='Richard Grimsley'),
    C.MODEL_FIELD_FORMATTED: fields.Boolean(default=False, required=False),
    C.MODEL_FIELD_PROVIDER_CODE_EQUALITY: fields.Boolean(default=False, required=False),
    C.MODEL_FIELD_LIMIT: fields.Integer(required=False, default=20, example=20),
    C.MODEL_FIELD_SKIP: fields.Integer(required=False, default=0),
})


def register_npi_models(ns):
    ns.models[npi_query_model.name] = npi_query_model
