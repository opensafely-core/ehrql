# Using the measures framework

## Introduction

The measures framework is used to calculate **quotients** (i.e. a numerator divided by a denominator) and to see how these **vary over time** and when broken down by different **groupings**.

The numerators, denominators and groups are all defined using ehrQL queries, just like we would use with a dataset definition. But the way those definitions are used is a bit different.

To explain the concepts involved we'll start with a basic but complete example and walk through each of the elements.


## Basic example

Suppose we want to know what proportion of the patients prescribed atorvastatin tablets in a given month were prescribed 80mg tablets, with the results broken down by sex and calculated for each of the first six months of 2022. Here's how we'd do that using the measures framework:

### Code

```ehrql
from ehrql import INTERVAL, case, create_measures, months, when
from ehrql.tables.core import medications, patients

# Every measure definitions file must include this line
measures = create_measures()

# Disable disclosure control for demonstration purposes.
# Values will neither be suppressed nor rounded.
measures.configure_disclosure_control(enabled=False)

# Small codelist for demonstration purposes; the real list would be longer
atorvastatin_tablets = [
    "39733211000001101",
    "39695411000001103",
    "39733011000001106",
    "39733111000001107",
]

atorvastatin_80mg_tablets = [
    "39733211000001101",
]

# The use of the special INTERVAL placeholder below is the key part of
# any measure definition as it allows the definition to be evaluated
# over a range of different intervals, rather than a fixed pair of dates
rx_in_interval = medications.where(
    medications.date.is_during(INTERVAL)
)
atorvastatin_rx = rx_in_interval.where(
    medications.dmd_code.is_in(atorvastatin_tablets)
)
atorvastatin_80_rx = rx_in_interval.where(
    medications.dmd_code.is_in(atorvastatin_80mg_tablets)
)

has_recorded_sex = patients.sex.is_in(["male", "female"])

measures.define_measure(
    name="atorva_80",
    numerator=atorvastatin_80_rx.exists_for_patient(),
    denominator=atorvastatin_rx.exists_for_patient() & has_recorded_sex,
    group_by={
        "sex": patients.sex
    },
    intervals=months(6).starting_on("2022-01-01"),
)
```

### Running the example

