from flask_restplus import Resource, Namespace, marshal
from sqlalchemy.sql import text
from app import db
from flask import current_app, request
from ..models.pharmacy import ca_pharmacy_list_model
from .mixins import GetPayloadMixIn

from ..decorators import jwt_required
from ..authorizations import authorizations_access_token, authorizations
from ..parser import get_request_argument , pharmacy_request_parser

pharmacy_ns = Namespace('pharmacy', description="Pharmacy", path="/pharmacy",
                        decorators=[jwt_required],
                        authorizations=authorizations)


@pharmacy_ns.route('/')
class PharmacySearch(Resource):
    """
    :param args:
    :param kwargs:
    :return:
    """
    @pharmacy_ns.doc(responses={ 200: 'Success', 401: 'Failed to fetch Pharmacies', 400: 'Search field is required'},
			parser=pharmacy_request_parser,
            security=authorizations_access_token)
    def get(self):
        args = get_request_argument()

        if not args.get('search'):
            return {"msg": "Search field is required"}, 400

        table_name = current_app.config["PHARMACY_LIST_TABLE_NAME"]
        sql = text(f"""SELECT `pharmacy`, `address`, `phone` FROM {table_name}
                    WHERE `pharmacy` LIKE :search_text LIMIT :limit_value  OFFSET :offset_value ;""")
        try:
            res = db.engine.execute(sql, {
                "search_text" : f"%{args.get('search')}%",
                "limit_value" : int(args.get('limit')),
                "offset_value" : int(args.get("offset"))
            })
            pharmacy = res.fetchall()
        except ValueError:
            return {"msg": f"limit and offset values should be integers"}, 400
        except Exception as err:
            current_app.logger.error(f"failed to fetch pharmacies: {err}")
            return {"msg": f"Failed to fetch Pharmacies: {err}"}, 400

        current_app.logger.info("Pharmacies fetched successfully")
        data = marshal(pharmacy, ca_pharmacy_list_model)
        return {
            'limit': args.get('limit'),
            'offset': args.get("offset"),
            'data': data
        }, 200


@pharmacy_ns.route('/create/')
class Pharmacy(GetPayloadMixIn, Resource):

    @pharmacy_ns.doc(responses={ 200: 'Success', 401: 'Failed to insert pharmacy'},
            security=authorizations_access_token)
    @pharmacy_ns.expect(ca_pharmacy_list_model, validate=True)
    def post(self):
        current_app.logger.info("post")
        payload = self.get_payload(pharmacy_ns, ca_pharmacy_list_model)
        current_app.logger.info("payload")
        table_name = current_app.config["PHARMACY_LIST_TABLE_NAME"]
        sql = text(f"""INSERT INTO {table_name} (`pharmacy`, `address`, `phone`)
                    VALUES (:pharmacy, :address, :phone) ;""")
        try:
            res = db.engine.execute(sql, {"pharmacy": f"{payload['pharmacy']}",
                                                "address": f"{payload['address']}",
                                                "phone": f"{payload['phone']}"})
        except Exception as err:
            current_app.logger.error(f"Failed to insert pharmacy: {err}")
            return {"msg": f"Failed to insert pharmacy: {err}"}, 401
        current_app.logger.info("Pharmacy Added successfully")
        return {}, 200
