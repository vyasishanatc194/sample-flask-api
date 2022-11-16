from flask_restplus import Model, fields


insurance_payer_info_model = Model('InsuranceInfo', {
    'id': fields.Integer(description="Database Table ID of Insurance Payer Info", required=False, example=75),
    'insurance_code': fields.String(description="Insurance Code", required=True),
    'plan': fields.String(description="Insurance Plan", required=True),
    'plan_type': fields.String(description="Plan Type", required=True),
})


def register_insurance_payer_info_models(ns):
    ns.models[insurance_payer_info_model.name] = insurance_payer_info_model
