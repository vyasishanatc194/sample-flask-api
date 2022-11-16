import datetime
import hashlib
from sqlalchemy import text
from flask import current_app

from app.models import db


def create_refresh_token_record(data: dict):
    """

    TODO: Have to add docs and proper exception handling

    :param data:
    :return:
    """
    refresh_token_record_table = current_app.config['REFRESH_TOKEN_RECORD_TABLE']  # "form_builder_refresh_token_record"
    insert_sql = text(f"""INSERT INTO {refresh_token_record_table} 
            ({', '.join(list(data.keys()))})
            VALUES (:{', :'.join(list(data.keys()))});
        """)
    result = db.get_engine(bind="auth").execute(insert_sql, data)
    return result.lastrowid


def update_refresh_token_record(token_hash, is_active=False):
    """

    TODO: Have to add docs and proper exception handling

    :param token_hash:
    :param is_active:
    :return:
    """
    refresh_token_record_table = current_app.config['REFRESH_TOKEN_RECORD_TABLE']  # "form_builder_refresh_token_record"
    update_sql = text(f"""UPDATE {refresh_token_record_table} 
                      SET is_active = :is_active, updated_at = :updated_at
                      WHERE token_hash = :token_hash  ;""")
    db.get_engine(bind="auth").execute(update_sql, {"is_active": is_active,
                                   "token_hash": token_hash,
                                   "updated_at": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")})

    return True


def is_refresh_token_valid(token_hash):
    """

    TODO: Have to add docs and proper exception handling

    :param token_hash:
    :return:
    """
    refresh_token_record_table = current_app.config['REFRESH_TOKEN_RECORD_TABLE']  # "form_builder_refresh_token_record"
    select_query = text(f"""SELECT id, reference_value, reference_source, reference_type, app_info, app_identifier 
                FROM {refresh_token_record_table} 
                WHERE token_hash = :token_hash AND is_active = 1 AND expire_at > :expire_at LIMIT 1;""")
    res = db.get_engine(bind="auth").execute(select_query, {"token_hash": token_hash,
                                           "expire_at": datetime.datetime.utcnow()})
    token = dict(res.fetchone() or {})
    print(f"token: {token}")
    return token


def create_hash(to_hash: str) -> str:
    """

    :param to_hash:
    :return:
    """
    salt = current_app.config["AUTH_KEY_SALT"]
    to_hash = f"{salt}{to_hash}{salt}"
    return hashlib.sha512(to_hash.encode()).hexdigest()