You can save this file as `measure_definition.py` and then run the [`generate-measures`](../reference/cli.md#generate-measures) command on it:
```
opensafely exec ehrql:v1 generate-measures measure_definition.py --output measures.csv
```

### Results

This should produce a file called `measures.csv` whose contents look something like this:

measure | interval_start | interval_end | ratio | numerator | denominator | sex
-- | -- | -- | -- | -- | -- | --
atorva_80 | 2022-01-01 | 2022-01-31 | 0 | 0 | 5 | female
atorva_80 | 2022-01-01 | 2022-01-31 | 0.2 | 2 | 10 | male
atorva_80 | 2022-02-01 | 2022-02-28 | 0 | 0 | 3 | female
atorva_80 | 2022-02-01 | 2022-02-28 | 0.2 | 1 | 5 | male
atorva_80 | 2022-03-01 | 2022-03-31 | 0.5 | 3 | 6 | female
atorva_80 | 2022-03-01 | 2022-03-31 | 0.2 | 2 | 10 | male
atorva_80 | 2022-04-01 | 2022-04-30 | 0.444 | 4 | 9 | male
atorva_80 | 2022-04-01 | 2022-04-30 | 0.125 | 1 | 8 | female
atorva_80 | 2022-05-01 | 2022-05-31 | 0.286 | 2 | 7 | male
atorva_80 | 2022-05-01 | 2022-05-31 | 0.2 | 1 | 5 | female
atorva_80 | 2022-06-01 | 2022-06-30 | 0.25 | 2 | 8 | male
atorva_80 | 2022-06-01 | 2022-06-30 | 0.5 | 5 | 10 | female


Here the **`measure`** column always has the same value (`atorva_80`) because we only have a single measure defined, but if we had defined multiple measures then this would tell us which measure each row relates to.

The **`interval_start`** and **`interval_end`** columns show the date range (inclusive) covered by each row. In this case there are 12 rows because each of the six months appears twice: once where `sex=male` and again where `sex=female`.

The **`denominator`** column gives the number of patients for each interval-sex combination which match our denominator definition. The **`numerator`** column gives the number of patients which _also_ match the numerator definition. That is, a patient must match both the denominator and numerator definitions to be included in the numerator.

The **`ratio`** is simply `numerator` divided by `denominator`.

The **`sex`** column gives the value of the expression we supplied when defining `group_by`. Had we defined any other groupings (say `age_band`) then they would appear as additional columns here.


## Core concepts

### Defining a measure

A measure definition always starts by creating a measures collection object:
```python
measures = create_measures()
```

Each individual measure is then defined by calling [`measures.define_measure()`](../reference/language.md#Measures.define_measure):
```python
measures.define_measure(
    name="atorva_80",
    numerator=atorvastatin_80_rx.exists_for_patient(),
    denominator=atorvastatin_rx.exists_for_patient() & has_recorded_sex,
    group_by={
        "sex": patients.sex
    },
    intervals=months(6).starting_on("2022-01-01"),
)
```

The **`name`** argument is just used so we can identify our measure in
the output. It can be anything you like so long as it contains only
alphanumeric and underscore characters and starts with a letter.

The **`denominator`** argument defines the condition that patients must
match to be included in the denominator i.e. it is a [boolean patient
series](../reference/language.md#BoolPatientSeries). (It is also possible
to supply an integer here, but we'll cover this later.)

The **`numerator`** arguments defines the _additional_ condition that
patients must also meet to be included in the numerator. (Again, this
can also be an integer as we'll discuss later.)

The **`group_by`** argument defines how we would like our results broken
down. It's optional – leaving it out means that we'll get a single row
for each time interval – but most measures define at least one set of
groups. It is supplied as a dictionary mapping group names to group
definitions.

As we saw in the example above, each group name defined here ends up as
column in the results. Each group definition should be a "categorical"
patient series, that is: a patient series which takes only a fixed set
of values.

The **`interval`** argument defines the time periods over which the
measure will be calculated. This is given as a list of start date/end
date pairs but, as typing these all out by hand would be laborious, we
provide several convenience functions for generating such lists:
[`years`](../reference/language.md#years.starting_on),
[`months`](../reference/language.md#months.starting_on) and
[`weeks`](../reference/language.md#weeks.starting_on).


### The `INTERVAL` placeholder

The key difference between the ehrQL we'd write for a dataset definition and the ehrQL we write for a measure comes in this line here:
```python
rx_in_interval = medications.where(
    medications.date.is_during(INTERVAL)
)
```

This filters the medications table to include just those prescribed during "the current interval" without specifying exactly what the interval is.

In a dataset definition we would need to reference a specific pair of dates here e.g.:
```python
rx_in_interval = medications.where(
    medications.date.is_on_or_between("2022-01-01", "2022-01-31")
)
```

But the query we use in our measure definition needs to be evaluated over a range of date intervals, not just one. We can handle this by using the special `INTERVAL` value as a placeholder for the start and end dates of the intervals:
```python
rx_in_interval = medications.where(
    medications.date.is_on_or_between(INTERVAL.start_date, INTERVAL.end_date)
)
```

However, it's a bit cumbersome to have to type `is_on_or_between()`, `start_date` and `end_date` every time so we provide `is_during()` as a convenient shorthand:
```python
rx_in_interval = medications.where(
    medications.date.is_during(INTERVAL)
)
```

### Disclosure control

By default, numerators and denominators are subject to disclosure control.
First, values less than or equal to seven are replaced with zero (suppressed);
then, values are rounded to the nearest five.

We disabled disclosure control with this line here:

```python
measures.configure_disclosure_control(enabled=False)
```

However, we should carefully consider whether we wish to disable disclosure control when
running inside of the secure environment. If we don't, then we should remove that line.

## Additional notes

### Multiple measures

We're not restricted to just one measure per file. If we wanted to add
another measure using the same numerator and denominator but this time
broken down by age band, then we would start by defining an age band variable
like this:
```python
age = patients.age_on(INTERVAL.start_date)
age_band = case(
    when((age >= 0) & (age < 20)).then("0-19"),
    when((age >= 20) & (age < 40)).then("20-39"),
    when((age >= 40) & (age < 60)).then("40-59"),
    when((age >= 60) & (age < 80)).then("60-79"),
    when(age >= 80).then("80+"),
)
```

And then we can define a new measure exactly like the previous one but
with different `name` and using `age_band` in our `group_by` argument:

```python
measures.define_measure(
    name="atorva_80_by_age",
    numerator=atorvastatin_80_rx.exists_for_patient(),
    denominator=atorvastatin_rx.exists_for_patient() & has_recorded_sex,
    group_by={
        "age_band": age_band
    },
    intervals=months(6).starting_on("2022-01-01"),
)
```


### Removing duplication

As our second measure shares so much in common with our first it seems
redundant to have to specify the numerator, denominator and intervals
all over again. Furthermore, if we ever wanted to make changes to these
definitions we'd need to make the change in multiple places to keep them
consistent.

To avoid this we can use
[`measures.define_defaults()`](../reference/language.md#Measures.define_defaults)
to set values which we know are going to be common between all the
measures in our file:
```python
measures.define_defaults(
    numerator=atorvastatin_80_rx.exists_for_patient(),
    denominator=atorvastatin_rx.exists_for_patient() & has_recorded_sex,
    intervals=months(6).starting_on("2022-01-01"),
)
```

And then we can define our two measures using:
```python
measures.define_measure(
    name="atorva_80",
    group_by={
        "sex": patients.sex
    },
)

measures.define_measure(
    name="atorva_80_by_age",
    group_by={
        "age_band": age_band
    },
)
```


### Grouping by multiple features

The above example defines two separate measures, one grouping by sex and
the other by age band. But it is also possible to define a single
measure that groups by sex _and_ age band simultaneously:
```python
measures.define_measure(
    name="atorva_80_by_age_and_sex",
    group_by={
        "sex": patients.sex,
        "age_band": age_band,
    },
)
```

This will produce a row of output for each possible combination of sex
and age band: `male,0-19` `female,0-19`, `male,20-39`, `female,20-39`
and so on for all ten combinations.

As we defined our measure to cover monthly intervals over a six month
period, this means that this single measure will produce 60 rows – ten
for each month.


### Dummy data

When run outside of the secure environment ehrQL will generate dummy
data for measures just as it does with datasets. However, note that
generating meaningful results for measures defined over a large time
period and with many different groupings can require significantly more
dummy data than would be needed for a dataset definition. The measures
framework will make a crude attempt to guess how many dummy patients it
should generate, but you may need to adjust this number using the
[`measures.configure_dummy_data()`](../reference/language.md#Measures.configure_dummy_data)
method.

For more information about using dummy data with measures please see our
[how-to guide](../how-to/dummy-measures-data.md).
