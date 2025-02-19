<h4 class="attr-heading" id="DateDifference" data-toc-label="DateDifference" markdown>
  <tt><em>class</em> <strong>DateDifference</strong>(<em>lhs</em>, <em>rhs</em>)</tt>
</h4>

<div markdown="block" class="indent">
Represents the difference between two dates or date series (i.e. it is what you
get when you perform subtractions on [DatePatientSeries](#DatePatientSeries.sub)
or [DateEventSeries](#DateEventSeries.sub)).
<div class="attr-heading" id="DateDifference.days">
  <tt><strong>days</strong></tt>
  <a class="headerlink" href="#DateDifference.days" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
The value of the date difference in days (can be positive or negative).
</div>

<div class="attr-heading" id="DateDifference.weeks">
  <tt><strong>weeks</strong></tt>
  <a class="headerlink" href="#DateDifference.weeks" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
The value of the date difference in whole weeks (can be positive or negative).
</div>

<div class="attr-heading" id="DateDifference.months">
  <tt><strong>months</strong></tt>
  <a class="headerlink" href="#DateDifference.months" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
The value of the date difference in whole calendar months (can be positive or
negative).
</div>

<div class="attr-heading" id="DateDifference.years">
  <tt><strong>years</strong></tt>
  <a class="headerlink" href="#DateDifference.years" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
The value of the date difference in whole calendar years (can be positive or
negative).
</div>

</div>


<h4 class="attr-heading" id="days" data-toc-label="days" markdown>
  <tt><em>class</em> <strong>days</strong>(<em>value</em>)</tt>
</h4>

<div markdown="block" class="indent">
Represents a duration of time specified in days.

Example usage:
```python
last_medication_date = medications.sort_by(medications.date).last_for_patient().date
start_date = last_medication_date - days(90)
end_date = last_medication_date + days(90)
```
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
weeks(3).ending_on("2000-01-21")
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
Represents a duration of time specified in calendar months.

Example usage:
```python
last_medication_date = medications.sort_by(medications.date).last_for_patient().date
start_date = last_medication_date - months(3)
end_date = last_medication_date + months(3)
```

Consider using [`days()`](#days) or [`weeks()`](#weeks) instead -
see the section on [Ambiguous Dates](#ambiguous-dates) for more.
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
weeks(3).ending_on("2000-01-21")
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
Represents a duration of time specified in weeks.

Example usage:
```python
last_medication_date = medications.sort_by(medications.date).last_for_patient().date
start_date = last_medication_date - weeks(12)
end_date = last_medication_date + weeks(12)
```
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
weeks(3).ending_on("2000-01-21")
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
Represents a duration of time specified in calendar years.

Example usage:
```python
last_medication_date = medications.sort_by(medications.date).last_for_patient().date
start_date = last_medication_date - years(1)
end_date = last_medication_date + years(1)
```

Consider using [`days()`](#days) or [`weeks()`](#weeks) instead -
see the section on [Ambiguous Dates](#ambiguous-dates) for more.
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
weeks(3).ending_on("2000-01-21")
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
