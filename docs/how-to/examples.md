## How to use this page

You can either read this page from start to end
to get an idea of the kinds of queries you can make with ehrQL.

Or you can use the navigation bar at the top-right of this page,
to see a list of the examples,
and then jump to a specific example of interest.

### Examples in this page all use the TPP backend

### Some examples using `codelist_from_csv()`

:warning: Some examples refer to CSV codelists using the
`codelist_from_csv` function,
but are incomplete.
To actually use these code example,
you will need to correctly complete the function call.
The codelists are not provided as a part of these examples.

For example, instead of:

```python
asthma_codelist = codelist_from_csv(XXX)
```

you will need a line more like:

```python
asthma_codelist = codelist_from_csv("your-asthma-codelist.csv", column="code")
```

which provides the filename `your-asthma-codelist.csv`
and the name of the CSV column with codes.

#### Using codelists with category columns

Some codelists will have a category column that groups individual codes into categories. For example, [this codelist for ethnicity](https://www.opencodelists.org/codelist/opensafely/ethnicity-snomed-0removed/2e641f61/) has 2 category columns, which represent categories at both 6 and 16 levels. To make use of these categories, you can use `codelist_from_csv()` as follows:

```python
ethnicity_codelist = codelist_from_csv("ethnicity_codelist_with_categories", column="snomedcode", category_column="Grouping_6")
```

If you include an argument for `category_column`, the codelist returned will be a *dictionary* mapping individual codes to their respective categories. Without the `category_column` argument, the codelist returned will be a *list* of codes.

You can see an example of [how to access these categories within your dataset definition ](#finding-each-patients-ethnicity) below.

## Finding patient demographics

### Finding each patient's age

```python
from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

dataset = Dataset()
dataset.age = patients.age_on("2023-01-01")
```

Alternatively, using a native Python `date`:

```python
from datetime import date
from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

dataset = Dataset()
dataset.age = patients.age_on(date(2023, 1, 1))
```

Or using an `index_date` variable:

```python
from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

index_date = "2023-01-01"
dataset = Dataset()
dataset.age = patients.age_on(index_date)
```

### Assigning each patient an age band

```python
from ehrql import Dataset, case, when
from ehrql.tables.beta.tpp import patients

dataset = Dataset()
age = patients.age_on("2023-01-01")
dataset.age_band = case(
        when(age < 20).then("0-19"),
        when(age < 40).then("20-39"),
        when(age < 60).then("40-59"),
        when(age < 80).then("60-79"),
        when(age >= 80).then("80+"),
        default="missing",
)
```

### Finding each patient's date of birth

```python
from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

dataset = Dataset()
dataset.date_of_birth = patients.date_of_birth
```

### Finding each patient's date of death in their primary care record

```python
from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

dataset = Dataset()
dataset.date_of_death = patients.date_of_death
```

:notepad_spiral: This value comes from the patient's EHR record.

There is generally a lag between the death being recorded in ONS data and appearing in the primary care record,
but the date itself is usually reliable when it appears. There may be multiple records of death for each patient
within this table, so you may wish to take the earliest or latest record available for each patient.
By contrast, cause of death is often not accurate in the primary care record so we don't make it available to query here.

### Finding each patient's date, place, and cause of death from ONS records

```python
from ehrql import Dataset
from ehrql.tables.beta.tpp import ons_deaths

dataset = Dataset()
last_ons_death = ons_deaths.sort_by(ons_deaths.date).last_for_patient()
dataset.date_of_death = last_ons_death.date
dataset.place_of_death = last_ons_death.place
dataset.cause_of_death = last_ons_death.cause_of_death_01
```

:notepad_spiral: There are currently [multiple](https://github.com/opensafely-core/ehrql/blob/d29ff8ab2cebf3522258c408f8225b7a76f7b6f2/ehrql/tables/beta/core.py#L78-L92) cause of death fields. We aim to resolve these to a single feature in the future.

### Finding each patient's sex

```python
from ehrql import Dataset
from ehrql.tables.beta.tpp import patients

dataset = Dataset()
dataset.sex = patients.sex
```

The possible values are "female", "male", "intersex", and "unknown".

### Finding each patient's ethnicity

Ethnicity can be defined using a codelist. There are a lot of individual codes that can used to indicate a patients' fine-grained ethnicity. To make analysis more manageable, ethnicity is therefore commonly grouped into higher level categories. Above, we described how you can [import codelists that have a category column](#some-examples-using-codelist_from_csv). You can use a codelist with a category column to map clinical event codes for ethnicity to higher level categories as in this example:

```python
from ehrql import Dataset
from ehrql.tables.beta.core import clinical_events
from ehrql.codes import codelist_from_csv

dataset = Dataset()

ethnicity_codelist = codelist_from_csv(
    "ethnicity_codelist_with_categories",
    column="snomedcode",
    category_column="Grouping_6",
)

dataset.latest_ethnicity_code = (
    clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity_codelist))
    .where(clinical_events.date.is_on_or_before("2023-01-01"))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .snomedct_code
)
latest_ethnicity_group = latest_ethnicity_code.to_category(
    ethnicity_codelist
)
```

## Finding attributes related to each patient's address as of a given date

### Finding each patient's IMD rank

```python
from ehrql import Dataset
from ehrql.tables.beta.tpp import addresses

dataset = Dataset()
dataset.imd = addresses.for_patient_on("2023-01-01").imd_rounded
```

The original IMD ranking is rounded to the nearest 100.
The rounded IMD ranking ranges from 0 to 32,800.

See [this code comment](https://github.com/opensafely-core/ehrql/blob/d29ff8ab2cebf3522258c408f8225b7a76f7b6f2/ehrql/tables/beta/tpp.py#L117-L123) about how we choose one address if a patient has multiple registered addresses on the given date.

### Calculating each patient's IMD quintile

```python
from ehrql import Dataset, case, when
from ehrql.tables.beta.tpp import addresses

dataset = Dataset()
imd = addresses.for_patient_on("2023-01-01").imd_rounded
dataset.imd_quintile = case(
    when((imd >=0) & (imd < int(32844 * 1 / 5))).then("1 (most deprived)"),
    when(imd < int(32844 * 2 / 5)).then("2"),
    when(imd < int(32844 * 3 / 5)).then("3"),
    when(imd < int(32844 * 4 / 5)).then("4"),
    when(imd < int(32844 * 5 / 5)).then("5 (least deprived)"),
    default="unknown"
)
```

### Finding each patient's rural/urban classification

```python
from ehrql import Dataset
from ehrql.tables.beta.tpp import addresses

dataset = Dataset()
dataset.rural_urban = addresses.for_patient_on("2023-01-01").rural_urban_classification
```

The meaning of this value is as follows:

* 1 - Urban major conurbation
* 2 - Urban minor conurbation
* 3 - Urban city and town
* 4 - Urban city and town in a sparse setting
* 5 - Rural town and fringe
* 6 - Rural town and fringe in a sparse setting
* 7 - Rural village and dispersed
* 8 - Rural village and dispersed in a sparse setting

### Finding each patient's MSOA

```python
from ehrql import Dataset
from ehrql.tables.beta.tpp import addresses

dataset = Dataset()
dataset.msoa = addresses.for_patient_on("2023-01-01").msoa
```

### Finding multiple attributes of each patient's address

```python
from ehrql import Dataset
from ehrql.tables.beta.tpp import addresses

dataset = Dataset()
address = addresses.for_patient_on("2023-01-01")
dataset.imd = address.imd
dataset.rural_urban_classification = address.rural_urban_classification
dataset.msoa = address.msoa
```

## Finding attributes related to each patient's GP practice as of a given date

### Finding each patient's practice's pseudonymised identifier

```python
from ehrql import Dataset
from ehrql.tables.beta.tpp import practice_registrations

dataset = Dataset()
dataset.practice = practice_registrations.for_patient_on("2023-01-01").practice_pseudo_id
```

### Finding each patient's practice's STP

```python
from ehrql import Dataset
from ehrql.tables.beta.tpp import practice_registrations

dataset = Dataset()
dataset.stp = practice_registrations.for_patient_on("2023-01-01").practice_stp
```

### Finding each patient's practice's region

```python
from ehrql import Dataset
from ehrql.tables.beta.tpp import practice_registrations

dataset = Dataset()
dataset.region = practice_registrations.for_patient_on("2023-01-01").nuts1_region_name
```

### Finding multiple attributes of each patient's practice

```python
from ehrql import Dataset
from ehrql.tables.beta.tpp import practice_registrations

dataset = Dataset()
registration = practice_registrations.for_patient_on("2023-01-01")
dataset.practice = registration.practice_pseudo_id
dataset.stp = registration.practice_stp
dataset.region = registration.nuts1_region_name
```

## Does each patient have an event matching some criteria?

### Does each patient have a clinical event matching a code in a codelist?

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

asthma_codelist = codelist_from_csv(XXX)

dataset = Dataset()
dataset.has_had_asthma_diagnosis = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).exists_for_patient()
```

### Does each patient have a clinical event matching a code in a codelist in a time period?

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

asthma_codelist = codelist_from_csv(XXX)

dataset = Dataset()
dataset.has_recent_asthma_diagnosis = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).where(
        clinical_events.date.is_on_or_between("2022-07-01", "2023-01-01")
).exists_for_patient()
```

### Does each patient have a medication event matching some criteria?

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import medications

statin_medications = codelist_from_csv(XXX)

dataset = Dataset()
dataset.has_recent_statin_prescription = medications.where(
        medications.dmd_code.is_in(statin_medications)
).where(
        medications.is_on_or_between("2022-07-01", "2023-01-01")
).exists_for_patient()
```

### Does each patient have a hospitalisation event matching some criteria?

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import hospital_admissions

cardiac_diagnosis_codes = codelist_from_csv(XXX)

dataset = Dataset()
dataset.has_recent_cardiac_admission = hospital_admissions.where(
        hospital_admissions.primary_diagnoses .is_in(cardiac_diagnosis_codes)
).where(
        hospital_admissions.is_on_or_between("2022-07-01", "2023-01-01")
).exists_for_patient()
```

## How many events does each patient have matching some criteria?

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import medications

statin_medications = codelist_from_csv(XXX)

dataset = Dataset()
dataset.number_of_statin_prescriptions_in_last_year = medications.where(
        medications.dmd_code.is_in(statin_medications)
).where(
        medications.is_on_or_between("2022-01-01", "2023-01-01")
).count_for_patient()
```

## What is the first/last event matching some criteria?

The `first_for_patient()` and `last_for_patient()` methods can only be used on a sorted frame.
Frames can be sorted by calling the `sort_by()` method with the column to sort the frame by.

### What is the earliest/latest clinical event matching some criteria?

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

asthma_codelist = codelist_from_csv(XXX)

dataset = Dataset()
dataset.first_asthma_diagnosis_date = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).where(
        clinical_events.date.is_on_or_after("2022-07-01")
).sort_by(
        clinical_events.date
).first_for_patient().date
```

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

asthma_codelist = codelist_from_csv(XXX)

dataset = Dataset()
dataset.last_asthma_diagnosis_date = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).where(
        clinical_events.date.is_on_or_after("2022-07-01")
).sort_by(
        clinical_events.date
).last_for_patient().date
```

### What is the earliest/latest medication event matching some criteria?

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import medications

statin_medications = codelist_from_csv(XXX)

dataset = Dataset()
dataset.first_statin_prescription_date = medications.where(
        medications.dmd_code.is_in(statin_medications)
).where(
        medications.date.is_on_or_after("2022-07-01")
).sort_by(
        medications.date
).first_for_patient().date
```

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import medications

statin_medications = codelist_from_csv(XXX)

dataset = Dataset()
dataset.last_statin_prescription_date = medications.where(
        medications.dmd_code.is_in(statin_medications)
).where(
        medications.date.is_on_or_after("2022-07-01")
).sort_by(
        medications.date
).last_for_patient().date
```

### What is the earliest/latest hospitalisation event matching some criteria?

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import hospital_admissions

cardiac_diagnosis_codes = codelist_from_csv(XXX)

dataset = Dataset()
dataset.first_cardiac_hospitalisation_date = hospital_admissions.where(
        hospital_admissions.snomedct_code.is_in(cardiac_diagnosis_codes)
).where(
        hospital_admissions.date.is_on_or_after("2022-07-01")
).sort_by(
        hospital_admissions.date
).first_for_patient().date
```

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import medications

cardiac_diagnosis_codes = codelist_from_csv(XXX)

dataset = Dataset()
dataset.last_cardiac_hospitalisation_date = medications.where(
        medications.dmd_code.is_in(cardiac_diagnosis_codes)
).where(
        medications.date.is_on_or_after("2022-07-01")
).sort_by(
        medications.date
).last_for_patient().date
```

### What is the clinical event, matching some criteria, with the least/greatest value?

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

hba1c_codelist = codelist_from_csv(XXX)

dataset = Dataset()
max_hba1c = clinical_events.where(
        clinical_events.snomedct_code.is_in(hba1c_codelist)
).where(
        clinical_events.date.is_on_or_after("2022-07-01")
).numeric_value.maximum_for_patient()

dataset.date_of_max_hba1c_observed = clinical_events.where(clinical_events.snomedct_code.is_in(hba1c_codelist)
).where(
        clinical_events.numeric_value == max_hba1c
).sort_by(
        clinical_events.date
).last_for_patient().date
```

## Getting properties of an event matching some criteria

### What is the code of the first/last clinical event matching some criteria?

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

asthma_codelist = codelist_from_csv(XXX)

dataset = Dataset()
dataset.first_asthma_diagnosis_date = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).where(
        clinical_events.date.is_on_or_after("2022-07-01")
).sort_by(
        clinical_events.date
).first_for_patient().snomedct_code
```

### What is the date of the first/last clinical event matching some criteria?

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

asthma_codelist = codelist_from_csv(XXX)

dataset = Dataset()
dataset.first_asthma_diagnosis_date = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).where(
        clinical_events.date.is_on_or_after("2022-07-01")
).sort_by(
        clinical_events.date
).first_for_patient().date
```

### What is the code and date of the first/last clinical event matching some criteria?

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

asthma_codelist = codelist_from_csv(XXX)

dataset = Dataset()
first_asthma_diagnosis = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).where(
        clinical_events.date.is_on_or_after("2022-07-01")
).sort_by(
        clinical_events.date
).first_for_patient()
dataset.first_asthma_diagnosis_code = first_asthma_diagnosis.snomedct_code
dataset.first_asthma_diagnosis_date = first_asthma_diagnosis.date

