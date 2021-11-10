from cohortextractor.query_interface import QueryBuilder


class ClinicalEvents(QueryBuilder):
    code = "code"
    date = "date"

    def __init__(table_name):
        super().__init__("clinical_events")


clinical_events = ClinicalEvents()
