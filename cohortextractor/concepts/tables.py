from cohortextractor.query_interface import QueryBuilder


class ClinicalEvents(QueryBuilder):
    code = "code"
    date = "date"

    def __init__(self):
        super().__init__("clinical_events")


clinical_events = ClinicalEvents()
