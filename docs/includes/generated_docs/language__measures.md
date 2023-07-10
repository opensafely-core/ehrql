<h4 class="attr-heading" id="Measures" data-toc-label="Measures" markdown>
  <tt><em>class</em> <strong>Measures</strong>()</tt>
</h4>

<div markdown="block" class="indent">
Define a collection of measures to be generated. Each measure definition file must
define a single `Measures()` instance called `measures` like so:
```py
measures = Measures()
```
<div class="attr-heading" id="Measures.define_measure">
  <tt><strong>define_measure</strong>(<em>name</em>, <em>numerator=None</em>, <em>denominator=None</em>, <em>group_by=None</em>, <em>intervals=None</em>)</tt>
  <a class="headerlink" href="#Measures.define_measure" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Add a measure to the list of measures to be generated.

_name_<br>
The name of the measure, as a string.

_numerator_<br>
The numerator definition, which must be a patient series but can be either
boolean or integer.

_denominator_<br>
The denominator definition, which must be a patient series but can be either
boolean or integer.

_group_by_<br>
Optional groupings to break down the results by. Must be supplied as a
dictionary of the form:
```py
{
    "group_name": group_definition,
    ...
}
```

_intervals_<br>
A list of start/end date pairs over which to evaluate the measures. These can be
most conveniently generated using the `starting_at()`/`ending_at()` methods on
[`years`](#years), [`months`](#months), and [`weeks`](#weeks) e.g.
```py
intervals = months(12).starting_at("2020-01-01")
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
When defining several measures which share common arguments you can reduce
repetition by defining default values for the measures.

Note that you can only define a single set of defaults and attempting to call
this method more than once is an error.
</div>

</div>



<h4 class="attr-heading" id="INTERVAL" data-toc-label="INTERVAL" markdown>
  <tt><strong>INTERVAL</strong></tt>
</h4>
<div markdown="block" class="indent">
This is a placeholder value to be used when defining numerator, denominator and group_by
columns in a measure. This allows these definitions to be written once and then be
automatically evaluated over multiple different intervals. It can be used just like any
pair of dates in ehrQL e.g.
```py
clincial_events.date.is_during(INTERVAL)
```
<div class="attr-heading" id="INTERVAL.start_date">
  <tt><strong>start_date</strong></tt>
  <a class="headerlink" href="#INTERVAL.start_date" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Placeholder for the start date (inclusive) of the interval. Can be used like any other
date e.g.
```py
clinical_events.date.is_on_or_after(INTERVAL.start_date)
```
</div>

<div class="attr-heading" id="INTERVAL.end_date">
  <tt><strong>end_date</strong></tt>
  <a class="headerlink" href="#INTERVAL.end_date" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Placeholder for the end date (inclusive) of the interval. Can be used like any other
date e.g.
```py
clinical_events.date.is_on_or_before(INTERVAL.end_date)
```
</div>

</div>
