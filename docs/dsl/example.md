# DSL example

Audience: Datalab developers.

Status: rough/ready, somewhat aspirational, uses old cohort terminology.  I would like to explore whether this can be used as the basis for some of the DSL documentation.

---

Imagine we're studying covid vaccinations, and we're interested in patients who have been registered at the same practice for a full year.

We want to end up with a one-row-per-patient table which we can then use for our analysis (an "input.csv" table), like the following:

| patient | age | sex | first_date | first_code | second_date | second_code | codes_match |
| - | - | - | - | - | - | - | - |
| 1234 | 42 | f | 2021-03-19 | pf | 2021-07-04 | pf | yes |
| 2345 | 51 | m | - | - | - | - | - |
| 4567 | 61 | m | 2021-06-23 | az | - | - |
| 5678 | 29 | f | 2021-07-01 | pf | 2021-12-27 | az | no |

The data we need lives in three database tables:

**patients**

| patient | age | sex |
| - | - | - |
| 1234 | 42 | f |
| 2345 | 51 | m |
| 3456 | 83 | f |
| 4567 | 61 | m |
| 5678 | 29 | f |

**registrations**

| id | patient | practice | start_date | end_date |
| - | - | - | - | - |
| 78 | 1234 | A | 1989-03-12 | 2021-04-13 |
| 79 | 1234 | B | 2012-04-13 | - |
| 80 | 2345 | C | 1999-12-01 | - |
| 81 | 3456 | D | 2001-12-03 | 2017-09-09 |
| 82 | 4567 | E | 2019-06-01 | 2015-09-01 |
| 83 | 4567 | F | 2015-10-25 | - |
| 84 | 5678 | G | 2019-02-12 | - |


**immunisations**

| id | patient | code | date |
| - | - | - | - |
| 43 | 1234 | pf | 2021-03-19 |
| 44 | 4567 | pox | 2021-10-10 |
| 45 | 4567 | az | 2021-06-23 |
| 46 | 1234 | flu | 2021-10-15 |
| 47 | 1234 | pf | 2021-07-04 |
| 48 | 2345 | flu | 2021-03-25 |
| 49 | 2345 | flu | 2021-08-19 |
| 50 | 5678 | pox | 2021-10-11 |
| 51 | 4567 | flu | 2021-12-14 |
| 52 | 3456 | pf | 2021-09-09 |
| 53 | 2345 | flu | 2021-11-02 |
| 54 | 5678 | pf | 2021-07-01 |
| 55 | 3456 | pox | 2021-11-03 |
| 56 | 3456 | az | 2021-04-01 |
| 57 | 5678 | az | 2021-12-30 |
| 58 | 5678 | pf | 2021-07-02 |

**patients** is a `PatientFrame`, while **registrations** and **immunisations** are `EventFrame`s.

---

A `PatientFrame` represents a collection of rows with at most one row per patient.  An `EventFrame` represents as collection of rows with multiple rows per patient.

An `EventFrame`/`PatientFrame` can be filtered to produce another `EventFrame`/`PatientFrame`, and you should think of them as being like unevaluated Django Querysets, in that they can be combined and acted on to produce something that can be turned into SQL.

Ultimately, we transform an `EventFrame`/`PatientFrame` into a `PatientSeries`, through filtering, sorting, aggregating, and selecting a column.

A `PatientSeries` represents a collection of values with one value per patient.

A `PatientSeries` can be assigned to a cohort, in which case a column with the `PatientSeries`'s values will be appended to the cohort's input.csv.

---

This diagram attempts to explain how a `EventFrame`/`PatientFrame` is transformed into a
`PatientSeries`.

The nodes are Python classes and the arrows are methods on those classes.

```
             +---+
             |   V
      filter |  PatientFrame
             |   |   |
             +---+   | select_column
                     V
                PatientSeries


             +---+
             |   V
      filter |  EventFrame -----------------------+
             |   |   |                            |
             +---+   | sort_by                    |
                     V                            |
             SortedEventFrame                     |
                     |                            |
        +---+        | (first/last)_for_patient   | (count/exists)_for_patient
        |   V        V                            |
 filter |  AggregatedEventFrame                   |
        |   |        |                            |
        +---+        | select_column              |
                     V                            |
               PatientSeries <--------------------+
```

---

Here's the code that we can use to generate an input.csv table.

