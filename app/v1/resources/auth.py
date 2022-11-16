import time
import datetime
from flask import current_app, request
from flask_restplus import Resource, Namespace
from sqlalchemy.sql import text

from app.models import db
from app.utils import timedelta_to_seconds
from app.refresh_token_utils import (create_refresh_token_record, is_refresh_token_valid,
                                     update_refresh_token_record, create_hash)
from .mixins import GetPayloadMixIn
from ..models.auth import auth_model
from ..parser import auth_refresh_token_header_parser
from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity
)
try:
    from flask import _app_ctx_stack as ctx_stack
except ImportError:  # pragma: no cover
    from flask import _request_ctx_stack as ctx_stack


auth_ns = Namespace('auth', description="Auth", path="/auth")


@auth_ns.route('/')
class Login(GetPayloadMixIn, Resource):

    @auth_ns.expect(auth_model, validate=True)
    def post(self):
        current_app.logger.info("post")
        payload = self.get_payload(auth_ns, auth_model)
        current_app.logger.info("payload")
        email, app_api_token = payload['email'], payload['app_api_token']
        sql = text(f"""SELECT `user`.`id`, `user`.`clinic_id`, `user`.`type`,
                    `clinic`.`clinic_key`, `clinic`.`clinic_type`, `clinic`.`country`, 
                    `clinic`.`state`, `clinic`.`emr_pathway`, `clinic`.`clinic_group`, 
                    `clinic`.`clinic_short_name`
                    FROM {current_app.config["AUTH_TABLE_NAME"]} `user`
                    INNER JOIN {current_app.config['CLINIC_TABLE_NAME']} AS `clinic`
                    ON (`clinic`.`id` = `user`.`clinic_id`)
                    WHERE `user`.`email_id` = :email AND `user`.`active` = 1;""")
        try:
            res = db.get_engine(bind="auth").execute(sql, {"email": email})
            user = res.fetchone()
            print(f"user: {user['clinic_id']}\n")
        except Exception as err:
            user = None
            current_app.logger.error(f"failed to fetch user: {err}")
        if user is None or app_api_token not in current_app.config["APP_API_TOKENS"]:
            current_app.logger.warning("Auth Failed: Bad username or password")
            return {"msg": "Bad username or password"}, 401
        user_scopes = 'all'
        referral_check = True
        user_claims = {"id": user['id'], 'table': current_app.config["AUTH_TABLE_NAME"],
                       'clinic_key': user['clinic_key'],
                       'clinic_type': user['clinic_type'],
                       'country': user['country'],
                       'state': user['state'],
                       'emr_pathway': user['emr_pathway'],
                       'clinic_group': user['clinic_group'],
                       'clinic_short_name': user['clinic_short_name'],
                       }
        # Identity can be any data that is json serializable
        access_token = create_access_token(identity=user['clinic_id'],
                                           user_claims=user_claims,
                                           headers={"referral_check": referral_check, 'scopes': user_scopes})
        refresh_token = create_refresh_token(identity=user['clinic_id'],
                                             user_claims=user_claims,
                                             headers={"referral_check": referral_check, 'scopes': user_scopes})
        expires_at = datetime.datetime.utcnow() + current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        expires_at_timestamp = int(time.time()) + timedelta_to_seconds(current_app.config["JWT_ACCESS_TOKEN_EXPIRES"])
        refresh_token_expires_at_timestamp = (int(time.time()) +
                                              timedelta_to_seconds(current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]))
        create_refresh_token_record({
            "reference_value": email,
            "reference_source": current_app.config["AUTH_TABLE_NAME"],
            "reference_type": "email_id",
            "token_hash": create_hash(refresh_token),
            "is_active": True,
            "expire_at": datetime.datetime.utcnow() + current_app.config["JWT_REFRESH_TOKEN_EXPIRES"],
            "app_info": "form_builder",
            "app_identifier": create_hash(payload['app_api_token'])
        })
        current_app.logger.info("auth new access token generated")
        return {"access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S"),
                "expires_at_timestamp": expires_at_timestamp,
                "refresh_token_expires_at_timestamp": refresh_token_expires_at_timestamp}, 200


@auth_ns.route('/refresh/')
class AuthRefresh(Resource):

    @auth_ns.expect(auth_refresh_token_header_parser, validate=True)
    @jwt_refresh_token_required
    def post(self, *args, **kwargs):
        refresh_token = request.headers.get('Authorization', '').replace('Bearer ', '', 1).strip()
        refresh_token_hash = create_hash(refresh_token)
        old_token_details = is_refresh_token_valid(refresh_token_hash)
        print(f'ctx_stack.top.jwt: {ctx_stack.top.jwt}')
        print(f'ctx_stack.top.jwt_header: {ctx_stack.top.jwt_header}')
        if not old_token_details.get("reference_value"):
            current_app.logger.warning("Refresh Token is not valid.")
            return {'message': 'Refresh Token is not valid.'}, 401
        update_refresh_token_record(refresh_token_hash, is_active=False)
        current_user = get_jwt_identity()
        expires_at = datetime.datetime.utcnow() + current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        expires_at_timestamp = int(time.time()) + timedelta_to_seconds(current_app.config["JWT_ACCESS_TOKEN_EXPIRES"])
        new_refresh_token = create_refresh_token(
            identity=current_user,
            user_claims=ctx_stack.top.jwt.get('user_claims'),
            headers={"referral_check": ctx_stack.top.jwt_header.get('referral_check'),
                     'scopes': ctx_stack.top.jwt_header.get('scopes')}
        )
        create_refresh_token_record({
            "reference_value": old_token_details.get("reference_value"),
            "reference_source": old_token_details.get("reference_source"),
            "reference_type": old_token_details.get("reference_type"),
            "token_hash": create_hash(new_refresh_token),
            "is_active": True,
            "expire_at": datetime.datetime.utcnow() + current_app.config["JWT_REFRESH_TOKEN_EXPIRES"],
            "app_info": old_token_details.get("app_info"),
            "app_identifier": old_token_details.get("app_identifier")
        })
        ret = {
            'access_token': create_access_token(
                identity=current_user,
                user_claims=ctx_stack.top.jwt.get('user_claims'),
                headers={"referral_check": ctx_stack.top.jwt_header.get('referral_check'),
                         'scopes': ctx_stack.top.jwt_header.get('scopes')}
            ),
            'expires_at': expires_at.strftime("%Y-%m-%d %H:%M:%S"),
            'expires_at_timestamp': expires_at_timestamp,
            "refresh_token": new_refresh_token,
            "refresh_token_expires_at_timestamp": (
                    int(time.time()) + timedelta_to_seconds(current_app.config["JWT_REFRESH_TOKEN_EXPIRES"])
            ),
        }
        current_app.logger.info("auth refresh token")
        return ret, 200
