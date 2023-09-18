<h4 class="attr-heading" id="Dataset" data-toc-label="Dataset" markdown>
  <tt><em>class</em> <strong>Dataset</strong>()</tt>
</h4>

<div markdown="block" class="indent">
Defines the patients you want to include in your dataset and the variables you want
to extract for each patient.

Every dataset definition file must define a `Dataset()` instance called `dataset`
like so:
```py
dataset = Dataset()
```

Variables are added to the dataset as attributes, for example:
```py
dataset.age = patients.age_on("2020-01-01")
```
<div class="attr-heading" id="Dataset.define_population">
  <tt><strong>define_population</strong>(<em>population_condition</em>)</tt>
  <a class="headerlink" href="#Dataset.define_population" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Define the condition that patients must meet to be included in the Dataset, in
the form of a [boolean patient series](#BoolPatientSeries) e.g.
```py
dataset.define_population(patients.date_of_birth < "1990-01-01")
```
</div>

<div class="attr-heading" id="Dataset.configure_dummy_data">
  <tt><strong>configure_dummy_data</strong>(<em>population_size</em>)</tt>
  <a class="headerlink" href="#Dataset.configure_dummy_data" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Configure the dummy data to be generated.

```py
dataset.configure_dummy_data(population_size=10000)
```
</div>

</div>



<h4 class="attr-heading" id="case" data-toc-label="case" markdown>
  <tt><strong>case</strong>(<em>*when_thens</em>, <em>default=None</em>)</tt>
</h4>
<div markdown="block" class="indent">
Take a sequence of condition-values of the form:
```py
when(condition).then(value)
```

And evaluate them in order, returning the value of the first condition which
evaluates True. If no condition matches and a `default` is specified then return
that, otherwise return NULL.

For example:
```py
category = case(
    when(size < 10).then("small"),
    when(size < 20).then("medium"),
    when(size >= 20).then("large"),
    default="unknown",
)
```

Note that because the conditions are evaluated in order we don't need the condition
for "medium" to specify `(size >= 10) & (size < 20)` because by the time the
condition for "medium" is being evaluated we already know the condition for "small"
is False.

A simpler form is available when there is a single condition.  This example:
```py
category = case(
    when(size < 15).then("small"),
    default="large",
)
```

can be rewritten as:
```py
category = when(size < 15).then("small").otherwise("large")
```
</div>



<h4 class="attr-heading" id="codelist_from_csv" data-toc-label="codelist_from_csv" markdown>
  <tt><strong>codelist_from_csv</strong>(<em>filename</em>, <em>column</em>, <em>category_column=None</em>)</tt>
</h4>
<div markdown="block" class="indent">
Read a codelist from a CSV file as either a list or a dictionary (for categorised
codelists).

_filename_<br>
Path to the file on disk, relative to the root of your repository. (Remember to use
UNIX/style/forward-slashes not Windows\style\backslashes.)

_column_<br>
Name of the column in the CSV file which contains the codes.

_category_column_<br>
Optional name of a column in the CSV file which contains categories to which each
code should be mapped. If this argument is passed then the resulting codelist will
be a dictionary mapping each code to its corresponding category. This can be passed
to the [`to_category()`](#CodePatientSeries.to_category) method to map a series of
codes to a series of categories.
</div>



<h4 class="attr-heading" id="maximum_of" data-toc-label="maximum_of" markdown>
  <tt><strong>maximum_of</strong>(<em>*args</em>)</tt>
</h4>
<div markdown="block" class="indent">
Return the maximum value of a collection of Series or Values, disregarding NULLs

For example:
```py
latest_event_date = maximum_of(event_series_1.date, event_series_2.date, "2001-01-01")
```
</div>



<h4 class="attr-heading" id="minimum_of" data-toc-label="minimum_of" markdown>
  <tt><strong>minimum_of</strong>(<em>*args</em>)</tt>
</h4>
<div markdown="block" class="indent">
Return the minimum value of a collection of Series or Values, disregarding NULLs

For example:
```py
ealiest_event_date = minimum_of(event_series_1.date, event_series_2.date, "2001-01-01")
```
</div>
