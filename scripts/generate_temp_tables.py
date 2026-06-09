#!/usr/bin/env python
import logging
import os

import urllib3
from sqlalchemy import text

from ehrql.backends.emisv2 import EMISV2Backend


urllib3.disable_warnings()

# Logging


class EpochFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return f"{record.created:.6f}"


class SelectiveFilter(logging.Filter):
    KEEP = [
        "Finished running query 001 / 003",
        "Fetching results from query 002",
    ]

    def filter(self, record):
        if record.levelno >= logging.WARNING:
            return True
        return any(msg in record.getMessage() for msg in self.KEEP)


formatter = EpochFormatter("%(asctime)s - %(levelname)s - %(message)s")
formatter.formatException = lambda exc_info: ""

handler = logging.StreamHandler()
handler.addFilter(SelectiveFilter())
handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.handlers.clear()
root_logger.addHandler(handler)

# Config
EXA_USERNAME = os.getenv("EXA_USERNAME")
EXA_TOKEN = os.getenv("EXA_TOKEN")
dsn = f"trino://{EXA_USERNAME}:{EXA_TOKEN}@explorerplus.stagingemisinsights.co.uk:443/hive/explorer_open_safely"
emisv2_engine = EMISV2Backend().get_query_engine(dsn)

# Statements
create_stmt = f"""
CREATE TABLE "{EXA_USERNAME}".a_tmp_table AS
SELECT
patient_id,
has_died,
date_of_death IS NOT NULL as has_date_of_death
FROM
patient
"""
select_stmt = f"""
SELECT
has_died = has_date_of_death AS is_expected
FROM
"{EXA_USERNAME}".a_tmp_table
"""
drop_stmt = f'DROP TABLE IF EXISTS "{EXA_USERNAME}"."a_tmp_table"'


def drop_table():
    # We just want to drop the table so just use the ehrql emis engine here
    with emisv2_engine.engine.connect() as connection:
        connection.execute(text(drop_stmt))


def run_queries():
    queries = [
        (False, text(create_stmt)),
        (True, text(select_stmt)),
        (False, text(drop_stmt)),
    ]

    # The get_results_stream_from_queries handles logging
    for res in emisv2_engine.get_results_stream_from_queries(queries):
        pass


def main():
    drop_table()

    n = 0
    r = 0
    while True:
        try:
            run_queries()
        except Exception as e:
            if "TABLE_NOT_FOUND" in str(e):
                logging.error(e, exc_info=False)
                drop_table()
                n += 1
            else:
                raise
        r += 1
        if n >= 20 or r >= 100:
            logging.info(f"Done - {r} loops with {n} errors.")
            break


if __name__ == "__main__":
    main()
