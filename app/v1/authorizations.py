try:
    from flask import _app_ctx_stack as ctx_stack
except ImportError:  # pragma: no cover
    from flask import _request_ctx_stack as ctx_stack


authorizations_access_token = "AccessToken"

authorizations_auth_password = "authPass"


authorizations = {
    authorizations_access_token: {
        'type': "apiKey",
        'in': 'header',
        'name': 'Authorization'
    }
}


def get_jwt_detail():
    return ctx_stack.top.jwt
