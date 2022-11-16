import time
from flask import request, current_app
from flask_restplus import Resource, Namespace, marshal
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)
from sqlalchemy.sql import text
from ..decorators import jwt_required
from ..models.npi import npi_query_model
from ..authorizations import authorizations_access_token, authorizations, get_jwt_detail
from .mixins import GetPayloadMixIn
from app import npi_query
from app.context_utils import get_form_owner_info
import app.constants as C
from ..parser import get_request_argument, npi_request_parser
from app import db
from ..models.physician import physician_model
from app.word_segment import load, segment as segment_words


npi_ns = Namespace('npi', description="NPI Query", path="/",
                   decorators=[jwt_required],
                   authorizations=authorizations)


@npi_ns.route("/npi")
@npi_ns.doc(security=authorizations_access_token)
class NpiQuery(GetPayloadMixIn, Resource):

    @npi_ns.expect(npi_query_model, validate=True)
    def post(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        user_id = get_jwt_identity()
        print(f"user_id: {user_id} ; {type(user_id)}")
        payload = self.get_payload(npi_ns, npi_query_model)
        clinic_info = get_form_owner_info(user_id)
        request_data = {
            "state": clinic_info.get("state") or "",
            "country": clinic_info.get("country") or "",
            C.MODEL_FIELD_LIMIT: payload.get(C.MODEL_FIELD_LIMIT) or 20,
            C.MODEL_FIELD_SKIP: payload.get(C.MODEL_FIELD_SKIP) or 0,
            C.MODEL_FIELD_FORMATTED: payload.get(C.MODEL_FIELD_FORMATTED) or False,
            C.MODEL_FIELD_PROVIDER_CODE_EQUALITY: payload.get(C.MODEL_FIELD_PROVIDER_CODE_EQUALITY) or False
        }
        if payload.get(C.MODEL_FIELD_QUERY, "").strip().isdigit() or payload.get(C.MODEL_FIELD_PROVIDER_CODE_EQUALITY):
            request_data.update({"npi": payload.get(C.MODEL_FIELD_QUERY, "").strip()})
        else:
            request_data.update({"name": payload.get(C.MODEL_FIELD_QUERY, "").strip()})
        t1 = time.time()
        data = npi_query.api_npi_us(request_data)
        current_app.logger.info(f"npi_query time: {time.time() - t1}")
        return data

    @npi_ns.response(200, 'Success', physician_model)
    @npi_ns.doc(responses={ 200: 'Success', 400: 'Failed to fetch data'},
            parser = npi_request_parser,
            security=authorizations_access_token)
    def get(self):
        """
        :param args:
        :param kwargs:
        :return:
        """
        user_detail = get_jwt_detail()
        args = get_request_argument()
        t1 = time.time()

        search = args.get('search')
        if user_detail['user_claims']['country'] == "us":
            table_name = current_app.config["PHYSICIAN_TABLE_US"]
        else:
            table_name = current_app.config["PHYSICIAN_TABLE_CA"]

        if args.get("provider_code_equality") and search:
            sql = text(f"""SELECT * FROM `{table_name}`
                    WHERE `ProviderCode` = :search_text
                    LIMIT :limit_value OFFSET :offset_value ;""")
        elif search and not args.get("provider_code_equality"):
            sql = text(f"""SELECT *,
                    MATCH(ProviderCode, ProviderName, ProviderFirstName, ProviderLastName, ProviderPracticeAddress1) AGAINST(:search_text IN BOOLEAN MODE) AS score
                    FROM `{table_name}`
                    WHERE MATCH(ProviderCode, ProviderName, ProviderFirstName, ProviderLastName, ProviderPracticeAddress1) AGAINST(:search_text IN BOOLEAN MODE)
                    AND ProviderName IS NOT NULL
                    LIMIT :limit_value OFFSET :offset_value ;""")
        else:
            sql = text(f"""SELECT *
                    FROM `{table_name}`
                    LIMIT :limit_value OFFSET :offset_value ;""")
        try:
            if search is not None and len(search.strip()) > 7 and ' ' not in search.strip():
                search = ' '.join(segment_words(search))
            search = (search or '').strip()
            ctx = {
                "search_text": search if args.get("provider_code_equality") else ' '.join([(f'*{word}*' if len(word) > 2 else word) for word in search.split()]),
                "limit_value": int(args.get('limit')),
                "offset_value": int(args.get("offset"))
            }
            print(f"ctx: {ctx}")
            res = db.engine.execute(sql, ctx)
            physician = res.fetchall()
        except ValueError:
            return {"msg": f"limit and offset values should be integers"}, 400
        except Exception as err:
            current_app.logger.error(f"failed to fetch data: {err}")
            return {"msg": f"Failed to fetch data: {err}"}, 400

        current_app.logger.info("Physicians fetched successfully")
        data = marshal(physician, physician_model)
        current_app.logger.info(f"npi_query time: {time.time() - t1}")
        if args.get('formatted'):
            data = npi_query.data_formatter(data)
        return {
            'limit': args.get('limit'),
            'offset': args.get("offset"),
            'data': data
        }, 200