import time
import string
import logging
from flask import escape
from sqlalchemy.sql import text
from itertools import permutations, groupby
from dotenv import load_dotenv

load_dotenv()


class NpiQuery:

    _conn = None

    VALID_COUNTRY_LIST = ["US", "CA"]

    DEFAULT_COUNTRY = "US"
    DEFAULT_LIMIT = 10
    MAX_LIMIT = 100

    DB_TABLE_MAP = {
        "US": "npi",
        "CA": "unified_stored_physicians_ca"
    }

    def __init__(self, db_connection=None):
        if db_connection is not None:
            self.init(db_connection)

    def init(self, db_connection):
        self._conn = db_connection

    @property
    def conn(self):
        return self._conn.get_engine(bind="npi")

    def get_npi_statement(self, table_name, state=None, provider_code_equality=False):
        sql = f"""SELECT * FROM {table_name} WHERE """
        if state:
            sql += " `ProviderPracticeState` = :state AND "
        if provider_code_equality:
            sql += " `ProviderCode` = :npi ; "
        else:
            sql += " `ProviderName` IS NOT NULL AND "
            sql += " `ProviderCode` LIKE :npi ORDER BY `ProviderCode` LIMIT :limit OFFSET :skip;"
        logging.info(f"npi sql: {sql}")
        return text(sql)

    def get_name_groups(self, length):
        return [list(g)[0] for k, g in groupby(sorted((permutations(range(length), 2)), key=lambda x: sum(x)),
                                               lambda x: sum(x))]

    def get_name_statement_by_rank(self, table_name: str, names: list, state=None):
        """

        :param table_name:
        :param names:
        :param state:
        :return:
        """
        sql, name_like, name_case = f"SELECT * {{rank}} FROM `{table_name}` WHERE \n", "", ""
        names = names[:3]
        name_count = len(names)
        if name_count == 2:
            name_case = f' WHEN ({" AND ".join([f" `ProviderName` LIKE :name{i} " for i in range(name_count)])}) THEN 1 '
        elif name_count == 3:
            name_case = f' WHEN ({" AND ".join([f" `ProviderName` LIKE :name{i} " for i in range(name_count)])}) THEN 1 '
            for name_group in self.get_name_groups(name_count):
                name_case += f'\n WHEN ({" AND ".join([f" `ProviderName` LIKE :name{i} " for i in name_group])}) THEN 2 '
        if name_case:
            name_case = f" , ( CASE \n{name_case} \n ELSE 9 END ) AS `rank` "

        if state:
            sql += " `ProviderPracticeState` = :state AND "
        sql += " `ProviderName` IS NOT NULL AND "
        for idx, name in enumerate(names):
            name_like += " \n( " if name_like == "" else " OR "
            name_like += f" `ProviderName` LIKE :name{idx} "
            if (idx + 1) == len(names):
                name_like += " ) "
        sql = sql.format(rank=name_case)
        sql += name_like
        if name_case:
            sql = f"SELECT * FROM ( {sql} ) AS T ORDER BY `rank` LIMIT :limit OFFSET :skip;"
        else:
            sql += "ORDER BY `ProviderCode` LIMIT :limit OFFSET :skip ;"
        logging.info(f"sql: {sql}")
        return text(sql)

    def validate_npi(self, value):
        if value is None:
            return False
        for c in str(value):
            if c not in string.digits:
                return False
        return True

    def get_names(self, request_data):
        first_name = str(escape(str(request_data.get("first_name", "")).strip()))
        last_name = str(escape(str(request_data.get("last_name", "")).strip()))
        name = str(escape(str(request_data.get("name", "")).strip()))

        name = [part.strip() for part in name.split(" ") if part.strip()] if name else []
        try:
            limit = int(str(request_data.get("limit", self.DEFAULT_LIMIT)).strip())
        except ValueError:
            limit = self.DEFAULT_LIMIT
        try:
            skip = int(str(request_data.get("skip", 0)).strip())
        except ValueError:
            skip = 0
        if not (first_name or last_name or name):
            return None
        limit = self.MAX_LIMIT if limit > self.MAX_LIMIT else limit
        return {"first_name": first_name, "last_name": last_name, 'name': name, 'limit': limit, 'skip': skip}

    def get_limits(self, request_data):
        try:
            limit = int(str(request_data.get("limit", self.DEFAULT_LIMIT)).strip())
        except ValueError:
            limit = self.DEFAULT_LIMIT
        try:
            skip = int(str(request_data.get("skip", 0)).strip())
        except ValueError:
            skip = 0
        return dict(limit=limit, skip=skip)

    def get_state(self, request_data):
        return str(escape(str(request_data.get("state", "")).upper().strip()))

    def get_npi(self, request_data):
        npi = str(escape(str(request_data.get("npi", "")).strip()))
        if not npi or not self.validate_npi(npi):
            return None
        return {"npi": f"{npi}" if request_data.get("provider_code_equality") else f"%{npi}%"}

    def get_country(self, request_data):
        country = str(escape(str(request_data.get("country", self.DEFAULT_COUNTRY)).upper()))
        return {"country": country, "is_valid": country in self.VALID_COUNTRY_LIST}

    def get_db_table(self, country: str):
        return self.DB_TABLE_MAP.get(country.upper(), 'npi')

    def api_npi_us(self, request_data):
        """

        request_data = {
          "name": "First Last",
          "npi": "1234567",
          "country": "us",
          "state": "fl",
          "limit": 20,
          "skip": 0,
          "provider_code_equality": false
        }

        :param request_data:
        :return:
        """
        # request_data = request_json or request_args
        country = self.get_country(request_data)
        if country["is_valid"] is False:
            return {"is_success": False, "Error": f"Invalid country: {country['country']}"}

        db_table = self.get_db_table(country.get("country", self.DEFAULT_COUNTRY))
        logging.info(f"db table: {db_table}")
        limits = self.get_limits(request_data)
        npi = self.get_npi(request_data)
        names = self.get_names(request_data)
        state = self.get_state(request_data)
        if not (npi or names):
            return {"is_success": False, "country": country.get("country", ""),
                    "Error": "Please provide npi or first_name or last_name"}

        if npi:
            logging.info(f"processing for NPI/CPSO/CPSBC")
            npi_data_list = []

            # only NPI based query
            npi.update({'limit': limits.get('limit', self.DEFAULT_LIMIT), 'skip': limits.get('skip', 0)})
            if state:
                npi.update({"state": state})
            t1 = time.time()
            res = self.conn.execute(
                self.get_npi_statement(db_table, state=state,
                                       provider_code_equality=request_data.get("provider_code_equality")),
                npi
            )
            logging.info(f"NPI_TIME: {time.time() - t1}")
            for row in res:
                npi_data_list.append(dict(row.items()))
            if not npi_data_list:
                return {"is_success": False, "country": country.get("country", self.DEFAULT_COUNTRY),
                        "Error": f"No record found for NPI {npi}"}
            if request_data.get("provider_code_equality"):
                return {"is_success": True, "data": self._get_single_provider_data(npi_data_list)}
            if request_data.get("formatted"):
                npi_data_list = self.data_formatter(npi_data_list)
            return {"is_success": True, "data": npi_data_list, "counts": len(npi_data_list),
                    "country": country.get("country", self.DEFAULT_COUNTRY),
                    "limit": limits.get('limit', self.DEFAULT_LIMIT), "skip": limits.get('skip', 0)}

        # name based NPI Query
        logging.info("processing for names")
        data_list = []
        name_parts = names.get("name") or [v.strip() for k, v in names.items() if k in ['first_name', 'last_name']]
        query_params = {'limit': names.get('limit', self.DEFAULT_LIMIT), 'skip': names.get('skip', 0)}
        if state:
            query_params.update({"state": state})
        if names.get("name"):
            for idx, name_part in enumerate(name_parts[:3]):
                query_params[f"name{idx}"] = f"%{name_part.strip()}%" if name_part.strip() else ""
        t1 = time.time()
        res = self.conn.execute(
            self.get_name_statement_by_rank(db_table, names=name_parts, state=state),
            query_params
        )
        logging.info(f"NAME_TIME: {time.time() - t1}")
        for row in res:
            data_list.append(dict(row.items()))
        if request_data.get("formatted"):
            data_list = self.data_formatter(data_list)
        return {"is_success": True, "counts": len(data_list), "data": data_list,
                "country": country.get("country", self.DEFAULT_COUNTRY),
                "limit": names.get('limit', self.DEFAULT_LIMIT), "skip": names.get('skip', 0)}

    def data_formatter(self, data_list: list) -> list:
        """

        :param data_list:
        :return:
        """
        return list(map(self.formatting_func, data_list))

    def formatting_func(self, data: dict) -> dict:
        """

        :param data:
        :return:
        """
        practice_city = (data.get('ProviderPracticeCity', "") if data.get('ProviderPracticeCity') is not None
                         else self._address_to_city(data.get("ProviderPracticeAddress1")))
        if data.get('ProviderFirstName') and data.get('ProviderLastName'):
            name = f"{data.get('ProviderFirstName')}, {data.get('ProviderLastName')}"
        else:
            name = data.get('ProviderName', "")

        return {"label": f"{name} ({practice_city})", "value": data.get("ProviderCode", "")}

    def _starts_with_number(self, str_data: str) -> bool:
        """

        :param str_data:
        :return:
        """
        return len(str_data) > 0 and str_data[0].isdigit()

    def _address_to_city(self, addrs: str) -> str:
        """

        :param addrs:
        :return:
        """
        if addrs is None:
            return ""
        states = ["bc", "BC"]
        addrs_arr = addrs.split(" ")
        if not ("bc" in addrs_arr or "BC" in addrs_arr):
            return addrs
        city = []
        special_chars = ['-', '_', ',', ':', ';', '$', '@']
        road_words = ['Rd', 'rd', 'Street', 'street', 'St', 'Road', 'road', "Ave", "PO", "BOX", "Box", "Dr", "Dr."]
        for idx, value in enumerate(addrs_arr):
            if value.isdigit() or value in special_chars or self._starts_with_number(value):
                continue
            if value in states:
                break

            if value in road_words and not addrs_arr[idx + 1] in states:
                city = []
                continue
            city.append(value)

        if len(city) < 1:
            return addrs
        return " ".join(city)

    def _get_single_provider_data(self, data_list: list) -> dict:
        """

        :param data_list:
        :return:
        """
        try:
            data = data_list[0]
        except IndexError:
            data = {}
        physician_data = {
            "FIRST_NAME": data.get('ProviderFirstName'),
            "LAST_NAME": data.get('ProviderLastName'),
            "PHONE_1": data.get('ProviderPracticeTelephone', "").replace("-", ""),
            "FAX_1": data.get('ProviderPracticeFax'),
            "ADDRESS_1": data.get('ProviderPracticeAddress1'),
            "ADDRESS_2": data.get('ProviderPracticeAddress2'),
            "CPSO": data.get('ProviderCode'),
            "BILLING_NO": data.get('ProviderBillingNo'),
            "NPI": data.get('ProviderCode'),
            "EMAIL": ""
        }
        return physician_data
