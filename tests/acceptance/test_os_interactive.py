from databuilder import tables
from databuilder.codelistlib import codelist
from databuilder.query_language import Dataset


def test_dataset_defintion():
    index_date = "2020-01-01"
    end_date = "2020-01-31"
    selected_codelist = codelist(["22K..", "123", "456"], system="snomed")

    dataset = Dataset()

    registered_patients = tables.registrations \
        .take(tables.registrations.date_from <= index_date) \
        .drop(tables.registrations.date_to <= end_date)

    registered_with_one_practice = registered_patients.count_for_patient() == 1

    dataset.set_population(registered_with_one_practice)

    #TODO count multiple events entered on the same day as a single event
    dataset.events = tables.events.take(tables.events.code.is_in(selected_codelist)) \
        .take(tables.events.date >= index_date) \
        .take(tables.events.date <= end_date) \
        .count_for_patient() \
        .replace_null_with(0)

    dataset.stp = registered_patients.only_one_per_patient().stp
