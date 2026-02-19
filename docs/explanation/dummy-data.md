# How ehrQL generates dummy data
This page is an explanation of how ehrQL generates dummy data for your dataset definition
or measures definition.
For how to make use of ehrQL's dummy data generation, take a look at the
[dummy data tutorial](../tutorials/dummy-data/index.md) or our [how-to guides](../how-to/index.md).

This page assumes that you have already completed the dummy data tutorial.

## ehrQL starts by generating dummy tables
When you use the [`generate-dataset`](../reference/cli.md#generate-dataset) or
[`generate-measures`](../reference/cli.md#generate-dataset) commands
without providing your own dummy data or dummy tables, ehrQL uses your dataset definition or
measures definition (hereafter referred to as your "query") to generate dummy versions of
each table that is used in the query.

ehrQL then runs your query on the dummy tables to produce a dummy output,
(i.e. a dummy dataset or dummy measures).

As shown in the [Generating dummy tables from a dataset definition](../tutorials/dummy-data/provide-dummy-tables/index.md#generating-dummy-tables-from-a-dataset-definition)
section of the dummy data tutorial, you can use
[`create-dummy-tables`](../reference/cli.md/#create-dummy-tables)
to only output the dummy tables (without running your query against them).

## ehrQL first generates dummy patients, then generates events for each patient
From the dummy data tutorial, you will be familiar with configuring
dummy data with [`configure_dummy_data`](../reference/language.md#Dataset.configure_dummy_data).

!!! info "Configuring `additional_population_constraint`"
    If you configure `additional_population_constraint` with `configure_dummy_data`,
    the dummy data generator treats the additional constraint as:

    * Part of population definition in `dataset.define_population`, if you are generating a dataset
    * A prerequisite for patients to be included in the denominator, if you are generating measures

You will also have seen this log message:
```
[info   ] Attempting to generate 10 matching patients (random seed: BwRV3spP, timeout: 60s)
```
, where 10 is your configured `population_size` and
the timeout means that ehrQL will run the generation process for a maximum of 60 seconds.

Here's what happens behind the scenes:

To find 10 matching patients, ehrQL actually first generates a large batch of dummy patients
from which to select those who match your desired population.
Each of the generated dummy patients has a `date_of_birth`,
and some of them have a `date_of_death`.

For each table you use in the query, ehrQL generates a dummy table containing some
rows for each dummy patient. (The precise number of rows per patient varies;
it is also dependent on the query.)

For example, if your query uses the `clinical_events` table, ehrQL generates a dummy
`clinical_events` table that contains events for each of the dummy patients.
The date(s) of a generated event will always be after the dummy patient's `date_of_birth`,
and if applicable, before their `date_of_death`.

!!! info "Dummy tables only contain columns used in the query"
    When generating dummy tables, ehrQL takes into account which columns are used in your query.
    For example, if your query uses `clinical_events.date` and `clinical_events.snomedct_code`
    but not `clinical_events.numeric_value`, ehrQL knows to generate a dummy
    `clinical_events` table with only two columns, `date` and `snomedct_code`.

ehrQL also tries to use information from your query in the generation process to increase the
likelihood of the patient fitting your desired population characteristics.
For example, if you provide a list of codes in your query, ehrQL will use the provided codes
in the dummy event data instead of random alphanumeric strings.

ehrQL then runs your query against these generated dummy tables to produce the dataset or measures.
The patients that match your dataset's population definition (for datasets) or denominator (for measures)
are the "matching patients".

Since the configured `population_size` is 10, ehrQL outputs the first 10 rows of the dummy dataset.

## ehrQL generates dummy patients in batches until `population_size` is met (or timeout)
ehrQL generates dummy patients in batches.
If the initial batch of dummy patients does not produce enough matching patients,
ehrQL will generate a new batch of dummy patients and run the query against the new dummy table rows.

Batches are generated until enough matching patients have been generated,
or until 60 seconds have passed (i.e. timeout), at which point ehrQL stops and provides the output so far.

As you develop your dataset definition or measures definition to become more complex,
you may find that ehrQL does not find enough matching patients before the timeout is reached.
In such cases, you can consider increasing the timeout value with `configure_dummy_data`.

## ehrQL's native dummy data generation is random and simplified
You are encouraged to take a moment to revisit the points in the
[Limitations of native ehrQL dummy data](../tutorials/dummy-data/limitations-of-native-ehrQL-dummy-data/index.md)
section of the dummy data tutorial.
Some of the limitations discussed are tied to the design of ehrQL's native dummy data generator.

ehrQL generates dummy data randomly without being informed by real data distributions.
(How certain data is distributed in real electronic health records can be a research question on its own!)

For example, the frequency distribution of a given codelist event (e.g. statin prescriptions) in a
dummy dataset has no innate correlation to the dummy patients' age distribution,
as both result from a random generation process whose only criterion is that the generated dummy data
fits your dataset definition or measures definition.

The generator aims to generate enough dummy patients (and dummy events) that meet
most arbitrary dataset definitions or measures definitions,
such that the dummy datasets and dummy measures outputs can be used to develop analysis scripts.
This means that even though the generator is not informed by real EHR data,
it does try to simplify things by applying some very basic constraints based on real-life expectations.

For example, you just read that ehrQL ensures that a dummy patient's dummy events always occur after
their `date_of_birth`.
This limitation produces "clean" dummy data that is usually more useful for downstream analysis scripts
(compared to the scenario where you would frequently observe negative ages in your dummy dataset).
However, this also means that ehrQL's dummy data may not inform you about edge cases or data quality issues
in the real data, like real EHR records containing dates that precede the patient's birth.

The appendix section below lists the simplifications that ehrQL's dummy data generator makes when generating
values for certain tables. You should not expect the same "clean" data in the real data.

## Appendix: Simplifications made in ehrQL's natively generated dummy data

### General
- All dates are always on or between `1900-01-01` and today's date
- A patient's events always occur after their `date_of_birth` (and before their `date_of_death` if they have one)
- A patient is only registered with a single practice from birth

---8<-- 'includes/generated_docs/dummy_data_constraints.md'
