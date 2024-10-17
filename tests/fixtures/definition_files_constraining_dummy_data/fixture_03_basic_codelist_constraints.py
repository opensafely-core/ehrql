# noqa: INP001
# Adapted from the ehrQL tutorial
# Constraints:
# - Clinical events table: ethnicity, date (from patient age)
# - Medications table: date (from patient DOB), DMD code
from pathlib import Path

from ehrql import (
    codelist_from_csv,
    create_dataset,
)
from ehrql.tables.core import medications, patients
from ehrql.tables.tpp import clinical_events


dataset = create_dataset()

dataset.configure_dummy_data(population_size=10)

# codelists
ethnicity_codelist_path = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "tutorial"
    / "example-study"
    / "codelists"
    / "opensafely-ethnicity.csv"
)
ethnicity_codelist = codelist_from_csv(
    ethnicity_codelist_path,
    column="Code",
    category_column="Grouping_6",
)

asthma_inhaler_codelist_path = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "tutorial"
    / "example-study"
    / "codelists"
    / "opensafely-asthma-inhaler-salbutamol-medication.csv"
)
asthma_inhaler_codelist = codelist_from_csv(
    str(asthma_inhaler_codelist_path),
    column="code",
)


dataset.define_population(patients.date_of_birth.is_on_or_before("1999-12-31"))

dataset.ethnicity = (
    clinical_events.where(clinical_events.ctv3_code.is_in(ethnicity_codelist))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .ctv3_code.to_category(ethnicity_codelist)
)

latest_asthma_med = (
    medications.where(medications.dmd_code.is_in(asthma_inhaler_codelist))
    .sort_by(medications.date)
    .last_for_patient()
)

dataset.asthma_med_date = latest_asthma_med.date
dataset.asthma_med_code = latest_asthma_med.dmd_code


if __name__ == "__main__":
    filepath = (
        Path(__file__).resolve().parents[3]
        / "docs"
        / "tutorial"
        / "example-study"
        / "codelists"
        / "opensafely-asthma-inhaler-salbutamol-medication.csv",
    )
    with open(filepath[0]) as f:
        print(f.read())
