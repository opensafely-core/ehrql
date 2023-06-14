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

If you have read these documentation pages in the [suggested order](ehrql-documentation.md#table-of-contents),
then all the examples you will have seen access the _core_ tables.

The core tables are intended to be compatible with multiple OpenSAFELY backends.
If you *only* use the core tables,
then your ehrQL dataset definition will be compatible with different OpenSAFELY backends,
without requiring any changes.

### Importing core tables

Make the core tables available for use in a dataset definition
with import statements like:

```python
from ehrql.tables.beta.core import medications, patients
```

where the `ehrql.tables.beta.core` specifies that we are using the core tables.

:spiral_notepad: Read the page on the [ehrQL data schema](the-ehrql-data-schema.md)
to learn how to understand which core tables are available,
and the data schema for those tables.

## Backend-specific tables

Different OpenSAFELY backends may opt to provide additional data tables other than the core tables.
You may wish to access these tables if the core tables are not sufficient
to answer the research question of interest.

:warning: When using backend-specific tables in a dataset definition,
your dataset definition will be only compatible with that backend.

:construction: TPP is the most fully developed backend,
offering several data tables.

:spiral_notepad: Implementation of other backends is still in development.
But all data in the EMIS OpenSAFELY backend is available via cohort-extractor.

### Importing backend-specific tables

Instead of referring to `core` in the import statement,
we use the name of the backend.

For example, for TPP-specific tables,
we use `tpp` in the import statement:

```python
from ehrql.tables.beta.tpp import addresses, patients
```

:spiral_notepad: In this example,
the `addresses` table is specific to the TPP backend.
The `patients` table is a core ehrQL table.
We import both core and backend-specific tables within a single import statement.

:spiral_notepad: Read the page on the [ehrQL data schema](the-ehrql-data-schema.md)
to learn how to understand which backend-specific tables are available,
and the data schema for those tables.

# What to read next

:fast_forward: [The ehrQL data schema](the-ehrql-data-schema.md)
