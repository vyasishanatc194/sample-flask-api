import fnmatch
import urllib.parse
from functools import wraps
import flask_jwt_extended as jwt
from flask import current_app, request
from flask_jwt_extended.view_decorators import verify_jwt_in_request
try:
    from flask import _app_ctx_stack as ctx_stack
except ImportError:  # pragma: no cover
    from flask import _request_ctx_stack as ctx_stack
import app.constants as C
from app.exceptions import InvalidRefererError


def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        referral_check = getattr(ctx_stack.top, 'jwt_header', {}).get('referral_check', True)
        scopes = getattr(ctx_stack.top, 'jwt_header', {}).get('scopes', 'all')
        print(f"jwt_header: {getattr(ctx_stack.top, 'jwt_header', {})}")
        if referral_check:
            referer_check()
        scope_check(scopes)
        print(f"executing function: {fn} with args: {args} ::and:: kwargs: {kwargs} ")
        return fn(*args, **kwargs)
    return wrapper


def referer_check() -> bool:
    """

    :return:
    """

    if not current_app.config.get('ENABLE_REFERER_CHECK', False):
        return True
    referer = request.headers.get("Referer", "")
    parts = urllib.parse.urlsplit(referer)
    try:
        host_to_match = parts.netloc.rsplit(':', 1)[0]
    except Exception as err:
        current_app.logger.warning(f'error: {err}')
        host_to_match = ''
    for pattern in current_app.config.get('VALID_REFERER_LIST', []):
        if fnmatch.fnmatch(host_to_match, pattern):
            current_app.logger.info(f"pattern: {pattern}; referer: {referer}")
            return True
    raise InvalidRefererError(f"Invalid Referer: {referer}")


def scope_check(scopes: str) -> bool:
    """

    :param scopes:
    :return:
    """
    print(f"scope_check with {scopes}")
    valid_scopes = [_.strip() for _ in scopes.split(',') if _.strip() in C.AVAILABLE_SCOPES]
    print(f"valid_scopes: {valid_scopes}")
    if valid_scopes:
        return True
    print("raise error")
    raise jwt.exceptions.WrongTokenError("scope not allowed")
