from flask_restplus import Model, fields


procedure_model = Model('Procedure', {
    'CPT_CODE': fields.String(description="CPT code", required=True),
    'DESCRIPTION': fields.String(description="Description", required=True),
})


def register_procedure_models(ns):
    ns.models[procedure_model.name] = procedure_model
