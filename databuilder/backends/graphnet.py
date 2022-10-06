import os

import databuilder.tables.beta.graphnet
import databuilder.tables.beta.smoketest

from ..query_engines.spark import SparkQueryEngine
from .base import BaseBackend, MappedTable

SCHEMA = os.environ.get("GRAPHNET_DB_SCHEMA", default="TRE")


class GraphnetBackend(BaseBackend):
    """Backend for working with data in Graphnet."""

    query_engine_class = SparkQueryEngine
    patient_join_column = "Patient_ID"
    implements = [databuilder.tables.beta.smoketest]

    patients = MappedTable(
        schema=SCHEMA,
        source="Patients",
        columns=dict(
            date_of_birth="DateOfBirth",
        ),
    )
