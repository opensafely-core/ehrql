This is a brief introduction to the ehrQL schema.

:construction: We intend to add more information,
in an easier to use form here.

## Latest version of the schema

:construction: For now, the canonical reference is the:

* [source code for the core ehrQL tables](https://github.com/opensafely-core/ehrql/blob/main/ehrql/tables/beta/core.py)
* [source code for the TPP ehrQL tables](https://github.com/opensafely-core/ehrql/blob/main/ehrql/tables/beta/tpp.py)

Core ehrQL tables are available in every backend.
The TPP ehrQL tables are only available in the TPP backend.

## Understanding the schema source code

Like ehrQL dataset definitions,
the code that processes ehrQL is written in Python too.

The below text briefly explains how you might use that source code
to know what you can access in which table.
This is not ideal,
but it is not as daunting as it might sound.

## Tables

* Each `class` with `@table` above it defines an ehrQL table.
* We make tables available for use within ehrQL via an import statement.
  For example, to access the addresses and patients tables via the TPP backend, we use:
  ```python
  from ehrql.tables.beta.tpp import addresses, patients
  ```

## Frames and series

Very briefly, to understand this page:

* Frames are table-like, with rows and columns.
* Series are column-like, containing a sequence of values.

:notepad_spiral: There is a more detailed explanation of [frames and series](ehrql-concepts-in-depth.md#core-types-of-object).

## Columns as series

* Attributes on each table class typically correspond to table columns,
  and are defined as `Series`.
* The data type for the column is specified inside the `Series()` expression.

## Constraints on column values

* There may be certain constraints on column values to ensure that all values are valid.

## Example

:warning: This is a worked example using a [snapshot in time of the code as of 2023-05-03](https://github.com/opensafely-core/ehrql/blob/1fb4ab97912bf1f4fe7c95cf710bb40ded8966c9/ehrql/tables/beta/tpp.py).
It may not represent the latest schema. (The latest version of the source code is [linked at the top of this page](the-ehrql-data-schema.md#latest-version-of-the-tpp-schema).)

## Practice registrations

The ehrQL software code snippet below can be [seen in full context in the source](https://github.com/opensafely-core/ehrql/blob/1fb4ab97912bf1f4fe7c95cf710bb40ded8966c9/ehrql/tables/beta/tpp.py#L35-L66).

```python
@table
class practice_registrations(EventFrame):
    start_date = Series(datetime.date)
    end_date = Series(datetime.date)
    practice_pseudo_id = Series(int)
    practice_stp = Series(
        str,
        constraints=[Constraint.Regex("E540000[0-9]{2}")],
    )
    practice_nuts1_region_name = Series(
        str,
        constraints=[
            Constraint.Categorical(
                [
                    "North East",
                    "North West",
                    "Yorkshire and The Humber",
                    "East Midlands",
                    "West Midlands",
                    "East",
                    "London",
                    "South East",
                    "South West",
                ]
            ),
        ],
        description=(
            "Name of the NUTS level 1 region of England to which the practice belongs.\n"
            "For more information see:\n"
            "https://www.ons.gov.uk/methodology/geography/ukgeographies/eurostat"
        ),
    )
```

From this code, we can deduce that:

* This `class` represents a table.
* The table is called `practice_registrations`
  * Therefore, we make this table available for use in a dataset definition via:
    ```python
    from ehrql.tables.beta.tpp import practice_registrations
    ```
* The `practice_registrations` table is based on an [`EventFrame`](ehrql-concepts-in-depth.md#event-frames).
* The `practice_registrations` table has five columns:
  * `start_date`
    * `datetime.date` type
  * `end_date`
    * `datetime.date` type
  * `practice_pseudo_id`
    * integer type
  * `practice_stp`
    * string type
    * `practice_stp` has the constraint that the value must start `E540000`
      and be followed by another two digits of 0-9.
  * `practice_nuts1_region_name`
    * string type
    * `practice_nuts1_region_name` has the constraint that it must match one of several names of UK geographical regions.
      For example, `North East`.
* The table has a `description` attribute,
  that provides human-readable information about the table.
* If we use the above `import` statement in the dataset definition,
  we can access columns on the `practice_registrations` table
  by specifying the table name and column name separated by a dot.
  * Example: `practice_registrations.start_date`
