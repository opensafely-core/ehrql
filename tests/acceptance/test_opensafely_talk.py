from databuilder import codelist, tables, variables
from databuilder.query_language import Dataset


def test_age_reuse():
    dataset = Dataset()
    dataset.age = variables.age(at="2022-01-01")


def test_age_raw():
    patients = tables.patients

    dataset = Dataset()
    dob = patients.date_of_birth
    dataset.age = ("2022-01-01" - dob).convert_to_years()


def test_has_died_reuse():
    dataset = Dataset()
    dataset.age = variables.has_died(at="2022-01-01")


def test_has_died_raw():
    index_date = "2022-01-01"
    deaths = tables.ons_deaths

    dataset = Dataset()
    dataset.has_died = deaths                     \
        .take(deaths.date_of_death <= index_date) \
        .exists_for_patient()


def test_bmi_reuse():
    dataset = Dataset()
    dataset.bmi = variables.bmi(
        index_date="2022-01-01", earliest_date="2012-01-01", min_age=16
    )


def test_bmi_raw():
    height_codelist = codelist(["XM01E", "229.."], "ctv3")
    weight_codelist = codelist(["X76C7", "22A.."], "ctv3")
    bmi_codelist = codelist(["22K.."], "ctv3")

    index_date = "2022-01-01"
    earliest_date = "2012-01-01"
    min_age = 16

    age = variables.age
    events = tables.events

    dataset = Dataset()

    height = events                               \
        .take(events.code.is_in(height_codelist)) \
        .take(events.date <= index_date)          \
        .take(age(at=events.date) >= min_age)     \
        .sort_by(events.date).last_for_patient()  \
        .value

    weight = events                               \
        .take(events.code.is_in(weight_codelist)) \
        .take(events.date <= index_date)          \
        .take(events.date >= earliest_date)       \
        .take(age(at=events.date) >= min_age)     \
        .sort_by(events.date).last_for_patient()  \
        .value

    bmi = events                                 \
        .take(events.code.is_in(bmi_codelist))   \
        .take(events.date <= index_date)         \
        .take(events.date >= earliest_date)      \
        .take(age(at=events.date) >= min_age)    \
        .sort_by(events.date).last_for_patient() \
        .value

    dataset.bmi = (weight / (height * height)).round(1).replace_null(bmi)
