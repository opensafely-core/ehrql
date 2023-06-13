ehrQL takes queries written by researchers (what we call "dataset definitions") and transforms them into SQL.
Although the exact SQL generated will be different for every dataset definition — and will be different for each type of database it is run against — there are certain basic patterns they will have in common.

At a high level, ehrQL proceeds by:
 1. generating a number of **intermediate queries**;
 2. transforming the output of these intermediate queries into something "**table-like**";
 3. determining the **population table**;
 4. joining the output of all these queries together in a final **results query**.


### 1. Intermediate queries

The job of the intermediate queries is to take data which contains multiple rows for each patient (e.g. a table of clinical events) and produce output which contains only one row for each patient (e.g. the most recent date that a certain event occurred for each patient).

There are only two patterns of query we use to do this.

#### (a) `AGGREGATE` and `GROUP BY`

For example, this counts the number of "xyz123" events for each patient (though other aggregation functions like `MAX` or `SUM` could be used here).

```sql
SELECT
  patient_id,
  COUNT(*)
FROM
  events
WHERE
  events.snomedct_code = 'xyz123'
GROUP BY
  patient_id
```

#### (b) `ORDER BY` and `PARTITION`

This example gets the `numeric_value` associated with the most recent "xyz123" event for each patient by sorting by `date` and getting just the first matching row for each patient.

```sql
SELECT
  patient_id,
  numeric_value
FROM (
  SELECT
    patient_id,
    numeric_value,
    row_number() OVER (PARTITION BY patient_id ORDER BY date DESC) AS row_num
  FROM
    events
  WHERE
    events.snomedct_code = 'xyz123'
) t
WHERE row_num = 1
```

In both cases, these queries will often involve pulling data from multiple tables which will all be joined on `patient_id` e.g.
```sql
SELECT
  table_1.patient_id,
  ...
FROM
  table_1
LEFT JOIN table_2
  ON table_1.patient_id = table_2.patient_id
LEFT JOIN table_3
  ON table_1.patient_id = table_3.patient_id
WHERE
  ...
GROUP BY
  table_1.patient_id
```


### 2. Table-like outputs

We need to use the outputs of the intermediate queries as the inputs to further queries — both other intermediate queries and the final results query.
This means that we need to transform them into something "table-like" i.e. something which can play the syntactic role of a table in other queries.
The exact method we use for this changes depending on which kind of database we're running against as different databases have different options available and different performance characteristics.
The three methods currently in use are:

#### (a) Common Table Expressions (CTEs)

```sql
WITH intermediate_table_1 AS (
  <SELECT ...>
)
```

#### (b) Temporary views

```sql
CREATE TEMPORARY VIEW intermediate_table_1 AS
  <SELECT ...>
```

#### (c) MS-SQL Temporary Tables

```sql
SELECT * INTO #intermediate_table_1 FROM (
  <SELECT ...>
) t
```


### 3. Population table

In order to build the final JOIN which produces our results we need a table containing all the `patient_id`s that are relevant to our query. By default we do this by UNIONing together all the `patient_id`s in all the tables referenced in the "population definition" (the property of a dataset definition describing the patients that should be included). The resulting query looks something like:
```sql
SELECT intermediate_table_1.patient_id FROM intermediate_table_1
UNION
SELECT intermediate_table_2.patient_id FROM intermediate_table_2
UNION
SELECT intermediate_table_2.patient_id FROM intermediate_table_3
UNION
...
```

It's important that this query doesn't miss out any `patient_id`s which ought to be included, but it doesn't matter if it includes additional patients because the WHERE clause on the final results query will filter these out.
So, as an optimisation, if there's a table which we can guarantee will always contain _all_ the `patient_id`s in the database (e.g. a `patients` or `registrations` table) then we can use that directly instead of doing these UNIONs.


### 4. Final results query

This is just a big LEFT JOIN against the population table, including the various intermediate tables and filtered by the population definition.
```sql
SELECT
  population_table.patient_id,
  <column_1_definition> AS output_column_1,
  <column_2_definition> AS output_column_2,
  ...
FROM
  population_table
LEFT JOIN intermediate_table_1
  ON population_table.patient_id = intermediate_table_1.patient_id
LEFT JOIN intermediate_table_2
  ON population_table.patient_id = intermediate_table_2.patient_id
...
WHERE
  <population_definition>
```