```
from cohortextractor2.concepts.tables import (
    immunisations as imms,
    patients,
    registrations,
)
from cohortextractor2.dsl import Cohort, categorise

from codelists import covid_vacc_codes

# Create a cohort.
cohort = Cohort()

# Create two PatientSeries for age and sex and assign to the cohort.
cohort.age = patients.select_column(patients.age)
cohort.sex = patients.select_column(patients.sex)

# Create a new EventFrame representing just the events with covid vaccination codes.
covid_imms = imms.filter(covid_vacc_codes.contains(imms.code))

# Create an AggregatedEventFrame representing just, for each patient, the first record
# in covid_imms.
first = covid_imms.sort_by(imms.date).first_for_patient()

# Create two PatientSeries for the first date / code and assign to the cohort.
cohort.first_date = first.select_column(imms.date)
cohort.first_code = first.select_column(imms.code)

# Create an AggregatedEventFrame representing, for each patient, just the record that
# occurs first 28 days after the first record of a covid vaccination.
second = (
    covid_imms.filter(imms.date > (cohort.first_date + 28))
    .sort_by(imms.date)
    .first_for_patient()
)

# Create two PatientSeries for the second date / code and assign to the cohort.
cohort.second_date = second.select_column("date")
cohort.second_code = second.select_column("code")

# Create a PatientSeries based on the values in two other PatientSeries.
cohort.codes_match = categorise(
    {
        "yes": cohort.first_code == cohort.second_code,
        "no": True,
    }
)

# Include only patients who have been at same practice for duration of study.
cohort.set_population(
    registrations.filter(registrations.start_date <= "2021-01-01")
    .filter(registrations.end_date >= "2021-06-30")
    .exists_for_patient()
)
```

---

What follows is a series of demonstrations of how each `PatientSeries` is constructed.

Note that the intermediate tables are not necessarily created.  They are intended to illustrate how you can think of the DSL working.

The only bit that might require further explanation is `imms.date > (cohort.first_date + 28)`.

---

```
cohort.age = patients.select_column(patients.age)  # PatientSeries
```

| patient | cohort.age |
| - | - |
| 1234 | 42 |
| 2345 | 51 |
| 3456 | 83 |
| 4567 | 61 |
| 5678 | 29 |

```
cohort.sex = patients.select_column(patients.sex)  # PatientSeries
```

| patient | cohort.sex |
| - | - |
| 1234 | f |
| 2345 | m |
| 3456 | f |
| 4567 | m |
| 5678 | f |

```
covid_imms = imms.filter(covid_vacc_codes.contains(imms.code))  # EventFrame
```

| id | patient | code | date |
| - | - | - | - |
| 43 | 1234 | pf | 2021-03-19 |
| 45 | 4567 | az | 2021-06-23 |
| 47 | 1234 | pf | 2021-07-04 |
| 52 | 3456 | pf | 2021-09-09 |
| 54 | 5678 | pf | 2021-07-01 |
| 56 | 3456 | az | 2021-04-01 |
| 57 | 5678 | az | 2021-12-30 |
| 58 | 5678 | pf | 2021-07-02 |

```
covid_imms.sort_by(imms.date)  # SortedEventFrame
```

| id | patient | code | date |
| - | - | - | - |
| 43 | 1234 | pf | 2021-03-19 |
| 56 | 3456 | az | 2021-04-01 |
| 45 | 4567 | az | 2021-06-23 |
| 54 | 5678 | pf | 2021-07-01 |
| 47 | 1234 | pf | 2021-07-04 |
| 52 | 3456 | pf | 2021-09-09 |
| 57 | 5678 | az | 2021-12-30 |
| 58 | 5678 | pf | 2021-07-02 |

```
first_covid_imm = covid_imms.sort_by(imms.date).first_for_patient()  # AggregatedEventFrame
```

| id | patient | code | date |
| - | - | - | - |
| 43 | 1234 | pf | 2021-03-19 |
| 56 | 3456 | az | 2021-04-01 |
| 45 | 4567 | az | 2021-06-23 |
| 54 | 5678 | pf | 2021-07-01 |

```
cohort.first_code = first_covid_imm.select_column(imms.code)  # PatientSeries
```

| patient | cohort.first_code |
| - | - |
| 1234 | pf |
| 3456 | az |
| 4567 | az |
| 5678 | pf |

```
cohort.first_date = first_covid_imm.select_column(imms.date)  # PatientSeries
```

| patient | cohort.first_date |
| - | - |
| 1234 | 2021-03-19 |
| 3456 | 2021-04-01 |
| 4567 | 2021-06-23 |
| 5678 | 2021-07-01 |

```
cohort.first_date + 28  # PatientSeries
```

| patient | cohort.first_date + 28|
| - | - |
| 1234 | 2021-04-16 |
| 3456 | 2021-04-29 |
| 4567 | 2021-07-21 |
| 5678 | 2021-07-29 |

```
imms.date > (cohort.first_date + 28)  # PatientSeries
```

| id | date > cohort.first_date + 28 |
| - | - |
| 43 | F |
| 44 | T |
| 45 | F |
| 46 | T |
| 47 | T |
| 48 | - |
| 49 | - |
| 50 | T |
| 51 | T |
| 52 | T |
| 53 | - |
| 54 | F |
| 55 | T |
| 56 | F |
| 57 | T |
| 58 | F |

To see where this came from, consider this table, and note that the values of the `cohort.first_date + 28` column come from the values corresponding to each row's patient.

