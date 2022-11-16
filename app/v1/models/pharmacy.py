from flask_restplus import Model, fields


ca_pharmacy_list_model = Model('Pharmacy', {
    'id': fields.Integer(description="Database Table ID of Pharmacy", required=False, example=75),
    'pharmacy': fields.String(description="Pharmacy Name", required=True),
    'address': fields.String(description="Pharmacy Address", required=True),
    'phone': fields.String(description="Pharmacy Phone", required=True),
})


def register_ca_pharmacy_list_models(ns):
    ns.models[ca_pharmacy_list_model.name] = ca_pharmacy_list_model
