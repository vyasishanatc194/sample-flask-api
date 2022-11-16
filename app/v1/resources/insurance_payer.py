from flask_restplus import Resource, Namespace, marshal
from sqlalchemy.sql import text
from app import db
from flask import current_app, request
from ..models.insurance_payer import insurance_payer_info_model
from .mixins import GetPayloadMixIn

from ..decorators import jwt_required
from ..authorizations import authorizations_access_token, authorizations
from ..parser import get_request_argument, insurance_request_parser
from app.word_segment import load, segment as segment_words


insurance_ns = Namespace('insurance', description="Insurance Payer Info", path="/insurance",
                         decorators=[jwt_required],
                         authorizations=authorizations)
load()


@insurance_ns.route('/<string:id>')
class UpdateInsuranceInfo(GetPayloadMixIn, Resource):
    @insurance_ns.doc(responses={ 200: 'Success', 401: 'Failed to update insurance information'},
            security=authorizations_access_token)
    @insurance_ns.expect(insurance_payer_info_model, validate=True)
    def put(self, id):
        current_app.logger.info("post")
        payload = self.get_payload(insurance_ns, insurance_payer_info_model)
        current_app.logger.info("payload")

        insurance_table = current_app.config["INSURANCE_TABLE"]

        sql = text(f"""UPDATE  {insurance_table} SET
                    insurance_code = :insurance_code,
                    plan = :plan,
                    plan_type = :plan_type
                    WHERE `id` = :id
                    ;""")
        try:
            db.engine.execute(sql, {
                "insurance_code": f"{payload['insurance_code']}",
                "plan": f"{payload['plan']}",
                "plan_type": f"{payload['plan_type']}",
                "id":id
            })
        except Exception as err:
            current_app.logger.error(f"Failed to update insurance information: {err}")
            return {"msg": f"Failed to update insurance information: {err}"}, 401
        current_app.logger.info("Insurance information updated successfully")
        return {}, 200


@insurance_ns.route('/')
class InsuranceInfo(Resource):
    """
    :param args:
    :param kwargs:
    :return:
    """
    @insurance_ns.doc(responses={200: 'Success', 401: 'Failed to fetch Insurance Information',
                                 400: 'Search field is required'},
                      parser=insurance_request_parser,
                      security=authorizations_access_token)
    def get(self):
        print(F"request.args: {request.args}")
        args = get_request_argument()

        search = args.get('search')
        limit = args.get('limit') if search is not None else 100
        if search is not None and len(search.strip()) > 7 and ' ' not in search.strip():
            print(f"search1: {search}")
            search = ' '.join(segment_words(search))
            print(f"search2: {search}")
        table_name = current_app.config["INSURANCE_TABLE"]
        if search is None:
            sql = f"""SELECT `id`, `insurance_code`, `plan`, `plan_type` 
                      FROM `{table_name}` ORDER BY `id` LIMIT :limit_value  OFFSET :offset_value ;"""
        else:
            sql = f"""SELECT `id`, `insurance_code`, `plan`, `plan_type`,
                        MATCH(plan) AGAINST(:search_text IN BOOLEAN MODE) AS score
                        FROM `{table_name}`
                        WHERE MATCH(plan) AGAINST(:search_text IN BOOLEAN MODE) 
                        LIMIT :limit_value  OFFSET :offset_value;"""
        try:
            search = (search or '').strip()
            print(' '.join([(f'*{word}*' if len(word) > 2 else word) for word in search.split()]))
            res = db.engine.execute(text(sql), {
                "search_text": ' '.join([(f'*{word}*' if len(word) > 2 else word) for word in search.split()]),
                "limit_value": int(limit),
                "offset_value": int(args.get("offset"))
            })
            insurance = res.fetchall()
        except ValueError:
            return {"msg": f"limit and offset values should be integers"}, 400
        except Exception as err:
            current_app.logger.error(f"failed to fetch insurance: {err}")
            return {"msg": f"Failed to fetch insurance: {err}"}, 401
        current_app.logger.info("Insurance Information fetched successfully")
        print(f"insurance: {insurance}\nsearch: {search}")
        data = marshal(insurance, insurance_payer_info_model)
        return {
            'limit': limit,
            'offset': args.get("offset"),
            'data': data
        }, 200
