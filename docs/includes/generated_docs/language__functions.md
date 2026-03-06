
<h4 class="attr-heading" id="case" data-toc-label="case" markdown>
  <tt><strong>case</strong>(<em>*when_thens</em>, <em>otherwise=None</em>)</tt>
</h4>
<div markdown="block" class="indent">
Take a sequence of condition-values of the form:
```python
when(condition).then(value)
```

And evaluate them in order, returning the value of the first condition which
evaluates True. If no condition matches, return the `otherwise` value (or NULL
if no `otherwise` value is specified).

Example usage:
```python
category = case(
    when(size < 10).then("small"),
    when(size < 20).then("medium"),
    when(size >= 20).then("large"),
    otherwise="unknown",
)
```

Note that because the conditions are evaluated in order we don't need the condition
for "medium" to specify `(size >= 10) & (size < 20)` because by the time the
condition for "medium" is being evaluated we already know the condition for "small"
is False.

A simpler form is available when there is a single condition.  This example:
```python
category = case(
    when(size < 15).then("small"),
    otherwise="large",
)
```

can be rewritten as:
```python
category = when(size < 15).then("small").otherwise("large")
```
</div>



<h4 class="attr-heading" id="maximum_of" data-toc-label="maximum_of" markdown>
  <tt><strong>maximum_of</strong>(<em>value</em>, <em>other_value</em>, <em>*other_values</em>)</tt>
</h4>
<div markdown="block" class="indent">
Return the maximum value of a collection of Series or Values, disregarding NULLs.
Unless all values in the collection are NULL, in which case return NULL.

Example usage:
```python
latest_event_date = maximum_of(event_series_1.date, event_series_2.date, "2001-01-01")
```
</div>



<h4 class="attr-heading" id="minimum_of" data-toc-label="minimum_of" markdown>
  <tt><strong>minimum_of</strong>(<em>value</em>, <em>other_value</em>, <em>*other_values</em>)</tt>
</h4>
<div markdown="block" class="indent">
Return the minimum value of a collection of Series or Values, disregarding NULLs.
Unless all values in the collection are NULL, in which case return NULL.

Example usage:
```python
earliest_event_date = minimum_of(event_series_1.date, event_series_2.date, "2001-01-01")
```
</div>



<h4 class="attr-heading" id="table_from_file" data-toc-label="table_from_file" markdown>
  <tt><strong>table_from_file</strong>(<em>path</em>, <em>columns=None</em>)</tt>
</h4>
<div markdown="block" class="indent">
Return a [`PatientFrame`](#PatientFrame) with data from the supplied file and having
the specified columns. This allows you to include data extracted by other actions in
your queries, just as if they were part of an ordinary table in the database.

_columns_<br>
A dictionary giving the names and types of the columns to use you want to use from
the file. For example:
```python
columns={
    "age": int,
    "sex": str,
    "index_date": datetime.date,
}
```

You don't have to include every column in the file, just the ones you want to use.
The order of the columns doesn't matter and you don't need to include the
`patient_id` column as ehrQL always includes this automatically.

This feature is commonly used in [case-control studies][cc-study], where cases and
controls are extracted and matched in separate actions and must then be combined
together.

For example, suppose you have a file `outputs/matched.arrow` with columns:

patient_id | age | sex    | index_date
---------- | --- | ------ | ----------
12345      |  23 | male   | 2025-06-01
67890      |  46 | female | 2024-10-01
…          |  …  | …      | …

You can use this as an ehrQL table with:

```python
import datetime
from ehrql import table_from_file

matched_patients = table_from_file(
    "outputs/matched.arrow",
    columns={
        "age": int,
        "sex": str,
        "index_date": datetime.date,
    }
)
```

You can then use `matched_patients` like any other ehrQL table e.g.
```python
from ehrql import create_dataset
from ehrql.tables.core import clinical_events

dataset = create_dataset()
# Include only patients with matches
dataset.define_population(
    matched_patients.exists_for_patient()
)

# Find events after each matched patient's index date
events = clinical_events.where(
    clinical_events.is_on_or_after(matched_patients.index_date)
)
```

[cc-study]: https://docs.opensafely.org/case-control-studies/
</div>



<h4 class="attr-heading" id="show" data-toc-label="show" markdown>
  <tt><strong>show</strong>(<em>element</em>, <em>*other_elements</em>, <em>label=None</em>, <em>head=None</em>, <em>tail=None</em>)</tt>
</h4>
<div markdown="block" class="indent">
Show the output of the specified ehrQL element or elements, derived from data in
local [dummy tables](../tutorials/dummy-data/provide-dummy-tables/index.md).

_element_<br>
Any ehrql element, such as a column, table or dataset.

_other_elements_<br>
0 or more compatible ehrQL columns can be provided, and will be dislayed in a single table.

If passing in multiple arguments, they must either have:

  - one row per patient (e.g. patients.sex, clinical_events.count_for_patient()), or
  - multiple rows per patient AND be from the same table (e.g. clinical_events.date,
      clinical_events.numeric_values)

_label_<br>
Optional label which will be printed in the `show` output.

_head_<br>
Show only the first N lines. If the output is an ehrQL column, table or dataset, it will
print only the first N lines of the table.

_tail_<br>
Show only the last N lines. If the output is an ehrQL column, table or dataset, it will
print only the last N lines of the table.

`head` and `tail` arguments can be combined, e.g. to show the first and last 5 lines of a table:

  `show(<table>, head=5, tail=5)`

For more detail on using the `show` function, see the
[documentation on the OpenSAFELY VS Code extension](../explanation/vscode-extension.md#the-show-function).
</div>
