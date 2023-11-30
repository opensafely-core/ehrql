"""
This schema defines the data (both primary care and externally linked) available in the
OpenSAFELY-EMIS backend. For more information about this backend, see
"[EMIS Primary Care](https://docs.opensafely.org/data-sources/emis/)".
"""
from ehrql.tables.beta.core import clinical_events, patients


__all__ = [
    "clinical_events",
    "patients",
]
