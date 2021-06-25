import importlib
import sys
import time
from pathlib import Path

import pymssql
from pymssql import OperationalError


def get_class_vars(cls):
    default_vars = set(dir(type("ArbitraryEmptyClass", (), {})))
    return [(key, value) for key, value in vars(cls).items() if key not in default_vars]


if __name__ == "__main__":
    sys.path.append("/workspace")
    study_definition = importlib.import_module("study_definition")
    Cohort = getattr(study_definition, "Cohort")

    cohort = {key: value for key, value in get_class_vars(Cohort)}

    query = cohort["everything"]
    sql = f"SELECT patient_id, {query.column} FROM {query.table}"
    print(sql, file=sys.stderr)

    timeout = 20
    limit = time.time() + timeout
    conn = None
    while not conn:
        try:
            conn = pymssql.connect(
                server="mssql", user="SA", password="Your_password123!", database="test"
            )
        except OperationalError as e:
            if time.time() >= limit:
                raise Exception(
                    f"Failed to connect to mssql after {timeout} seconds"
                ) from e
            time.sleep(1)

    cursor = conn.cursor()
    cursor.execute(sql)

    path = Path("/workspace/outputs/some_file.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open(mode="w") as f:
        f.write("patient_id,everything\n")

        for patient_id, code in cursor:
            f.write(f"{patient_id},{code}\n")

    conn.close()
