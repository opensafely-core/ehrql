This page explains several important concepts that you should understand
in order to write a dataset definition.

## An example dataset definition

Here is a very short dataset definition:

```python
from ehrql import Dataset
from ehrql.tables.beta.core import patients, medications

dataset = Dataset()

dataset.define_population(patients.date_of_birth.is_on_or_before("1999-12-31"))

asthma_codes = ["39113311000001107", "39113611000001102"]
latest_asthma_med = (
    medications.where(medications.dmd_code.is_in(asthma_codes))
    .sort_by(medications.date)
    .last_for_patient()
)

dataset.med_date = latest_asthma_med.date
dataset.med_code = latest_asthma_med.dmd_code
```

When this dataset definition is executed,
it generates a table of data containing rows only for patients born before the year 2000.
The table contains two columns:
`med_date` and `med_code`.

We will explain how the dataset definition works below.
Before that, we need to explain four important related types of object.

## Explaining the example dataset definition

We're now in a position to explain our example dataset definition.

To begin with, we import the Python objects that we'll need.

```python
from ehrql import Dataset
from ehrql.tables.beta.core import patients, medications
```

Next, we create a dataset object. Don't worry about exactly what this line does (but see the [ehrQL reference here](../reference/language.md#Dataset) if you're interested).

```python
dataset = Dataset()
```

Now, we define the population of our dataset. `define_population` is used to limit the population from which data is extracted.

```python
dataset.define_population(patients.date_of_birth.is_on_or_before("1999-12-31"))
```

This can be broken down.

```pycon
>>> patients.date_of_birth
0 | 1973-07-01
1 | 1948-03-01
2 | 2003-04-01
3 | 2007-06-01
4 | 1938-10-01
5 | 1994-04-01
6 | 1953-05-01
7 | 1992-08-01
8 | 1931-10-01
9 | 1979-04-01
>>> patients.date_of_birth.is_on_or_before("1999-12-31")
0 | True
1 | True
2 | False
3 | False
4 | True
5 | True
6 | True
7 | True
8 | True
9 | True
```

`dataset.define_population(s)` tells ehrQL that our dataset's population is only
the patients whose value in the series `s` is `True`.
So in this case,
our dataset's population consists of all patients born before the year 2000.

We're interested in asthma medications,
so we want to filter the medications event frame to contain
only rows for asthma medications.
We then want details of just the latest asthma medication.
So we need to transform the `medications` event frame into another, filtered, event frame,
and then we need to transform this into a patient frame.

```python
asthma_codes = ["39113311000001107", "39113611000001102"]
latest_asthma_med = (
    medications.where(medications.dmd_code.is_in(asthma_codes))
    .sort_by(medications.date)
    .last_for_patient()
)
```

Again, this can be broken down.

```pycon
>>> medications.dmd_code.is_in(asthma_codes)
0 | 0 | True
1 | 1 | True
1 | 2 | True
1 | 3 | False
3 | 4 | False
4 | 5 | True
5 | 6 | False
5 | 7 | True
7 | 8 | False
9 | 9 | False
>>> medications.where(medications.dmd_code.is_in(asthma_codes))
patient_id        | row_id            | date              | dmd_code
------------------+-------------------+-------------------+------------------
0                 | 0                 | 2014-01-11        | 39113611000001102
1                 | 1                 | 2015-08-06        | 39113611000001102
1                 | 2                 | 2018-09-21        | 39113311000001107
4                 | 5                 | 2017-05-11        | 39113611000001102
5                 | 7                 | 2019-07-06        | 39113611000001102
>>> medications.where(medications.dmd_code.is_in(asthma_codes)).sort_by(medications.date)
patient_id        | row_id            | date              | dmd_code
------------------+-------------------+-------------------+------------------
0                 | 0                 | 2014-01-11        | 39113611000001102
1                 | 1                 | 2015-08-06        | 39113611000001102
1                 | 2                 | 2018-09-21        | 39113311000001107
4                 | 5                 | 2017-05-11        | 39113611000001102
5                 | 7                 | 2019-07-06        | 39113611000001102
>>> medications.where(medications.dmd_code.is_in(asthma_codes)).sort_by(medications.date).last_for_patient()
patient_id        | date              | dmd_code
------------------+-------------------+------------------
0                 | 2014-01-11        | 39113611000001102
1                 | 2018-09-21        | 39113311000001107
4                 | 2017-05-11        | 39113611000001102
5                 | 2019-07-06        | 39113611000001102
```

Finally, we can transform this patient frame into two patient series,
which we can then add to our dataset.

```python
dataset.asthma_med_date = latest_asthma_med.date
dataset.asthma_med_code = latest_asthma_med.code
```

:notepad_spiral: Notice how the ehrQL sandbox can be useful
when developing your ehrQL queries.
It can sometimes be quicker to try out ideas interactively via the sandbox first,
instead of repeatedly editing a dataset definition and re-running it.