| id | patient | code | date | cohort.first_date + 28 | date > cohort.first_date + 28 |
| - | - | - | - | - | - |
| 43 | 1234 | pf | 2021-03-19 | 2021-04-16 | F |
| 44 | 4567 | pox | 2021-10-10 | 2021-07-21 | T |
| 45 | 4567 | az | 2021-06-23 | 2021-07-21 | F |
| 46 | 1234 | flu | 2021-10-15 | 2021-04-16 | T |
| 47 | 1234 | pf | 2021-07-04 | 2021-04-16 | T |
| 48 | 2345 | flu | 2021-03-25 | - | - |
| 49 | 2345 | flu | 2021-08-19 | - | - |
| 50 | 5678 | pox | 2021-10-11 | 2021-07-29 | T |
| 51 | 4567 | flu | 2021-12-14 | 2021-07-21 | T |
| 52 | 3456 | pf | 2021-09-09 | 2021-04-29 | T |
| 53 | 2345 | flu | 2021-11-02 | - | - |
| 54 | 5678 | pf | 2021-07-01 | 2021-07-29 | F |
| 55 | 3456 | pox | 2021-11-03 | 2021-04-29 | T |
| 56 | 3456 | az | 2021-04-01 | 2021-04-29 | F |
| 57 | 5678 | az | 2021-12-30 | 2021-07-29 | T |
| 58 | 5678 | pf | 2021-07-02 | 2021-07-29 | F |

```
covid_imms.filter(imms.date > (cohort.first_date + 28))  # EventFrame
```

| id | patient | code | date |
| - | - | - | - |
| 45 | 4567 | az | 2021-06-23 |
| 47 | 1234 | pf | 2021-07-04 |
| 52 | 3456 | pf | 2021-09-09 |
| 57 | 5678 | az | 2021-12-30 |

```
second_covid_imm = (
    covid_imms.filter(imms.date > (cohort.first_date + 28))
    .sort_by(imms.date)
    .first_for_patient()
)  # AggregatedEventFrame
```

| id | patient | code | date |
| - | - | - | - |
| 47 | 1234 | pf | 2021-07-04 |
| 52 | 3456 | pf | 2021-09-09 |
| 57 | 5678 | az | 2021-12-30 |

```
cohort.second_date = second_covid_imm.select_column("date")  # PatientSeries
```

| patient | cohort.second_date |
| - | - |
| 1234 | 2021-07-04 |
| 3456 | 2021-09-09 |
| 5678 | 2021-12-30 |

```
cohort.second_date = second_covid_imm.select_column("code")  # PatientSeries
```

| patient | cohort.second_code |
| - | - |
| 1234 | pf |
| 3456 | pf |
| 5678 | az |

```
cohort.codes_match = categorise(
    {
        "yes": cohort.first_code == cohort.second_code,
        "no": True,
    }
)  # PatientSeries
```

| patient | cohort.codes_match |
| - | - |
| 1234 | yes |
| 3456 | no |
| 4567 | - |
| 5678 | no |

Putting it all together:

| patient | age | sex | first_code | first_date | second_code | second_date | codes_match |
| - | - | - | - | - | - | - | - |
| 1234 | 42 | f | pf | 2021-03-19 | pf | 2021-07-04 | yes |
| 2345 | 51 | m | - | - | - | - | - |
| 3456 | 83 | f | az | 2021-04-01 | pf | 2021-09-09 | no |
| 4567 | 61 | m | az | 2021-06-23 | - | - | - |
| 5678 | 29 | f | pf | 2021-07-01 | az | 2021-07-02 | no |


```
registrations \
  .filter(registrations.start_date <= "2021-01-01") \
  .filter(registrations.end_date >= "2021-06-30") \
  .exists_for_patient()
```

| patient | exists_for_patient |
| - | - |
| 1234 | T |
| 2345 | T |
| 4567 | T |
| 5678 | T |

To understand where this came from, consider:

```
registrations \
  .filter(registrations.start_date <= "2021-01-01") \
  .filter(registrations.end_date >= "2021-06-30")
```

| id | patient | practice | start_date | end_date |
| - | - | - | - | - |
| 79 | 1234 | B | 2012-04-13 | - |
| 80 | 2345 | C | 1999-12-01 | - |
| 83 | 4567 | F | 2015-10-25 | - |
| 84 | 5678 | G | 2019-02-12 | - |

Setting the population acts a bit like a Pandas mask, filtering the input.csv table to
only contain rows present in the population `PatientSeries`.

| patient | age | sex | first_code | first_date | second_code | second_date | codes_match | exists_for_patient |
| - | - | - | - | - | - | - | - | - |
| 1234 | 42 | f | pf | 2021-03-19 | pf | 2021-07-04 | yes | T |
| 2345 | 51 | m | - | - | - | - | - | T |
| ~~3456 ~~| ~~83 ~~| ~~f ~~| ~~az ~~| ~~2021-04-01 ~~| ~~pf ~~| ~~2021-09-09 ~~| ~~no ~~| ~~F ~~|
| 4567 | 61 | m | az | 2021-06-23 | - | - | - | T |
| 5678 | 29 | f | pf | 2021-07-01 | az | 2021-07-02 | no | T |

Why doesn't ~~strikethrough~~ work in tables?