```

## Finding events occuring close in time to another event

### Finding the code of the first medication after the first clinical event matching some criteria

```python
from ehrql import Dataset, codelist_from_csv, weeks
from ehrql.tables.beta.tpp import clinical_events, medications

asthma_codelist = codelist_from_csv(XXX)
inhaled_corticosteroid_codelist = codelist_from_csv(XXX)

dataset = Dataset()
first_asthma_diagnosis_date = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).where(
        clinical_events.date.is_on_or_after("2022-07-01")
).sort_by(
        clinical_events.date
).first_for_patient().date
dataset.first_asthma_diagnosis_date = first_asthma_diagnosis_date
dataset.count_ics_prescriptions_2wks_post_diagnosis = medications.where(
        medications.dmd_code.isin(inhaled_corticosteroid_codelist
).where(
        medications.date.is_on_or_between(first_asthma_diagnosis_date,first_asthma_diagnosis_date + weeks(2))
)

```

## Performing arithmetic on numeric values of clinical events

### Finding the mean observed value of clinical events matching some criteria

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

hba1c_codelist = codelist_from_csv(XXX)

dataset = Dataset()
dataset.mean_hba1c = clinical_events.where(
        clinical_events.snomedct_code.is_in(hba1c_codelist)
).where(
        clinical_events.date.is_on_or_after("2022-07-01")
).numeric_value.mean_for_patient()
```

### Finding the observed value of clinical events matching some criteria expressed relative to another value

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

hba1c_codelist = codelist_from_csv(XXX)

dataset = Dataset()
mean_hba1c = clinical_events.where(
        clinical_events.snomedct_code.is_in(hba1c_codelist)
).where(
        clinical_events.date.is_on_or_after("2022-07-01")
).numeric_value.maximum_for_patient()

dataset.mean_max_hbac_difference = max_hba1c - (
clinical_events.where(clinical_events.snomedct_code.is_in(hba1c_codelist)
).where(
        clinical_events.numeric_value == max_hba1c
).sort_by(
        clinical_events.date
).numeric_value.mean_for_patient())
```

## Finding events within a date range

### Finding events within a fixed date range

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

asthma_codelist = codelist_from_csv(XXX)

dataset = Dataset()
dataset.has_recent_asthma_diagnosis = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).where(
        clinical_events.date.is_on_or_between("2022-07-01", "2023-01-01")
).exists_for_patient()
```

### Finding events within a date range plus a constant

```python
from ehrql import Dataset, codelist_from_csv, weeks
from ehrql.tables.beta.tpp import clinical_events

asthma_codelist = codelist_from_csv(XXX)

index_date = "2022-07-01"

dataset = Dataset()
dataset.has_recent_asthma_diagnosis = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).where(
        clinical_events.date.is_on_or_between(index_date, index_date + weeks(2))
).exists_for_patient()
```

### Finding events within a dynamic date range

```python
from ehrql import Dataset, codelist_from_csv, months
from ehrql.tables.beta.tpp import clinical_events

diabetes_codelist = codelist_from_csv(XXX)
hba1c_codelist = codelist_from_csv(XXX)

dataset = Dataset()
first_diabetes_code_date = clinical_events.where(
        clinical_events.snomedct_code.is_in(diabetes_codelist)
).sort_by(
        clinical_events.date
).first_for_patient().date

dataset.count_of_hba1c_tests_6mo_post_first_diabetes_code = clinical_events.where(
        clinical_events.snomedct_code.is_in(hba1c_codelist)
).where(
        clinical_events.date.is_on_or_between(first_diabetes_code_date, first_diabetes_code_date + months(6))
).count_for_patient()
```

### Excluding events which have happened in the future

Data quality issues with many sources may result in events apparently happening in future dates (e.g. 9999-01-01), it is useful to filter these from your analysis.

```python
from datetime import date
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

asthma_codelist = codelist_from_csv(XXX)

dataset = Dataset()
dataset.has_recent_asthma_diagnosis = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).where(
        clinical_events.date > "2022-07-01"
).where(
        clinical_events.date < datetime.today()
).exists_for_patient()

```

## Extracting parts of dates and date differences

### Finding the year an event occurred

```python
from datetime import date
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

asthma_codelist = codelist_from_csv(XXX)

dataset = Dataset()
dataset.year_of_first = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).sort_by(
        clinical_events.date
).first_for_patient().date.year

```

### Finding prescriptions made in particular months of the year

```python
from ehrql import Dataset
from ehrql.tables.beta.tpp import medications

amoxicillin_codelist = codelist_from_csv(XXX)

winter_months = [10,11,12,1,2,3]

dataset = Dataset()
dataset.winter_amoxicillin_count = medications.where(
        medications.dmd_code.isin(amoxicillin_codelist)
).where(
        medications.date.month.isin(winter_months)
)
```

### Finding the number of weeks between two events

```python
from ehrql import Dataset, codelist_from_csv
from ehrql.tables.beta.tpp import clinical_events

asthma_codelist = codelist_from_csv(XXX)
asthma_review_codelist = codelist_from_csv(XXX)

dataset = Dataset()
first_asthma_diagnosis = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_codelist)
).sort_by(clinical_events.date).first_for_patient()

first_asthma_review = clinical_events.where(
        clinical_events.snomedct_code.is_in(asthma_review_codelist)
).where(
        clinical_events.date.is_on_or_after(first_asthma_diagnosis)
).sort_by(clinical_events.date).first_for_patient()

dataset.weeks_between_diagnosis_and_review = (first_asthma_review - first_asthma_diagnosis).weeks
```
