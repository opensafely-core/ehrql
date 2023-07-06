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


<h4 class="attr-heading" id="days" data-toc-label="days" markdown>
  <tt><em>class</em> <strong>days</strong>(<em>value</em>)</tt>
</h4>

<div markdown="block" class="indent">
Represents a duration of time specified in days
<div class="attr-heading" id="days.eq">
  <tt><em>self</em> <strong>==</strong> <em>other</em></tt>
  <a class="headerlink" href="#days.eq" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean indicating whether the two durations have the same value and units.
</div>

<div class="attr-heading" id="days.ne">
  <tt><em>self</em> <strong>!=</strong> <em>other</em></tt>
  <a class="headerlink" href="#days.ne" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean indicating whether the two durations do not have the same value
and units.
</div>

<div class="attr-heading" id="days.add">
  <tt><em>self</em> <strong>+</strong> <em>other</em></tt>
  <a class="headerlink" href="#days.add" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Add this duration to a date to produce a new date.

Alternatively two durations with the same units may be added to produce a new duration.
</div>

<div class="attr-heading" id="days.sub">
  <tt><em>self</em> <strong>-</strong> <em>other</em></tt>
  <a class="headerlink" href="#days.sub" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Subtract another duration of the same units from this duration.
</div>

<div class="attr-heading" id="days.neg">
  <tt><em></em> <strong>-</strong> <em>self</em></tt>
  <a class="headerlink" href="#days.neg" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Invert this duration so that rather that representing a movement, say, four
weeks forwards in time it now represents a movement four weeks backwards.
</div>

<div class="attr-heading" id="days.starting_on">
  <tt><strong>starting_on</strong>(<em>date</em>)</tt>
  <a class="headerlink" href="#days.starting_on" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a list of time intervals covering the duration starting on the supplied
date. For example:
```py
weeks(3).starting_on("2000-01-01")
```
Returns:
```
[
    (date(2000, 1, 1), date(2000, 1, 7)),
    (date(2000, 1, 8), date(2000, 1, 14)),
    (date(2000, 1, 15), date(2000, 1, 21)),
]
```

