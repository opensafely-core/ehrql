
<h4 class="attr-heading" id="create_measures" data-toc-label="create_measures" markdown>
  <tt><strong>create_measures</strong>()</tt>
</h4>
<div markdown="block" class="indent">
A measure definition file must define a collection of measures called `measures`.

```python
measures = create_measures()
```

Add measures to the collection using [`define_measure`](#Measures.define_measure):

```python
measures.define_measure(
    name="adult_proportion",
    numerator=patients.age_on(INTERVAL.start_date) >=18,
    denominator=patients.exists_for_patient()
)
```
</div>


<h4 class="attr-heading" id="Measures" data-toc-label="Measures" markdown>
  <tt><em>class</em> <strong>Measures</strong>()</tt>
</h4>

<div markdown="block" class="indent">
The preferential way to create a collection of measures is with [`create_measures`](#create_measures).
<div class="attr-heading" id="Measures.define_measure">
  <tt><strong>define_measure</strong>(<em>name</em>, <em>numerator=None</em>, <em>denominator=None</em>, <em>group_by=None</em>, <em>intervals=None</em>)</tt>
  <a class="headerlink" href="#Measures.define_measure" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Add a measure to the collection of measures to be generated.

_name_<br>
The name of the measure, as a string. Only used to identify the measure in the
output. Must contain only alphanumeric and underscore characters and must
start with a letter.

_numerator_<br>
The numerator definition, which must be a patient series but can be either
boolean or integer.

_denominator_<br>
The denominator definition, which must be a patient series but can be either
boolean or integer.

_group_by_<br>
Optional groupings to break down the results by. If supplied, must be a
dictionary of the form:
```python
{
    "group_name": group_definition,
    ...
}
```

 * each _group_name_ becomes a column in the output. It must contain only
alphanumeric and underscore characters and must start with a letter. It also
must not clash with any reserved column names like "numerator" or "ratio".

 * each _group_definition_ must be a categorical patient series (i.e. a patient
series which takes only a fixed set of values).

_intervals_<br>
A list of start/end date pairs over which to evaluate the measures. These can be
most conveniently generated using the `starting_on()`/`ending_on()` methods on
[`years`](#years), [`months`](#months), and [`weeks`](#weeks) e.g.
```python
intervals = months(12).starting_on("2020-01-01")
```

The `numerator`, `denominator` and `intervals` arguments can be omitted if
default values for them have been set using
[`define_defaults()`](#Measures.define_defaults).
</div>

<div class="attr-heading" id="Measures.define_defaults">
  <tt><strong>define_defaults</strong>(<em>numerator=None</em>, <em>denominator=None</em>, <em>group_by=None</em>, <em>intervals=None</em>)</tt>
  <a class="headerlink" href="#Measures.define_defaults" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Define default values for a collection of measures. Useful to reduce
repetition when defining several measures which share common arguments.

Example usage:
```python
measures.define_defaults(
    intervals=months(6).starting_on("2020-01-01"),
)
```

Note that you can only define a single set of defaults and attempting to call
this method more than once is an error.
</div>

<div class="attr-heading" id="Measures.configure_dummy_data">
  <tt><strong>configure_dummy_data</strong>(<em>population_size=10</em>, <em>legacy=False</em>, <em>timeout=60</em>, <em>additional_population_constraint=None</em>)</tt>
  <a class="headerlink" href="#Measures.configure_dummy_data" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Configure the dummy data to be generated.

_population_size_<br>
Maximum number of patients to generate.

Note that you may get fewer patients than this if the generator runs out of time
– see `timeout` below.

_legacy_<br>
Use legacy dummy data.

_timeout_<br>
Maximum time in seconds to spend generating dummy data.

_additional_population_constraint_<br>
An additional ehrQL query that can be used to constrain the population that will
be selected for dummy data. This is incompatible with legacy mode.

For example, if you wanted to ensure that two dates appear in a particular order in your
dummy data, you could add ``additional_population_constraint = dataset.first_date <
dataset.second_date``.

You can also combine constraints with ``&`` as normal in ehrQL.
E.g. ``additional_population_constraint = patients.sex.is_in(['male', 'female']) & (
patients.age_on(some_date) < 80)`` would give you dummy data consisting of only men
and women who were under the age of 80 on some particular date.

Example usage:
```python
measures.configure_dummy_data(population_size=10000)
```
</div>

<div class="attr-heading" id="Measures.configure_disclosure_control">
  <tt><strong>configure_disclosure_control</strong>(<em>enabled=True</em>)</tt>
  <a class="headerlink" href="#Measures.configure_disclosure_control" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Configure disclosure control.

By default, numerators and denominators are subject to disclosure control.
First, values less than or equal to seven are replaced with zero (suppressed);
then, values are rounded to the nearest five.

To disable disclosure control:

```python
measures.configure_disclosure_control(enabled=False)
```

For more information about disclosure control in OpenSAFELY, please see the
"[Updated disclosure control
guidance](https://www.opensafely.org/updated-output-checking-processes/)" page.
</div>

</div>



<h4 class="attr-heading" id="INTERVAL" data-toc-label="INTERVAL" markdown>
  <tt><strong>INTERVAL</strong></tt>
</h4>
<div markdown="block" class="indent">
This is a placeholder value to be used when defining `numerator`, `denominator` and
`group_by` columns in a measure. This allows these definitions to be written once and
then be automatically evaluated over multiple different intervals. Can be used just
like any pair of dates in ehrQL.

Example usage:
```python
clinical_events.date.is_during(INTERVAL)
```
<div class="attr-heading" id="INTERVAL.start_date">
  <tt><strong>start_date</strong></tt>
  <a class="headerlink" href="#INTERVAL.start_date" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Placeholder for the start date (inclusive) of the interval. Can be used like any other
date.

Example usage:
```python
clinical_events.date.is_on_or_after(INTERVAL.start_date)
```
</div>

<div class="attr-heading" id="INTERVAL.end_date">
  <tt><strong>end_date</strong></tt>
  <a class="headerlink" href="#INTERVAL.end_date" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Placeholder for the end date (inclusive) of the interval. Can be used like any other
date.

Example usage:
```python
clinical_events.date.is_on_or_before(INTERVAL.end_date)
```
</div>

</div>
