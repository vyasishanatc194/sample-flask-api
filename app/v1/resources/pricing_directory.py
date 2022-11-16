from flask_restplus import Resource, Namespace, marshal, reqparse
from sqlalchemy.sql import text
from app import db
from flask import current_app, request
from ..models.pricing_directory import pricing_directory_model

from ..decorators import jwt_required
from ..authorizations import authorizations_access_token, authorizations
from ..parser import get_request_argument, pricing_request_parser


pricing_ns = Namespace('PricingDirectory', description="Pricing Directory", path="/pricing",
                        # decorators=[jwt_required],
                        # authorizations=authorizations
                        )


@pricing_ns.route('')
class PricingSearch(Resource):
    """
    :param args:
    :param kwargs:
    :return:
    """
    @pricing_ns.doc(responses={ 200: 'Success', 401: 'Failed to fetch Pricing', 400: 'Search field is required'},
			parser=pricing_request_parser,
            security=authorizations_access_token
            )
    def get(self):
        args = get_request_argument()
        procedure_code = args.get('procedure_code','')
        profile_name = args.get('profile_name', '')
        if not procedure_code:
             return {"msg": "procedure code field is required"}, 400
        table_name = current_app.config["US_PROCEDURE_PRICING_DIRECTORY"]
        if procedure_code and profile_name:
            sql = f"""SELECT * FROM `{table_name}`
                        WHERE `procedure_code` LIKE :procedure_code AND
                        `profile_name` LIKE :profile_name
                        LIMIT :limit_value  OFFSET :offset_value ;"""
        elif procedure_code and not profile_name:
            sql = f"""SELECT * FROM `{table_name}`
                        WHERE `procedure_code` LIKE :procedure_code
                        LIMIT :limit_value  OFFSET :offset_value ;"""
        try:
            res = db.engine.execute(text(sql), {
                "procedure_code" : int(args.get('procedure_code')),
                "profile_name": f"%{args.get('profile_name')}%",
                "limit_value" : int(args.get('limit')),
                "offset_value" : int(args.get("offset"))
            })
            pricing_directory = res.fetchall()
        except ValueError:
            return {"msg": f"limit and offset values should be integers"}, 400
        except Exception as err:
            current_app.logger.error(f"failed to fetch procedure pricing: {err}")
            return {"msg": f"Failed to fetch prodedure pricing: {err}"}, 400

        current_app.logger.info("Procedure Pricing fetched successfully")
        data = marshal(pricing_directory, pricing_directory_model)
        return {
            'limit': args.get('limit'),
            'offset': args.get("offset"),
            'data': data
        }, 200
