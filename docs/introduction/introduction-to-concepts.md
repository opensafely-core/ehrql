This page outlines some important concepts that you should understand
before reading the rest of the documentation.

**ehrQL** is a Python-based query language for electronic health record (EHR) data.
ehrQL has been designed for use with the OpenSAFELY platform.

An ehrQL query takes the form of a **dataset definition**.

A dataset definition is written in [Python](https://docs.python.org/3/tutorial/index.html)
and is saved in a file.

When a dataset definition is **executed** against data,
a **dataset** is generated and written to an output file.

A dataset definition may run against **dummy data**, when developing the ehrQL query on your own computer,
or real patient data, when the dataset definition runs on the OpenSAFELY platform.

A dataset is a table containing **one row per patient**,
and **one column per feature of interest**.

Features of interest might include:

* a patient's age on a given date
* whether a patient has received a particular medication in a given interval
* a patient's recorded cause of death

Refer to the [collection of examples](../how-to/examples.md) for more examples of features,
and how to include features in an ehrQL query.

A dataset is restricted to include only the patients who belong to a specified **population**.
For example, a typical study might be interested only in the population of patients:

* who were registered with any practice on a given date
* who died in a certain interval
* who received a particular diagnosis

Once a dataset has been generated,
further analysis can be carried out.
Refer to [ehrQL and OpenSAFELY](../explanation/using-ehrql-in-opensafely-projects.md) for more details.

## A short ehrQL example

:bulb: This example is here to give you an idea of what ehrQL looks like.
It is explained more fully in the tutorial.

### The dataset definition

This is a minimal,
but complete,
example of a dataset definition:

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

In this dataset definition,
the dataset is restricted to the population of patients born on or before 31st December 1999.
The features of interest are the Dictionary of Medicines and Devices (dm+d) code,
and date of the last asthma medication
that the patient was prescribed.

### The output

The above dataset definition,
when executed against some simple dummy data,
might generate a CSV file containing the following rows:

| `patient_id` | `med_date` | `med_code`
|-|-|-
| 0 | 2014-01-11 | 39113611000001102
| 1 | 2018-09-21 | 39113311000001107
| 4 | 2017-05-11 | 39113611000001102
| 5 | 2019-07-06 | 39113611000001102
