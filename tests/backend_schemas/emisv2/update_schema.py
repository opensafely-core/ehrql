# import os

# get env variables

# TODO: improve just file update-emis-v2-schema recipe

import os

# TODO: uv add the below to make ehrql dependecy : dev or prod?
import urllib3
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import text


urllib3.disable_warnings()


environment = "staging"  # The environmnent you wish to connect to (either "staging" or "production")
username = os.environ.get("EXA_USERNAME")  # Your EXA username for that environment
token = os.environ.get("EXA_TOKEN")


class TrinoSqlAlchemy:
    environments = {
        "staging": "explorerplus.stagingemisinsights.co.uk",  # Note: this is the URL for token access
        "production": "explorerplus.emishealthinsights.co.uk",
    }

    def __init__(self, token, username, environment="staging") -> None:
        self.user = username
        self.token = token
        self.host = self.environments[environment]
        self.port = 443
        self.catalog = "hive"
        self._session = None

    # def get_df(self, sql):
    #     data = list(self.get_iterator(sql))
    #     return pd.DataFrame(data)

    def get_iterator(self, sql: str):
        cursor = self.execute(sql)
        keys = cursor.keys()
        # print(keys)
        for row in cursor:
            yield {key: str(x) for key, x in zip(keys, row)}

    def execute(self, sql: str):
        return self.session.execute(text(sql))

    @property
    def session(self):
        if self._session is None:
            self._session = self.get_session()
        return self._session

    def get_session(self):
        conf = (
            f"trino://{self.user}:{self.token}@{self.host}:{self.port}/{self.catalog}"
        )
        args = {"http_scheme": "https", "verify": False, "request_timeout": 90}
        engine = create_engine(conf, connect_args=args)
        session_cls = sessionmaker(bind=engine)
        return session_cls()

    @property
    def engine(self):
        return self.session.get_bind()


# SQLAlchemy
trino = TrinoSqlAlchemy(username=username, token=token, environment=environment)

sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'explorer_open_safely'"
result = trino.get_iterator(sql)

for item in result:
    # breakpoint()
    # print(item)
    data = inspect(trino.engine).get_columns(
        table_name=item["table_name"], schema="explorer_open_safely"
    )
    print(item, data)
    # breakpoint()

### from the jupyter notebook
# class TrinoDBAPI:
#     environments = {
#         "staging": "explorerplus.stagingemisinsights.co.uk",  # Note: this is the URL for token access
#         "production": "explorerplus.emishealthinsights.co.uk",
#     }

#     def __init__(self, username: str, token: str, environment:str="staging") -> None:
#         self.user = username
#         self.token = token
#         self.host = self.environments[environment] # Eitherstaging or production
#         self.port = 443
#         self.catalog = "hive"
#         self._cursor = None

#     @property
#     def cursor(self):
#         if self._cursor is None:
#             self._cursor = self.get_cursor()
#         return self._cursor

#     def get_cursor(self):

#         conn = connect(
#             host=self.host,
#             port=self.port,
#             user=self.user,
#             catalog=self.catalog,
#             auth=BasicAuthentication(self.user, self.token),
#             http_scheme='https',
#             verify=False,
#         )
#         cursor = conn.cursor()
#         return cursor


#     def execute(self, sql: str):
#         self.cursor.execute(sql)
#         return self.cursor.fetchall()

#     # def get_df(self, sql: str) -> pd.DataFrame:
#     #     data = self.execute(sql)
#     #     cols = [x[0] for x in self.cursor.description]
#     #     df = pd.DataFrame(data, columns=cols)
#     #     return df


# # breakpoint()
# # Trino DBAPI
# trino = TrinoDBAPI(username=username, token=token, environment=environment)

# sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'explorer_open_safely'"
# data = trino.execute(sql)
# print(type(data))

# trino.get_df("show tables from hive.explorer_open_safely")

# sql = "select * from hive.explorer_open_safely.patient limit 1"
# print(trino.get_df(sql))
