from pathlib import Path

from databuilder import categorise, codelist, table
from databuilder.validate_dummy_data import validate_dummy_data

from .codelists import (
    any_long_covid_code,
    any_primary_care_code,
    covid_codes,
    ethnicity_codes,
    post_viral_fatigue_codes,
)

pandemic_start = "2020-02-01"
index_date = "2020-11-01"
bmi_code = codelist(["22K.."], system="ctv3")


class Cohort:

    # Population
    # Patients registered on 2020-11-01
    _registrations = table("practice_registrations").date_in_range(index_date)
    _current_registrations = _registrations.latest("date_end")
    population = _registrations.exists()
    practice_id = _current_registrations.get("pseudo_id")

    # COVID infection
    sgss_positive = (
        table("covid_test_results").filter(positive_result=True).earliest().get("date")
    )

    primary_care_covid = (
        table("clinical_events")
        .filter("code", is_in=any_primary_care_code)
        .earliest()
        .get("date")
    )

    hospital_covid = (
        table("hospitalizations")
        .filter("code", is_in=covid_codes)
        .earliest()
        .get("date")
    )

    # Outcome
    _long_covid_table = table("clinical_events").filter(
        "code", is_in=any_long_covid_code
    )
    long_covid = _long_covid_table.exists()
    first_long_covid_date = _long_covid_table.earliest().get("date")
    first_long_covid_code = _long_covid_table.earliest().get("code")

    _post_viral_fatigue_table = table("clinical_events").filter(
        "code", is_in=post_viral_fatigue_codes
    )
    post_viral_fatigue = _post_viral_fatigue_table.exists()
    first_post_viral_fatigue_date = _post_viral_fatigue_table.earliest().get("date")

    # Demographics
    # Age
    _age = table("patients").age_as_of(index_date)
    _age_categories = {
        "0-17": _age < 18,
        "18-24": (_age >= 18) & (_age < 25),
        "25-34": (_age >= 25) & (_age < 35),
        "35-44": (_age >= 35) & (_age < 45),
        "45-54": (_age >= 45) & (_age < 55),
        "55-69": (_age >= 55) & (_age < 70),
        "70-79": (_age >= 70) & (_age < 80),
        "80+": _age >= 80,
    }
    age_group = categorise(_age_categories, default="missing")

    # Sex
    sex = table("patients").first_by("patient_id").get("sex")

    # Region
    region = _current_registrations.get("nuts1_region_name")

    # IMD
    _imd_value = table("patient_address").imd_rounded_as_of(index_date)
    _imd_groups = {
        "1": (_imd_value >= 1) & (_imd_value < (32844 * 1 / 5)),
        "2": (_imd_value >= 32844 * 1 / 5) & (_imd_value < (32844 * 2 / 5)),
        "3": (_imd_value >= 32844 * 2 / 5) & (_imd_value < (32844 * 3 / 5)),
        "4": (_imd_value >= 32844 * 3 / 5) & (_imd_value < (32844 * 4 / 5)),
        "5": (_imd_value >= 32844 * 4 / 5) & (_imd_value < 32844),
    }
    imd = categorise(_imd_groups, default="0")

    # Ethnicity
    ethnicity = (
        table("clinical_events")
        .filter("code", is_in=ethnicity_codes)
        .filter("date", on_or_before=index_date)
        .latest()
        .get("code")
    )

    # Clinical variables
    # Latest recorded BMI
    _bmi_value = (
        table("clinical_events")
        .filter("code", is_in=bmi_code)
        .latest()
        .get("numeric_value")
    )
    _bmi_groups = {
        "Obese I (30-34.9)": (_bmi_value >= 30) & (_bmi_value < 35),
        "Obese II (35-39.9)": (_bmi_value >= 35) & (_bmi_value < 40),
        "Obese III (40+)": (_bmi_value >= 40) & (_bmi_value < 100)
        # set maximum to avoid any impossibly extreme values being classified as obese
    }
    bmi = categorise(_bmi_groups, default="Not obese")
    # Previous COVID
    _previous_covid_categories = {
        "COVID positive": (sgss_positive | primary_care_covid) & ~hospital_covid,
        "COVID hospitalised": hospital_covid,
    }
    previous_covid = categorise(_previous_covid_categories, default="No COVID code")


# Add the long covid and post viral code count variables
for target_codelist in [any_long_covid_code, post_viral_fatigue_codes]:
    for code in target_codelist.codes:
        filtered_to_code = (
            table("clinical_events")
            .filter("code", is_in=codelist([code], target_codelist.system))
            .filter("date", on_or_after=pandemic_start)
        )
        count_variable_def = filtered_to_code.count("code")
        date_variable_def = filtered_to_code.earliest().get("date")
        setattr(Cohort, f"{target_codelist.system}_{code}", count_variable_def)
        setattr(Cohort, f"{target_codelist.system}_{code}_date", date_variable_def)


def test_validate_dummy_data():
    dummy_data_file = (
        Path(__file__).parent.parent
        / "fixtures"
        / "dummy_data"
        / "long_covid_dummy_data.csv"
    )
    validate_dummy_data(Cohort, dummy_data_file, Path("output.csv"))
