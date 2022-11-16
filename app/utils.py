import pytz
import logging
from sqlalchemy import MetaData
from flask import current_app
from app import db

def timedelta_to_seconds(td):
    return td.seconds + td.days * 24 * 60 * 60


def get_time_zone(zone_name):
    tz_name_maps = {
        "PST": "US/Pacific",
        "EST": "US/Eastern"
    }
    try:
        return pytz.timezone(zone_name)
    except pytz.exceptions.UnknownTimeZoneError as err:
        logging.warning(f"get_time_zone error: {err} ; fallback to mapped and default UTC")
    mapped_tz_name = tz_name_maps.get(zone_name, "UTC")
    return pytz.timezone(mapped_tz_name)


def get_table(table_name):
    engine = db.get_engine(current_app)
    metadata = MetaData(engine, reflect=True)
    table = metadata.tables.get(table_name)
    return table