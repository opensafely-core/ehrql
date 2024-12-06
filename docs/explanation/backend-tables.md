OpenSAFELY provides secure access to real data
via different OpenSAFELY backends.

For example, there is a TPP backend,
for querying patient data held by TPP.

The tables that are available for use in ehrQL
depend on which OpenSAFELY backend that you access.

We can consider two kinds of table:

* core tables
* backend-specific tables

## Core tables

If you have read these documentation pages in the suggested order,
then all the examples you will have seen access the _core_ tables.

The core tables are intended to be compatible with any OpenSAFELY backend providing primary care data.
If you *only* use the core tables,
then your ehrQL dataset definition will be compatible with different OpenSAFELY backends,
without requiring any changes.

### Importing core tables

Make the core tables available for use in a dataset definition
with import statements like:

```python
from ehrql.tables.core import medications, patients
```

where the `ehrql.tables.core` specifies that we are using the core tables.

## Backend-specific tables

Different OpenSAFELY backends may opt to provide additional data tables other than the core tables.
You may wish to access these tables if the core tables are not sufficient
to answer the research question of interest.

:warning: When using backend-specific tables in a dataset definition,
your dataset definition will be only compatible with that backend.

:notepad_spiral: Implementation of other backends is still in development.
But all data in the EMIS OpenSAFELY backend is available via cohort-extractor.

### Importing backend-specific tables

Instead of referring to `core` in the import statement,
we use the name of the backend.

For example, for TPP-specific tables,
we use `tpp` in the import statement:

```python
from ehrql.tables.tpp import addresses, patients
```

:notepad_spiral: In this example,
the `addresses` table is specific to the TPP backend.
The `patients` table is a core ehrQL table.
We import both core and backend-specific tables within a single import statement.

## Using the table schema reference

In the examples given so far,
the names of the table schemas, tables and columns
have been provided for you.

For example,
in the initial [dataset definition](../tutorial/working-with-data-with-ehrql/index.md) of the tutorial,
we had the following line:

```python
from ehrql.tables.core import patients, practice_registrations, clinical_events, medications
```

* `core` is the *table schema*
* `patients`, `practice_registrations`, `clinical_events` and `medications` are the *table names*

We also used the `show()` command to display the `patients` table and saw that the *table columns*
available were `date_of_birth`, `sex` and `date_of_death`.

Use the [table schema reference](../reference/schemas.md)
to look up which schemas and columns are available.

The table schema reference explains:

* which backends support the schema
* the table column names
* the table column data types
* any additional constraints on table column values
* additional contextual information about table columns
* whether table columns contain at most one row per patient,
  or may contain multiple rows per patient

:grey_question: Consult the [`core`](../reference/schemas/core.md) schema.
Choose any of the tables there
and understand its structure from the schema.
