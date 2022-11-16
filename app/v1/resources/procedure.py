import copy
from flask_restplus import Resource, Namespace, marshal
from sqlalchemy.sql import text
from app import db
from flask import current_app, request
from ..models.procedure import procedure_model

from ..decorators import jwt_required
from ..authorizations import authorizations_access_token, authorizations
from ..parser import get_request_argument ,procedure_request_parser
from app.word_segment import load, segment as segment_words


procedure_ns = Namespace('Procedure', description="Procedure", path="/procedure",
                        decorators=[jwt_required],
                        authorizations=authorizations)


@procedure_ns.route('')
class ProcedureSearch(Resource):
    """
    :param args:
    :param kwargs:
    :return:
    """
    @procedure_ns.doc(responses={ 200: 'Success', 401: 'Failed to fetch Procedure', 400: 'Search field is required'},
			parser=procedure_request_parser,
            security=authorizations_access_token)
    def get(self):
        args = get_request_argument()

        if not args.get('search'):
            return {"msg": "Search field is required"}, 400
        search = args.get('search')
        if search is not None and len(search.strip()) > 7 and ' ' not in search.strip():
            search = ' '.join(segment_words(search))

        table_name = current_app.config["CPT_INFO_AKUMIN"]

        sql = f""" SELECT `CPT_CODE`, `DESCRIPTION`,
                    MATCH(CPT_CODE, DESCRIPTION) AGAINST(:search_text IN BOOLEAN MODE) AS SCORE
                    FROM `{table_name}`
                    WHERE MATCH(CPT_CODE, DESCRIPTION) AGAINST(:search_text IN BOOLEAN MODE)
                    LIMIT :limit_value OFFSET :offset_value; """

        try:
            search = (search or '').strip()
            ctx = {
                "search_text": ' '.join([(f'*{word}*' if len(word) > 2 else word) for word in search.split()]),
                "limit_value": int(args.get('limit')),
                "offset_value": int(args.get("offset"))
            }
            print(f"ctx: {ctx}")
            res = db.engine.execute(text(sql), ctx)
            pharmacy = res.fetchall()
        except ValueError:
            return {"msg": f"limit and offset values should be integers"}, 400
        except Exception as err:
            current_app.logger.error(f"failed to fetch procedure: {err}")
            return {"msg": f"Failed to fetch prodedure: {err}"}, 400

        current_app.logger.info("Procedures fetched successfully")
        data = marshal(pharmacy, procedure_model)
        if args.get('formatted'):
            data_list = []
            for d in data:
                fd = copy.deepcopy(d)
                fd.update({'label': f"{fd['CPT_CODE']} - {fd['DESCRIPTION']}",
                           "value": f"{fd['CPT_CODE']} - {fd['DESCRIPTION']}"})
                data_list.append(fd)
        else:
            data_list = data
        return {
            'limit': args.get('limit'),
            'offset': args.get("offset"),
            'data': data_list
        }, 200
