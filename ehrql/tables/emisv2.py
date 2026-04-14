from ehrql.tables.core import clinical_events, medications, patients


# Exclude emisv2 tables from docs for now to avoid user confusion
exclude_from_docs = True

__all__ = [
    "clinical_events",
    "medications",
    "patients",
]
