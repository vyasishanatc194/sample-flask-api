from flask_restplus import Model, fields


physician_model = Model('Physician', {
    'ProviderBillingNo': fields.String(description="ProviderBillingNo", required=False),
    'ProviderCode': fields.String(description="ProviderCode", required=False),
    'ProviderLastName': fields.String(description="ProviderLastName", required=True),
    'ProviderFirstName': fields.String(description="ProviderFirstName", required=True),
    'ProviderName': fields.String(description="ProviderName", required=False),
    'ProviderPracticeAddress1': fields.String(description="ProviderPracticeAddress1", required=False),
    'ProviderPracticeAddress2': fields.String(description="ProviderPracticeAddress2", required=False),
    'ProviderPracticeTelephone': fields.String(description="ProviderPracticeTelephone", required=False),
    'ProviderPracticeFax': fields.String(description="ProviderPracticeFax", required=False),
    'ProviderPracticeCity': fields.String(description="ProviderPracticeCity", required=False),
    'ProviderPracticeState': fields.String(description="ProviderPracticeState", required=False),
    'ProviderPracticeCountry': fields.String(description="ProviderPracticeCountry", required=False),
})

physician_update_model = Model('physician_update_model', {
    'ProviderBillingNo': fields.String(description="ProviderBillingNo", required=False),
    'ProviderLastName': fields.String(description="ProviderLastName", required=True),
    'ProviderFirstName': fields.String(description="ProviderFirstName", required=True),
    'ProviderName': fields.String(description="ProviderName", required=False),
    'ProviderPracticeAddress1': fields.String(description="ProviderPracticeAddress1", required=False),
    'ProviderPracticeAddress2': fields.String(description="ProviderPracticeAddress2", required=False),
    'ProviderPracticeTelephone': fields.String(description="ProviderPracticeTelephone", required=False),
    'ProviderPracticeFax': fields.String(description="ProviderPracticeFax", required=False),
    'ProviderPracticeCity': fields.String(description="ProviderPracticeCity", required=False),
    'ProviderPracticeState': fields.String(description="ProviderPracticeState", required=False),
    'ProviderPracticeCountry': fields.String(description="ProviderPracticeCountry", required=False),
})


def register_physician_list_models(ns):
    ns.models[physician_model.name] = physician_model
    ns.models[physician_update_model.name] = physician_update_model
