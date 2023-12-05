ehrQL v1 was released on Friday 8th December 2023.

It contains a small number of breaking changes from v0.

## Upgrading from v0

* In `project.yaml`, replace either `ehrql:v0` or `databuilder:v0` with `ehrql:v1`
* From the command line, run `opensafely pull ehrql`

## Breaking changes

### Removal of `databuilder` imports

Some projects have been using ehrQL from when the project was called "Databuilder".

Update lines in your dataset definition that use `databuilder` imports to `ehrql`.
For example, change:

```python
from databuilder import create_dataset
```

to:

```python
from ehrql import create_dataset
```


### Movement of tables out of the "beta" namespace

Tables have been moved out of the "beta" namespace.

Update lines in your dataset definition that import tables from the beta namespace.
For example, change:

```python
from ehrql.tables.beta.core import patients
```

to:

```python
from ehrql.tables.core import patients
```

### Change to default size of dummy dataset

By default, a dummy dataset will now contain data for 10 patients.
This means when you generate a dummy dataset from the console,
you get a tractable amount of output.

This can be changed per dataset with:

```python
dataset.configure_dummy_data(population_size=1000)
```

### Renaming of language features

For consistency, a few small language features have been renamed.

* `if_null_then` has been renamed to `when_null_then`.
* The `default` argument to `case()` has been renamed to `otherwise`.
* `Dataset.configure_dummy_dataset` has been renamed to `Dataset.configure_dummy_data`.


### Deprecation of `tpp.hospital_admissions` table

The `tpp.hospital_admissions` table duplicated the `tpp.apcs` table.
Additionally, its `.primary_diagnoses` field should have been called `.primary_diagnosis`.

Update lines in your dataset definition that use `tpp.hospital_admissions` to use `tpp.apcs`
For example, change:

```python
from ehrql.tables.beta.core import hospital_admissions
```

to:

```python
from ehrql.tables.core import apcs
```


### Change to behaviour when household information is missing

When querying `tpp.household_memberships_2020`,
`None` is now returned instead of zero if information for a household is missing.


## Getting help

If you are stuck or unsure how to upgrade, ask your co-pilot or seek help in Slack.
