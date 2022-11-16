from flask_restplus import Resource, Namespace
from sqlalchemy.sql import text
from app import db
from flask import current_app
from app.v1.models.physician import physician_model
from app.v1.resources.mixins import GetPayloadMixIn

from app.v1.decorators import jwt_required
from app.v1.authorizations import authorizations_access_token, authorizations, get_jwt_detail


physician_ns = Namespace('physician', description="Physician", path="/physician",
                        decorators=[jwt_required],
                        authorizations=authorizations)


@physician_ns.route('/')
class Physician(GetPayloadMixIn, Resource):

    @physician_ns.doc(security=authorizations_access_token)
    @physician_ns.expect(physician_model, validate=True)
    def post(self):
        current_app.logger.info("post")
        payload = self.get_payload(physician_ns, physician_model)
        current_app.logger.info("payload")

        user_detail = get_jwt_detail()
        if user_detail['user_claims']['country'] == "us":
            physician_table = current_app.config["PHYSICIAN_TABLE_US"]
        elif user_detail['user_claims']['country'] == "ca":
            physician_table = current_app.config["PHYSICIAN_TABLE_CA"]
        else:
            current_app.logger.error(f"Failed to insert physician: Invalid country selected")
            return {"msg": f"Failed to insert physician: Please select country from [CA, US]"}, 401

        sql = text(f"""INSERT INTO {physician_table}
                    (`ProviderCode`, `ProviderBillingNo`, `ProviderLastName`,
                    `ProviderFirstName`, `ProviderName`, `ProviderPracticeAddress1`,
                    `ProviderPracticeAddress2`, `ProviderPracticeTelephone`,
                    `ProviderPracticeFax`, `ProviderPracticeCity`,
                    `ProviderPracticeState`, `ProviderPracticeCountry`)
                    VALUES (:code, :billing_no, :last_name, :first_name, :name, :practice_address1,
                    :practice_address2, :practice_telephone, :practice_fax, :practice_city,
                    :practice_state, :practice_country) ;""")
        try:
            db.get_engine(bind="npi").execute(sql, {"code": f"{payload['ProviderCode']}",
                        "billing_no": f"{payload['ProviderBillingNo']}",
                        "last_name": f"{payload['ProviderLastName']}",
                        "first_name": f"{payload['ProviderFirstName']}",
                        "name": f"{payload['ProviderName']}",
                        "practice_address1": f"{payload['ProviderPracticeAddress1']}",
                        "practice_address2": f"{payload['ProviderPracticeAddress2']}",
                        "practice_telephone": f"{payload['ProviderPracticeTelephone']}",
                        "practice_fax": f"{payload['ProviderPracticeFax']}",
                        "practice_city": f"{payload['ProviderPracticeCity']}",
                        "practice_state": f"{payload['ProviderPracticeState']}",
                        "practice_country": f"{payload['ProviderPracticeCountry']}"
                        })

        except Exception as err:
            current_app.logger.error(f"Failed to insert physician: {err}")
            return {"msg": f"Failed to insert physician: {err}"}, 401
        current_app.logger.info("Physician Added successfully")
        return {}, 200

    @physician_ns.doc(security=authorizations_access_token)
    @physician_ns.expect(physician_model, validate=True)
    def put(self, provider_code):
        current_app.logger.info("post")
        payload = self.get_payload(physician_ns, physician_model)
        current_app.logger.info("payload")

        user_detail = get_jwt_detail()
        if user_detail['user_claims']['country'] == "us":
            physician_table = current_app.config["PHYSICIAN_TABLE_US"]
        elif user_detail['user_claims']['country'] == "ca":
            physician_table = current_app.config["PHYSICIAN_TABLE_CA"]
        else:
            current_app.logger.error(f"Failed to update physician: Invalid country selected")
            return {"msg": f"Failed to update physician: Please select country from [CA, US]"}, 401

        sql = text(f"""UPDATE {physician_table} SET
                    ProviderBillingNo = :billing_no,
                    ProviderLastName = :last_name,
                    ProviderFirstName = :first_name,
                    ProviderName = :name,
                    ProviderPracticeAddress1 = :practice_address1,
                    ProviderPracticeAddress2 = :practice_address2,
                    ProviderPracticeTelephone = :practice_telephone,
                    ProviderPracticeFax = :practice_fax,
                    ProviderPracticeCity = :practice_city,
                    ProviderPracticeState = :practice_state,
                    ProviderPracticeCountry = :practice_country
                    WHERE `ProviderCode` = :provider_code
                    ;""")
        try:
            db.get_engine(bind="npi").execute(sql, {
                    "billing_no": f"{payload['ProviderBillingNo']}",
                    "last_name": f"{payload['ProviderLastName']}",
                    "first_name": f"{payload['ProviderFirstName']}",
                    "name": f"{payload['ProviderName']}",
                    "practice_address1": f"{payload['ProviderPracticeAddress1']}",
                    "practice_address2": f"{payload['ProviderPracticeAddress2']}",
                    "practice_telephone": f"{payload['ProviderPracticeTelephone']}",
                    "practice_fax": f"{payload['ProviderPracticeFax']}",
                    "practice_city": f"{payload['ProviderPracticeCity']}",
                    "practice_state": f"{payload['ProviderPracticeState']}",
                    "practice_country": f"{payload['ProviderPracticeCountry']}",
                    "provider_code" : f"{provider_code}"
            })

        except Exception as err:
            current_app.logger.error(f"Failed to insert physician: {err}")
            return {"msg": f"Failed to insert physician: {err}"}, 400
        current_app.logger.info("Physician Added successfully")
        return {}, 200



