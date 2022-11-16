from sqlalchemy import text
from flask import current_app

from app import db


def get_form_owner_info(clinic_user_id: int) -> dict:
    """

    :param clinic_user_id:
    :return:
    """
    query = text(f"""SELECT 
        `id` AS clinic_id, `clinic_short_name`, `region`, `state`, `country`, `emr_pathway`, 
        `oscar_base_url`, `oscar_consumer_key`, `oscar_client_secret`, `oscar_callback_url`, 
        `oscar_verifier`, `oscar_token`, `oscar_token_secret`, `oscar_token_expired`,
        `accuro_uuid`, `clinic_key`, `telnyx_number`, `twilio_number`,
        (CASE
            WHEN `emr_pathway` = 'INFINITT' THEN 1
            ELSE 0
        END) AS is_multi_location 
        FROM {current_app.config["CLINIC_TABLE_NAME"]} 
        WHERE `id` = :clinic_user_id""")

    clinic_info = {}
    try:
        res = db.get_engine(bind='auth').execute(query, {"clinic_user_id": clinic_user_id})
        for row in res:
            clinic_info = dict(row)
            break
    except Exception as err:
        current_app.logger.error(f"get_form_owner_info query error: {err}")
    return clinic_info
