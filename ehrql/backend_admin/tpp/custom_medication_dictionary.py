import csv
import logging
import pathlib

import sqlalchemy

from ehrql.__main__ import add_dsn_argument


log = logging.getLogger(__name__)


HELP = """
    Get or update the CustomMedicationDictionary table.
    """

CUSTOM_MEDICATION_DICTIONARY_CSV = pathlib.Path(__file__).with_name(
    "custom_medication_dictionary.csv"
)


def add_arguments(parser, environ):
    parser.add_argument(
        "action",
        choices=["get", "update"],
    )
    add_dsn_argument(parser, environ)


def run(*, backend_class, dsn, action, environ, user_args):
    backend = backend_class(environ)
    query_engine = backend.get_query_engine(dsn)

    temp_database_name = environ.get(
        "TEMP_DATABASE_NAME", "PLACEHOLDER_FOR_TEMP_DATABASE_NAME"
    )

    with query_engine.engine.connect() as tpp_connection:
        dictionary = CustomMedicationDictionary(tpp_connection, temp_database_name)

        match action:
            case "get":
                current_dictionary_contents = dictionary.get()
                # nb. This is not very nicely printed, but it should be plenty for
                # our purposes at the moment
                print(current_dictionary_contents)
            case "update":
                current_dictionary_contents = dictionary.update()
                print("OK")
            case _:  # pragma: no cover
                assert False


class CustomMedicationDictionary:
    def __init__(self, tpp_connection, temp_database_name):
        # The MSSQLQueryEngine query engine's connections use AUTOCOMMIT (see
        # `MSSQLQueryEngine.get_sqlalchemy_execution_options`).
        # We need to rollback if anything goes wrong in an `update`, so we
        # override the isolation level back to SQL Server's normal default for this
        # connection.
        self.tpp_connection = tpp_connection.execution_options(
            isolation_level="READ COMMITTED"
        )
        self.table_name = f"{temp_database_name}..CustomMedicationDictionary"

    def drop(self):
        self.tpp_connection.execute(
            sqlalchemy.text(f"""
            IF OBJECT_ID('{self.table_name}', 'U') IS NOT NULL
              DROP TABLE {self.table_name}
            """)
        )

    def create(self):
        self.tpp_connection.execute(
            sqlalchemy.text(f"""
            CREATE TABLE {self.table_name} (
                DMD_ID VARCHAR(50) COLLATE Latin1_General_CI_AS,
                MultilexDrug_ID VARCHAR(767),
            )
            """)
        )

    def update(self):
        """Create & populate CustomMedicationDictionary table"""
        try:
            self.drop()
            self.create()
            self.tpp_connection.execute(
                sqlalchemy.text(
                    f"INSERT INTO {self.table_name} VALUES (:dmdid, :multilexid)"
                ),
                self.load_csv(),
            )
            self.tpp_connection.commit()
        except sqlalchemy.exc.OperationalError:
            # If we attempt to insert invalid data, we want to reinstate
            # the table from before we dropped it!
            self.tpp_connection.rollback()
            raise

    def get(self):
        result = self.tpp_connection.execute(
            sqlalchemy.text(f"""
            SELECT DMD_ID, MultilexDrug_ID
            FROM {self.table_name}
            ORDER BY DMD_ID, MultilexDrug_ID
            """)
        )
        return list(result)

    @staticmethod
    def load_csv():
        with CUSTOM_MEDICATION_DICTIONARY_CSV.open(newline="") as f:
            reader = csv.reader(f)
            next(reader)  # skip header row
            return [{"dmdid": x[0], "multilexid": x[1]} for x in reader]
