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
--8<-- 'includes/code/how-to/examples/patient_age-standalone-success/analysis/dataset_definition.py
```

Alternatively, using a native Python `date`:

```python
--8<-- 'includes/code/how-to/examples/patient_age2-standalone-success/analysis/dataset_definition.py
```

Or using an `index_date` variable:

```python
--8<-- 'includes/code/how-to/examples/patient_age3-standalone-success/analysis/dataset_definition.py
```

### Assigning each patient an age band

```python
--8<-- 'includes/code/how-to/examples/age_band-standalone-success/analysis/dataset_definition.py
```

### Finding each patient's date of birth

```python
--8<-- 'includes/code/how-to/examples/birth_date-standalone-success/analysis/dataset_definition.py
```

### Finding each patient's date of death in their primary care record

```python
--8<-- 'includes/code/how-to/examples/death_ehr-standalone-success/analysis/dataset_definition.py
```

:notepad_spiral: This value comes from the patient's EHR record.

There is generally a lag between the death being recorded in ONS data and appearing in the primary care record,
but the date itself is usually reliable when it appears. There may be multiple records of death for each patient
within this table, so you may wish to take the earliest or latest record available for each patient.
By contrast, cause of death is often not accurate in the primary care record so we don't make it available to query here.

### Finding each patient's date, place, and cause of death from ONS records

```python
--8<-- 'includes/code/how-to/examples/ons_records-standalone-success/analysis/dataset_definition.py
```

:notepad_spiral: There are currently [multiple](https://github.com/opensafely-core/ehrql/blob/d29ff8ab2cebf3522258c408f8225b7a76f7b6f2/ehrql/tables/beta/core.py#L78-L92) cause of death fields. We aim to resolve these to a single feature in the future.

### Finding each patient's sex

```python
--8<-- 'includes/code/how-to/examples/patient_sex-standalone-success/analysis/dataset_definition.py
```

The possible values are "female", "male", "intersex", and "unknown".

### Finding each patient's ethnicity

Ethnicity can be defined using a codelist. There are a lot of individual codes that can used to indicate a patients' fine-grained ethnicity. To make analysis more manageable, ethnicity is therefore commonly grouped into higher level categories. Above, we described how you can [import codelists that have a category column](#some-examples-using-codelist_from_csv). You can use a codelist with a category column to map clinical event codes for ethnicity to higher level categories as in this example:

```python
--8<-- 'includes/code/how-to/examples/patient_ethnicity-standalone-success/analysis/dataset_definition.py
```

## Finding attributes related to each patient's address as of a given date

### Finding each patient's IMD rank

```python
--8<-- 'includes/code/how-to/examples/imd_rank-standalone-success/analysis/dataset_definition.py
```

The original IMD ranking is rounded to the nearest 100.
The rounded IMD ranking ranges from 0 to 32,800.

See [this code comment](https://github.com/opensafely-core/ehrql/blob/d29ff8ab2cebf3522258c408f8225b7a76f7b6f2/ehrql/tables/beta/tpp.py#L117-L123) about how we choose one address if a patient has multiple registered addresses on the given date.

### Calculating each patient's IMD quintile

```python
--8<-- 'includes/code/how-to/examples/imd_quintile-standalone-success/analysis/dataset_definition.py
```

### Finding each patient's rural/urban classification

```python
--8<-- 'includes/code/how-to/examples/rural_urban-standalone-success/analysis/dataset_definition.py
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
--8<-- 'includes/code/how-to/examples/patient_msoa-standalone-success/analysis/dataset_definition.py
```

### Finding multiple attributes of each patient's address

```python
--8<-- 'includes/code/how-to/examples/address_attributes-standalone-success/analysis/dataset_definition.py
```

## Finding attributes related to each patient's GP practice as of a given date

### Finding each patient's practice's pseudonymised identifier

```python
--8<-- 'includes/code/how-to/examples/practice_id-standalone-success/analysis/dataset_definition.py
```

### Finding each patient's practice's STP

```python
--8<-- 'includes/code/how-to/examples/practice_stp-standalone-success/analysis/dataset_definition.py
```

### Finding each patient's practice's region

```python
--8<-- 'includes/code/how-to/examples/practice_region-standalone-success/analysis/dataset_definition.py
```

### Finding multiple attributes of each patient's practice

```python
--8<-- 'includes/code/how-to/examples/practice_attributes-standalone-success/analysis/dataset_definition.py
```

## Does each patient have an event matching some criteria?

### Does each patient have a clinical event matching a code in a codelist?

```python
--8<-- 'includes/code/how-to/examples/event_match-standalone-success/analysis/dataset_definition.py
```

### Does each patient have a clinical event matching a code in a codelist in a time period?

```python
--8<-- 'includes/code/how-to/examples/event_time-standalone-success/analysis/dataset_definition.py
```

### Does each patient have a medication event matching some criteria?

```python
--8<-- 'includes/code/how-to/examples/medication_match-standalone-success/analysis/dataset_definition.py
```

### Does each patient have a hospitalisation event matching some criteria?

```python
--8<-- 'includes/code/how-to/examples/hospitalisation_match-standalone-success/analysis/dataset_definition.py
```

## How many events does each patient have matching some criteria?

```python
--8<-- 'includes/code/how-to/examples/event_count-standalone-success/analysis/dataset_definition.py
```

## What is the first/last event matching some criteria?

The `first_for_patient()` and `last_for_patient()` methods can only be used on a sorted frame.
Frames can be sorted by calling the `sort_by()` method with the column to sort the frame by.

### What is the earliest/latest clinical event matching some criteria?

```python
--8<-- 'includes/code/how-to/examples/first_event-standalone-success/analysis/dataset_definition.py
```

```python
--8<-- 'includes/code/how-to/examples/last_event-standalone-success/analysis/dataset_definition.py
```

### What is the earliest/latest medication event matching some criteria?

```python
--8<-- 'includes/code/how-to/examples/first_medication-standalone-success/analysis/dataset_definition.py
```

```python
--8<-- 'includes/code/how-to/examples/last_medication-standalone-success/analysis/dataset_definition.py
```

### What is the earliest/latest hospitalisation event matching some criteria?

```python
--8<-- 'includes/code/how-to/examples/first_hospitalisation-standalone-success/analysis/dataset_definition.py
```

```python
--8<-- 'includes/code/how-to/examples/last_hospitalisation-standalone-success/analysis/dataset_definition.py
```

### What is the clinical event, matching some criteria, with the least/greatest value?

```python
--8<-- 'includes/code/how-to/examples/maximum_event-standalone-success/analysis/dataset_definition.py
```

## Getting properties of an event matching some criteria

### What is the code of the first/last clinical event matching some criteria?

```python
--8<-- 'includes/code/how-to/examples/first_code-standalone-success/analysis/dataset_definition.py
```

### What is the date of the first/last clinical event matching some criteria?

```python
--8<-- 'includes/code/how-to/examples/first_date-standalone-success/analysis/dataset_definition.py
```

### What is the code and date of the first/last clinical event matching some criteria?

```python
--8<-- 'includes/code/how-to/examples/first_attributes-standalone-success/analysis/dataset_definition.py
```

## Finding events occuring close in time to another event

### Finding the code of the first medication after the first clinical event matching some criteria

```python
--8<-- 'includes/code/how-to/examples/medication_after-standalone-success/analysis/dataset_definition.py
```

## Performing arithmetic on numeric values of clinical events

### Finding the mean observed value of clinical events matching some criteria

```python
--8<-- 'includes/code/how-to/examples/mean_value-standalone-success/analysis/dataset_definition.py
```

### Finding the observed value of clinical events matching some criteria expressed relative to another value

```python
--8<-- 'includes/code/how-to/examples/event_criteria-standalone-success/analysis/dataset_definition.py
```

## Finding events within a date range

### Finding events within a fixed date range

```python
--8<-- 'includes/code/how-to/examples/fixed_dates-standalone-success/analysis/dataset_definition.py
```

### Finding events within a date range plus a constant

```python
--8<-- 'includes/code/how-to/examples/date_constant-standalone-success/analysis/dataset_definition.py
```

### Finding events within a dynamic date range

```python
--8<-- 'includes/code/how-to/examples/dynamic_dates-standalone-success/analysis/dataset_definition.py
```

### Excluding events which have happened in the future

Data quality issues with many sources may result in events apparently happening in future dates (e.g. 9999-01-01), it is useful to filter these from your analysis.

```python
--8<-- 'includes/code/how-to/examples/exclude_future-standalone-success/analysis/dataset_definition.py
```

## Extracting parts of dates and date differences

### Finding the year an event occurred

```python
--8<-- 'includes/code/how-to/examples/event_year-standalone-success/analysis/dataset_definition.py
```

### Finding prescriptions made in particular months of the year

```python
--8<-- 'includes/code/how-to/examples/prescription_months-standalone-success/analysis/dataset_definition.py
```

### Finding the number of weeks between two events

```python
--8<-- 'includes/code/how-to/examples/weeks_between-standalone-success/analysis/dataset_definition.py
```
