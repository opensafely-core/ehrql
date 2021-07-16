import os

import cohortextractor.main


def get_mode(name, values, default):
    key = f"{name}_MODE"
    mode = os.environ.get(key, default)
    if mode not in values:
        raise ValueError(
            f"Unknown {key} {mode}. Possible values are {','.join(values)}."
        )
    return mode


def extract(cohort, backend, database):
    return list(cohortextractor.main.extract(cohort, backend(database.host_url())))