Useful for generating the `intervals` arguments to [`Measures`](#Measures).
</div>

<div class="attr-heading" id="days.ending_on">
  <tt><strong>ending_on</strong>(<em>date</em>)</tt>
  <a class="headerlink" href="#days.ending_on" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a list of time intervals covering the duration ending on the supplied
date. For example:
```py
weeks(3).ending_on("2000-01-15")
```
Returns:
```
[
    (date(2000, 1, 1), date(2000, 1, 7)),
    (date(2000, 1, 8), date(2000, 1, 14)),
    (date(2000, 1, 15), date(2000, 1, 21)),
]
```

Useful for generating the `intervals` arguments to [`Measures`](#Measures).
</div>

</div>


<h4 class="attr-heading" id="months" data-toc-label="months" markdown>
  <tt><em>class</em> <strong>months</strong>(<em>value</em>)</tt>
</h4>

<div markdown="block" class="indent">
Represents a duration of time specified in calendar months
<div class="attr-heading" id="months.eq">
  <tt><em>self</em> <strong>==</strong> <em>other</em></tt>
  <a class="headerlink" href="#months.eq" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean indicating whether the two durations have the same value and units.
</div>

<div class="attr-heading" id="months.ne">
  <tt><em>self</em> <strong>!=</strong> <em>other</em></tt>
  <a class="headerlink" href="#months.ne" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean indicating whether the two durations do not have the same value
and units.
</div>

<div class="attr-heading" id="months.add">
  <tt><em>self</em> <strong>+</strong> <em>other</em></tt>
  <a class="headerlink" href="#months.add" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Add this duration to a date to produce a new date.

Alternatively two durations with the same units may be added to produce a new duration.
</div>

<div class="attr-heading" id="months.sub">
  <tt><em>self</em> <strong>-</strong> <em>other</em></tt>
  <a class="headerlink" href="#months.sub" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Subtract another duration of the same units from this duration.
</div>

<div class="attr-heading" id="months.neg">
  <tt><em></em> <strong>-</strong> <em>self</em></tt>
  <a class="headerlink" href="#months.neg" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Invert this duration so that rather that representing a movement, say, four
weeks forwards in time it now represents a movement four weeks backwards.
</div>

<div class="attr-heading" id="months.starting_on">
  <tt><strong>starting_on</strong>(<em>date</em>)</tt>
  <a class="headerlink" href="#months.starting_on" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a list of time intervals covering the duration starting on the supplied
date. For example:
```py
weeks(3).starting_on("2000-01-01")
```
Returns:
```
[
    (date(2000, 1, 1), date(2000, 1, 7)),
    (date(2000, 1, 8), date(2000, 1, 14)),
    (date(2000, 1, 15), date(2000, 1, 21)),
]
```

Useful for generating the `intervals` arguments to [`Measures`](#Measures).
</div>

<div class="attr-heading" id="months.ending_on">
  <tt><strong>ending_on</strong>(<em>date</em>)</tt>
  <a class="headerlink" href="#months.ending_on" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a list of time intervals covering the duration ending on the supplied
date. For example:
```py
weeks(3).ending_on("2000-01-15")
```
Returns:
```
[
    (date(2000, 1, 1), date(2000, 1, 7)),
    (date(2000, 1, 8), date(2000, 1, 14)),
    (date(2000, 1, 15), date(2000, 1, 21)),
]
```

Useful for generating the `intervals` arguments to [`Measures`](#Measures).
</div>

</div>


<h4 class="attr-heading" id="weeks" data-toc-label="weeks" markdown>
  <tt><em>class</em> <strong>weeks</strong>(<em>value</em>)</tt>
</h4>

<div markdown="block" class="indent">
Represents a duration of time specified in weeks
<div class="attr-heading" id="weeks.eq">
  <tt><em>self</em> <strong>==</strong> <em>other</em></tt>
  <a class="headerlink" href="#weeks.eq" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean indicating whether the two durations have the same value and units.
</div>

<div class="attr-heading" id="weeks.ne">
  <tt><em>self</em> <strong>!=</strong> <em>other</em></tt>
  <a class="headerlink" href="#weeks.ne" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean indicating whether the two durations do not have the same value
and units.
</div>

<div class="attr-heading" id="weeks.add">
  <tt><em>self</em> <strong>+</strong> <em>other</em></tt>
  <a class="headerlink" href="#weeks.add" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Add this duration to a date to produce a new date.

Alternatively two durations with the same units may be added to produce a new duration.
</div>

<div class="attr-heading" id="weeks.sub">
  <tt><em>self</em> <strong>-</strong> <em>other</em></tt>
  <a class="headerlink" href="#weeks.sub" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Subtract another duration of the same units from this duration.
</div>

<div class="attr-heading" id="weeks.neg">
  <tt><em></em> <strong>-</strong> <em>self</em></tt>
  <a class="headerlink" href="#weeks.neg" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Invert this duration so that rather that representing a movement, say, four
weeks forwards in time it now represents a movement four weeks backwards.
</div>

<div class="attr-heading" id="weeks.starting_on">
  <tt><strong>starting_on</strong>(<em>date</em>)</tt>
  <a class="headerlink" href="#weeks.starting_on" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a list of time intervals covering the duration starting on the supplied
date. For example:
```py
weeks(3).starting_on("2000-01-01")
```
Returns:
```
[
    (date(2000, 1, 1), date(2000, 1, 7)),
    (date(2000, 1, 8), date(2000, 1, 14)),
    (date(2000, 1, 15), date(2000, 1, 21)),
]
```

Useful for generating the `intervals` arguments to [`Measures`](#Measures).
</div>

<div class="attr-heading" id="weeks.ending_on">
  <tt><strong>ending_on</strong>(<em>date</em>)</tt>
  <a class="headerlink" href="#weeks.ending_on" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a list of time intervals covering the duration ending on the supplied
date. For example:
```py
weeks(3).ending_on("2000-01-15")
```
Returns:
```
[
    (date(2000, 1, 1), date(2000, 1, 7)),
    (date(2000, 1, 8), date(2000, 1, 14)),
    (date(2000, 1, 15), date(2000, 1, 21)),
]
```

Useful for generating the `intervals` arguments to [`Measures`](#Measures).
</div>

</div>


<h4 class="attr-heading" id="years" data-toc-label="years" markdown>
  <tt><em>class</em> <strong>years</strong>(<em>value</em>)</tt>
</h4>

<div markdown="block" class="indent">
Represents a duration of time specified in calendar years
<div class="attr-heading" id="years.eq">
  <tt><em>self</em> <strong>==</strong> <em>other</em></tt>
  <a class="headerlink" href="#years.eq" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean indicating whether the two durations have the same value and units.
</div>

<div class="attr-heading" id="years.ne">
  <tt><em>self</em> <strong>!=</strong> <em>other</em></tt>
  <a class="headerlink" href="#years.ne" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean indicating whether the two durations do not have the same value
and units.
</div>

<div class="attr-heading" id="years.add">
  <tt><em>self</em> <strong>+</strong> <em>other</em></tt>
  <a class="headerlink" href="#years.add" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Add this duration to a date to produce a new date.

Alternatively two durations with the same units may be added to produce a new duration.
</div>

<div class="attr-heading" id="years.sub">
  <tt><em>self</em> <strong>-</strong> <em>other</em></tt>
  <a class="headerlink" href="#years.sub" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Subtract another duration of the same units from this duration.
</div>

<div class="attr-heading" id="years.neg">
  <tt><em></em> <strong>-</strong> <em>self</em></tt>
  <a class="headerlink" href="#years.neg" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Invert this duration so that rather that representing a movement, say, four
weeks forwards in time it now represents a movement four weeks backwards.
</div>

<div class="attr-heading" id="years.starting_on">
  <tt><strong>starting_on</strong>(<em>date</em>)</tt>
  <a class="headerlink" href="#years.starting_on" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a list of time intervals covering the duration starting on the supplied
date. For example:
```py
weeks(3).starting_on("2000-01-01")
```
Returns:
```
[
    (date(2000, 1, 1), date(2000, 1, 7)),
    (date(2000, 1, 8), date(2000, 1, 14)),
    (date(2000, 1, 15), date(2000, 1, 21)),
]
```

Useful for generating the `intervals` arguments to [`Measures`](#Measures).
</div>

<div class="attr-heading" id="years.ending_on">
  <tt><strong>ending_on</strong>(<em>date</em>)</tt>
  <a class="headerlink" href="#years.ending_on" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a list of time intervals covering the duration ending on the supplied
date. For example:
```py
weeks(3).ending_on("2000-01-15")
```
Returns:
```
[
    (date(2000, 1, 1), date(2000, 1, 7)),
    (date(2000, 1, 8), date(2000, 1, 14)),
    (date(2000, 1, 15), date(2000, 1, 21)),
]
```

Useful for generating the `intervals` arguments to [`Measures`](#Measures).
</div>

</div>
