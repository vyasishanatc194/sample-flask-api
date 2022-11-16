from flask_restplus import Model, fields


auth_model = Model('Auth', {
    'app_api_token': fields.String(description="App api token", required=True, example='api-auth-token'),
    'email': fields.String(description="Email Address", required=True, example='akumin@blockhealth.co'),
})


def register_auth_models(ns):
    ns.models[auth_model.name] = auth_model
