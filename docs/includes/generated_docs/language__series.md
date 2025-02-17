<h4 class="attr-heading" id="BoolPatientSeries" data-toc-label="BoolPatientSeries" markdown>
  <tt><em>class</em> <strong>BoolPatientSeries</strong>()</tt>
</h4>

<div markdown="block" class="indent">
One row per patient series of type `boolean`
<div class="attr-heading" id="BoolPatientSeries.eq">
  <tt><em>self</em> <strong>==</strong> <em>other</em></tt>
  <a class="headerlink" href="#BoolPatientSeries.eq" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series comparing each value in this series with its
corresponding value in `other`.

Note that the result of comparing anything with NULL (including NULL itself) is NULL.

Example usage:
```python
patients.sex == "female"
```
</div>

<div class="attr-heading" id="BoolPatientSeries.ne">
  <tt><em>self</em> <strong>!=</strong> <em>other</em></tt>
  <a class="headerlink" href="#BoolPatientSeries.ne" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `==` above.

Note that the same point regarding NULL applies here.

Example usage:
```python
patients.sex != "unknown"
```
</div>

<div class="attr-heading" id="BoolPatientSeries.and">
  <tt><em>self</em> <strong>&</strong> <em>other</em></tt>
  <a class="headerlink" href="#BoolPatientSeries.and" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Logical AND

Return a boolean series which is True where both this series and `other` are
True, False where either are False, and NULL otherwise.

Example usage:
```python
is_female_and_alive = patients.is_alive_on("2020-01-01") & patients.sex.is_in(["female"])
```
</div>

<div class="attr-heading" id="BoolPatientSeries.or">
  <tt><em>self</em> <strong>|</strong> <em>other</em></tt>
  <a class="headerlink" href="#BoolPatientSeries.or" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Logical OR

Return a boolean series which is True where either this series or `other` is
True, False where both are False, and NULL otherwise.

Example usage:
```python
is_alive = patients.date_of_death.is_null() | patients.date_of_death.is_after("2020-01-01")
```
Note that the above example is equivalent to `patients.is_alive_on("2020-01-01")`.
</div>

<div class="attr-heading" id="BoolPatientSeries.invert">
  <tt><em></em> <strong>~</strong> <em>self</em></tt>
  <a class="headerlink" href="#BoolPatientSeries.invert" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Logical NOT

Return a boolean series which is the inverse of this series i.e. where True
becomes False, False becomes True, and NULL stays as NULL.

Example usage:
```python
is_born_outside_period = ~ patients.date_of_birth.is_on_or_between("2020-03-01", "2020-06-30")
```
</div>

<div class="attr-heading" id="BoolPatientSeries.is_null">
  <tt><strong>is_null</strong>()</tt>
  <a class="headerlink" href="#BoolPatientSeries.is_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each NULL value in this
series and False for each non-NULL value.

Example usage:
```python
patients.date_of_death.is_null()
```
</div>

<div class="attr-heading" id="BoolPatientSeries.is_not_null">
  <tt><strong>is_not_null</strong>()</tt>
  <a class="headerlink" href="#BoolPatientSeries.is_not_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_null()` above.

Example usage:
```python
patients.date_of_death.is_not_null()
```
</div>

<div class="attr-heading" id="BoolPatientSeries.when_null_then">
  <tt><strong>when_null_then</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#BoolPatientSeries.when_null_then" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Replace any NULL value in this series with the corresponding value in `other`.

Note that `other` must be of the same type as this series.

Example usage:
```python
(patients.date_of_death < "2020-01-01").when_null_then(False)
```
</div>

<div class="attr-heading" id="BoolPatientSeries.is_in">
  <tt><strong>is_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#BoolPatientSeries.is_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series which is
contained in `other`.

See how to combine `is_in` with a codelist in
[the how-to guide](../how-to/examples.md/#does-each-patient-have-a-clinical-event-matching-a-code-in-a-codelist).

Example usage:
```python
medications.dmd_code.is_in(["39113311000001107", "39113611000001102"])
```

`other` accepts any of the standard "container" types (tuple, list, set, frozenset,
or dict) or another event series.
</div>

<div class="attr-heading" id="BoolPatientSeries.is_not_in">
  <tt><strong>is_not_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#BoolPatientSeries.is_not_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_in()` above.
</div>

<div class="attr-heading" id="BoolPatientSeries.map_values">
  <tt><strong>map_values</strong>(<em>mapping</em>, <em>default=None</em>)</tt>
  <a class="headerlink" href="#BoolPatientSeries.map_values" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a new series with _mapping_ applied to each value. _mapping_ should
be a dictionary mapping one set of values to another.

Example usage:
```python
school_year = patients.age_on("2020-09-01").map_values(
    {13: "Year 9", 14: "Year 10", 15: "Year 11"},
    default="N/A"
)
```
</div>

<div class="attr-heading" id="BoolPatientSeries.as_int">
  <tt><strong>as_int</strong>()</tt>
  <a class="headerlink" href="#BoolPatientSeries.as_int" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return each value in this Boolean series as 1 (True) or 0 (False).
</div>

</div>


<h4 class="attr-heading" id="BoolEventSeries" data-toc-label="BoolEventSeries" markdown>
  <tt><em>class</em> <strong>BoolEventSeries</strong>()</tt>
</h4>

<div markdown="block" class="indent">
Multiple rows per patient series of type `boolean`
<div class="attr-heading" id="BoolEventSeries.eq">
  <tt><em>self</em> <strong>==</strong> <em>other</em></tt>
  <a class="headerlink" href="#BoolEventSeries.eq" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series comparing each value in this series with its
corresponding value in `other`.

Note that the result of comparing anything with NULL (including NULL itself) is NULL.

Example usage:
```python
patients.sex == "female"
```
</div>

<div class="attr-heading" id="BoolEventSeries.ne">
  <tt><em>self</em> <strong>!=</strong> <em>other</em></tt>
  <a class="headerlink" href="#BoolEventSeries.ne" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `==` above.

Note that the same point regarding NULL applies here.

Example usage:
```python
patients.sex != "unknown"
```
</div>

<div class="attr-heading" id="BoolEventSeries.and">
  <tt><em>self</em> <strong>&</strong> <em>other</em></tt>
  <a class="headerlink" href="#BoolEventSeries.and" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Logical AND

Return a boolean series which is True where both this series and `other` are
True, False where either are False, and NULL otherwise.

Example usage:
```python
is_female_and_alive = patients.is_alive_on("2020-01-01") & patients.sex.is_in(["female"])
```
</div>

<div class="attr-heading" id="BoolEventSeries.or">
  <tt><em>self</em> <strong>|</strong> <em>other</em></tt>
  <a class="headerlink" href="#BoolEventSeries.or" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Logical OR

Return a boolean series which is True where either this series or `other` is
True, False where both are False, and NULL otherwise.

Example usage:
```python
is_alive = patients.date_of_death.is_null() | patients.date_of_death.is_after("2020-01-01")
```
Note that the above example is equivalent to `patients.is_alive_on("2020-01-01")`.
</div>

<div class="attr-heading" id="BoolEventSeries.invert">
  <tt><em></em> <strong>~</strong> <em>self</em></tt>
  <a class="headerlink" href="#BoolEventSeries.invert" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Logical NOT

Return a boolean series which is the inverse of this series i.e. where True
becomes False, False becomes True, and NULL stays as NULL.

Example usage:
```python
is_born_outside_period = ~ patients.date_of_birth.is_on_or_between("2020-03-01", "2020-06-30")
```
</div>

<div class="attr-heading" id="BoolEventSeries.is_null">
  <tt><strong>is_null</strong>()</tt>
  <a class="headerlink" href="#BoolEventSeries.is_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each NULL value in this
series and False for each non-NULL value.

Example usage:
```python
patients.date_of_death.is_null()
```
</div>

<div class="attr-heading" id="BoolEventSeries.is_not_null">
  <tt><strong>is_not_null</strong>()</tt>
  <a class="headerlink" href="#BoolEventSeries.is_not_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_null()` above.

Example usage:
```python
patients.date_of_death.is_not_null()
```
</div>

<div class="attr-heading" id="BoolEventSeries.when_null_then">
  <tt><strong>when_null_then</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#BoolEventSeries.when_null_then" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Replace any NULL value in this series with the corresponding value in `other`.

Note that `other` must be of the same type as this series.

Example usage:
```python
(patients.date_of_death < "2020-01-01").when_null_then(False)
```
</div>

<div class="attr-heading" id="BoolEventSeries.is_in">
  <tt><strong>is_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#BoolEventSeries.is_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series which is
contained in `other`.

See how to combine `is_in` with a codelist in
[the how-to guide](../how-to/examples.md/#does-each-patient-have-a-clinical-event-matching-a-code-in-a-codelist).

Example usage:
```python
medications.dmd_code.is_in(["39113311000001107", "39113611000001102"])
```

`other` accepts any of the standard "container" types (tuple, list, set, frozenset,
or dict) or another event series.
</div>

<div class="attr-heading" id="BoolEventSeries.is_not_in">
  <tt><strong>is_not_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#BoolEventSeries.is_not_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_in()` above.
</div>

<div class="attr-heading" id="BoolEventSeries.map_values">
  <tt><strong>map_values</strong>(<em>mapping</em>, <em>default=None</em>)</tt>
  <a class="headerlink" href="#BoolEventSeries.map_values" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a new series with _mapping_ applied to each value. _mapping_ should
be a dictionary mapping one set of values to another.

Example usage:
```python
school_year = patients.age_on("2020-09-01").map_values(
    {13: "Year 9", 14: "Year 10", 15: "Year 11"},
    default="N/A"
)
```
</div>

<div class="attr-heading" id="BoolEventSeries.as_int">
  <tt><strong>as_int</strong>()</tt>
  <a class="headerlink" href="#BoolEventSeries.as_int" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return each value in this Boolean series as 1 (True) or 0 (False).
</div>

<div class="attr-heading" id="BoolEventSeries.count_distinct_for_patient">
  <tt><strong>count_distinct_for_patient</strong>()</tt>
  <a class="headerlink" href="#BoolEventSeries.count_distinct_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return an [integer patient series](#IntPatientSeries) counting the number of
distinct values for each patient in the series (ignoring any NULL values).

Note that if a patient has no values at all in the series the result will
be zero rather than NULL.

Example usage:
```python
medications.dmd_code.count_distinct_for_patient()
```
</div>

</div>


<h4 class="attr-heading" id="StrPatientSeries" data-toc-label="StrPatientSeries" markdown>
  <tt><em>class</em> <strong>StrPatientSeries</strong>()</tt>
</h4>

<div markdown="block" class="indent">
One row per patient series of type `string`
<div class="attr-heading" id="StrPatientSeries.eq">
  <tt><em>self</em> <strong>==</strong> <em>other</em></tt>
  <a class="headerlink" href="#StrPatientSeries.eq" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series comparing each value in this series with its
corresponding value in `other`.

Note that the result of comparing anything with NULL (including NULL itself) is NULL.

Example usage:
```python
patients.sex == "female"
```
</div>

<div class="attr-heading" id="StrPatientSeries.ne">
  <tt><em>self</em> <strong>!=</strong> <em>other</em></tt>
  <a class="headerlink" href="#StrPatientSeries.ne" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `==` above.

Note that the same point regarding NULL applies here.

Example usage:
```python
patients.sex != "unknown"
```
</div>

<div class="attr-heading" id="StrPatientSeries.lt">
  <tt><em>self</em> <strong>></strong> <em>other</em></tt>
  <a class="headerlink" href="#StrPatientSeries.lt" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
strictly less than its corresponding value in `other` and False otherwise (or NULL
if either value is NULL).

Example usage:
```python
is_underage = patients.age_on("2020-01-01") < 18
```
</div>

<div class="attr-heading" id="StrPatientSeries.le">
  <tt><em>self</em> <strong>>=</strong> <em>other</em></tt>
  <a class="headerlink" href="#StrPatientSeries.le" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is less
than or equal to its corresponding value in `other` and False otherwise (or NULL
if either value is NULL).

Example usage:
```python
is_underage = patients.age_on("2020-01-01") <= 17
```
</div>

<div class="attr-heading" id="StrPatientSeries.ge">
  <tt><em>self</em> <strong><=</strong> <em>other</em></tt>
  <a class="headerlink" href="#StrPatientSeries.ge" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
greater than or equal to its corresponding value in `other` and False otherwise
(or NULL if either value is NULL).

Example usage:
```python
is_adult = patients.age_on("2020-01-01") >= 18
```
</div>

<div class="attr-heading" id="StrPatientSeries.gt">
  <tt><em>self</em> <strong><</strong> <em>other</em></tt>
  <a class="headerlink" href="#StrPatientSeries.gt" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
strictly greater than its corresponding value in `other` and False otherwise (or
NULL if either value is NULL).

Example usage:
```python
is_adult = patients.age_on("2020-01-01") > 17
```
</div>

<div class="attr-heading" id="StrPatientSeries.is_null">
  <tt><strong>is_null</strong>()</tt>
  <a class="headerlink" href="#StrPatientSeries.is_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each NULL value in this
series and False for each non-NULL value.

Example usage:
```python
patients.date_of_death.is_null()
```
</div>

<div class="attr-heading" id="StrPatientSeries.is_not_null">
  <tt><strong>is_not_null</strong>()</tt>
  <a class="headerlink" href="#StrPatientSeries.is_not_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_null()` above.

Example usage:
```python
patients.date_of_death.is_not_null()
```
</div>

<div class="attr-heading" id="StrPatientSeries.when_null_then">
  <tt><strong>when_null_then</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#StrPatientSeries.when_null_then" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Replace any NULL value in this series with the corresponding value in `other`.

Note that `other` must be of the same type as this series.

Example usage:
```python
(patients.date_of_death < "2020-01-01").when_null_then(False)
```
</div>

<div class="attr-heading" id="StrPatientSeries.is_in">
  <tt><strong>is_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#StrPatientSeries.is_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series which is
contained in `other`.

See how to combine `is_in` with a codelist in
[the how-to guide](../how-to/examples.md/#does-each-patient-have-a-clinical-event-matching-a-code-in-a-codelist).

Example usage:
```python
medications.dmd_code.is_in(["39113311000001107", "39113611000001102"])
```

`other` accepts any of the standard "container" types (tuple, list, set, frozenset,
or dict) or another event series.
</div>

<div class="attr-heading" id="StrPatientSeries.is_not_in">
  <tt><strong>is_not_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#StrPatientSeries.is_not_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_in()` above.
</div>

<div class="attr-heading" id="StrPatientSeries.map_values">
  <tt><strong>map_values</strong>(<em>mapping</em>, <em>default=None</em>)</tt>
  <a class="headerlink" href="#StrPatientSeries.map_values" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a new series with _mapping_ applied to each value. _mapping_ should
be a dictionary mapping one set of values to another.

Example usage:
```python
school_year = patients.age_on("2020-09-01").map_values(
    {13: "Year 9", 14: "Year 10", 15: "Year 11"},
    default="N/A"
)
```
</div>

<div class="attr-heading" id="StrPatientSeries.contains">
  <tt><strong>contains</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#StrPatientSeries.contains" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each string in this series which
contains `other` as a sub-string and False otherwise. For NULL values, the
result is NULL.

Example usage:
```python
is_female = patients.sex.contains("fem")
```

`other` can be another string series, in which case corresponding values
are compared. If either value is NULL the result is NULL.
</div>

</div>


<h4 class="attr-heading" id="StrEventSeries" data-toc-label="StrEventSeries" markdown>
  <tt><em>class</em> <strong>StrEventSeries</strong>()</tt>
</h4>

<div markdown="block" class="indent">
Multiple rows per patient series of type `string`
<div class="attr-heading" id="StrEventSeries.eq">
  <tt><em>self</em> <strong>==</strong> <em>other</em></tt>
  <a class="headerlink" href="#StrEventSeries.eq" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series comparing each value in this series with its
corresponding value in `other`.

Note that the result of comparing anything with NULL (including NULL itself) is NULL.

Example usage:
```python
patients.sex == "female"
```
</div>

<div class="attr-heading" id="StrEventSeries.ne">
  <tt><em>self</em> <strong>!=</strong> <em>other</em></tt>
  <a class="headerlink" href="#StrEventSeries.ne" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `==` above.

Note that the same point regarding NULL applies here.

Example usage:
```python
patients.sex != "unknown"
```
</div>

<div class="attr-heading" id="StrEventSeries.lt">
  <tt><em>self</em> <strong>></strong> <em>other</em></tt>
  <a class="headerlink" href="#StrEventSeries.lt" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
strictly less than its corresponding value in `other` and False otherwise (or NULL
if either value is NULL).

Example usage:
```python
is_underage = patients.age_on("2020-01-01") < 18
```
</div>

<div class="attr-heading" id="StrEventSeries.le">
  <tt><em>self</em> <strong>>=</strong> <em>other</em></tt>
  <a class="headerlink" href="#StrEventSeries.le" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is less
than or equal to its corresponding value in `other` and False otherwise (or NULL
if either value is NULL).

Example usage:
```python
is_underage = patients.age_on("2020-01-01") <= 17
```
</div>

<div class="attr-heading" id="StrEventSeries.ge">
  <tt><em>self</em> <strong><=</strong> <em>other</em></tt>
  <a class="headerlink" href="#StrEventSeries.ge" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
greater than or equal to its corresponding value in `other` and False otherwise
(or NULL if either value is NULL).

Example usage:
```python
is_adult = patients.age_on("2020-01-01") >= 18
```
</div>

<div class="attr-heading" id="StrEventSeries.gt">
  <tt><em>self</em> <strong><</strong> <em>other</em></tt>
  <a class="headerlink" href="#StrEventSeries.gt" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
strictly greater than its corresponding value in `other` and False otherwise (or
NULL if either value is NULL).

Example usage:
```python
is_adult = patients.age_on("2020-01-01") > 17
```
</div>

<div class="attr-heading" id="StrEventSeries.is_null">
  <tt><strong>is_null</strong>()</tt>
  <a class="headerlink" href="#StrEventSeries.is_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each NULL value in this
series and False for each non-NULL value.

Example usage:
```python
patients.date_of_death.is_null()
```
</div>

<div class="attr-heading" id="StrEventSeries.is_not_null">
  <tt><strong>is_not_null</strong>()</tt>
  <a class="headerlink" href="#StrEventSeries.is_not_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_null()` above.

Example usage:
```python
patients.date_of_death.is_not_null()
```
</div>

<div class="attr-heading" id="StrEventSeries.when_null_then">
  <tt><strong>when_null_then</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#StrEventSeries.when_null_then" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Replace any NULL value in this series with the corresponding value in `other`.

Note that `other` must be of the same type as this series.

Example usage:
```python
(patients.date_of_death < "2020-01-01").when_null_then(False)
```
</div>

<div class="attr-heading" id="StrEventSeries.is_in">
  <tt><strong>is_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#StrEventSeries.is_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series which is
contained in `other`.

See how to combine `is_in` with a codelist in
[the how-to guide](../how-to/examples.md/#does-each-patient-have-a-clinical-event-matching-a-code-in-a-codelist).

Example usage:
```python
medications.dmd_code.is_in(["39113311000001107", "39113611000001102"])
```

`other` accepts any of the standard "container" types (tuple, list, set, frozenset,
or dict) or another event series.
</div>

<div class="attr-heading" id="StrEventSeries.is_not_in">
  <tt><strong>is_not_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#StrEventSeries.is_not_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_in()` above.
</div>

<div class="attr-heading" id="StrEventSeries.map_values">
  <tt><strong>map_values</strong>(<em>mapping</em>, <em>default=None</em>)</tt>
  <a class="headerlink" href="#StrEventSeries.map_values" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a new series with _mapping_ applied to each value. _mapping_ should
be a dictionary mapping one set of values to another.

Example usage:
```python
school_year = patients.age_on("2020-09-01").map_values(
    {13: "Year 9", 14: "Year 10", 15: "Year 11"},
    default="N/A"
)
```
</div>

<div class="attr-heading" id="StrEventSeries.contains">
  <tt><strong>contains</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#StrEventSeries.contains" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each string in this series which
contains `other` as a sub-string and False otherwise. For NULL values, the
result is NULL.

Example usage:
```python
is_female = patients.sex.contains("fem")
```

`other` can be another string series, in which case corresponding values
are compared. If either value is NULL the result is NULL.
</div>

<div class="attr-heading" id="StrEventSeries.count_distinct_for_patient">
  <tt><strong>count_distinct_for_patient</strong>()</tt>
  <a class="headerlink" href="#StrEventSeries.count_distinct_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return an [integer patient series](#IntPatientSeries) counting the number of
distinct values for each patient in the series (ignoring any NULL values).

Note that if a patient has no values at all in the series the result will
be zero rather than NULL.

Example usage:
```python
medications.dmd_code.count_distinct_for_patient()
```
</div>

<div class="attr-heading" id="StrEventSeries.minimum_for_patient">
  <tt><strong>minimum_for_patient</strong>()</tt>
  <a class="headerlink" href="#StrEventSeries.minimum_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the minimum value in the series for each patient (or NULL if the patient
has no values).

Example usage:
```python
clinical_events.where(...).numeric_value.minimum_for_patient()
```
</div>

<div class="attr-heading" id="StrEventSeries.maximum_for_patient">
  <tt><strong>maximum_for_patient</strong>()</tt>
  <a class="headerlink" href="#StrEventSeries.maximum_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the maximum value in the series for each patient (or NULL if the patient
has no values).

Example usage:
```python
clinical_events.where(...).numeric_value.maximum_for_patient()
```
</div>

</div>


<h4 class="attr-heading" id="IntPatientSeries" data-toc-label="IntPatientSeries" markdown>
  <tt><em>class</em> <strong>IntPatientSeries</strong>()</tt>
</h4>

<div markdown="block" class="indent">
One row per patient series of type `integer`
<div class="attr-heading" id="IntPatientSeries.eq">
  <tt><em>self</em> <strong>==</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntPatientSeries.eq" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series comparing each value in this series with its
corresponding value in `other`.

Note that the result of comparing anything with NULL (including NULL itself) is NULL.

Example usage:
```python
patients.sex == "female"
```
</div>

<div class="attr-heading" id="IntPatientSeries.ne">
  <tt><em>self</em> <strong>!=</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntPatientSeries.ne" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `==` above.

Note that the same point regarding NULL applies here.

Example usage:
```python
patients.sex != "unknown"
```
</div>

<div class="attr-heading" id="IntPatientSeries.lt">
  <tt><em>self</em> <strong>></strong> <em>other</em></tt>
  <a class="headerlink" href="#IntPatientSeries.lt" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
strictly less than its corresponding value in `other` and False otherwise (or NULL
if either value is NULL).

Example usage:
```python
is_underage = patients.age_on("2020-01-01") < 18
```
</div>

<div class="attr-heading" id="IntPatientSeries.le">
  <tt><em>self</em> <strong>>=</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntPatientSeries.le" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is less
than or equal to its corresponding value in `other` and False otherwise (or NULL
if either value is NULL).

Example usage:
```python
is_underage = patients.age_on("2020-01-01") <= 17
```
</div>

<div class="attr-heading" id="IntPatientSeries.ge">
  <tt><em>self</em> <strong><=</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntPatientSeries.ge" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
greater than or equal to its corresponding value in `other` and False otherwise
(or NULL if either value is NULL).

Example usage:
```python
is_adult = patients.age_on("2020-01-01") >= 18
```
</div>

<div class="attr-heading" id="IntPatientSeries.gt">
  <tt><em>self</em> <strong><</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntPatientSeries.gt" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
strictly greater than its corresponding value in `other` and False otherwise (or
NULL if either value is NULL).

Example usage:
```python
is_adult = patients.age_on("2020-01-01") > 17
```
</div>

<div class="attr-heading" id="IntPatientSeries.add">
  <tt><em>self</em> <strong>+</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntPatientSeries.add" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the sum of each corresponding value in this series and `other` (or NULL
if either is NULL).
</div>

<div class="attr-heading" id="IntPatientSeries.sub">
  <tt><em>self</em> <strong>-</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntPatientSeries.sub" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return each value in this series with its corresponding value in `other`
subtracted (or NULL if either is NULL).
</div>

<div class="attr-heading" id="IntPatientSeries.mul">
  <tt><em>self</em> <strong>*</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntPatientSeries.mul" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the product of each corresponding value in this series and `other` (or
NULL if either is NULL).
</div>

<div class="attr-heading" id="IntPatientSeries.truediv">
  <tt><em>self</em> <strong>/</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntPatientSeries.truediv" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a series with each value in this series divided by its correponding value
in `other` (or NULL if either is NULL).

Note that the result is always if a float even if the inputs are integers.
</div>

<div class="attr-heading" id="IntPatientSeries.floordiv">
  <tt><em>self</em> <strong>//</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntPatientSeries.floordiv" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a series with each value in this series divided by its correponding value
in `other` and then rounded **down** to the nearest integer value (or NULL if either
is NULL).

Note that the result is always if an integer even if the inputs are floats.
</div>

<div class="attr-heading" id="IntPatientSeries.neg">
  <tt><em></em> <strong>-</strong> <em>self</em></tt>
  <a class="headerlink" href="#IntPatientSeries.neg" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the negation of each value in this series.
</div>

<div class="attr-heading" id="IntPatientSeries.is_null">
  <tt><strong>is_null</strong>()</tt>
  <a class="headerlink" href="#IntPatientSeries.is_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each NULL value in this
series and False for each non-NULL value.

Example usage:
```python
patients.date_of_death.is_null()
```
</div>

<div class="attr-heading" id="IntPatientSeries.is_not_null">
  <tt><strong>is_not_null</strong>()</tt>
  <a class="headerlink" href="#IntPatientSeries.is_not_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_null()` above.

Example usage:
```python
patients.date_of_death.is_not_null()
```
</div>

<div class="attr-heading" id="IntPatientSeries.when_null_then">
  <tt><strong>when_null_then</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#IntPatientSeries.when_null_then" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Replace any NULL value in this series with the corresponding value in `other`.

Note that `other` must be of the same type as this series.

Example usage:
```python
(patients.date_of_death < "2020-01-01").when_null_then(False)
```
</div>

<div class="attr-heading" id="IntPatientSeries.is_in">
  <tt><strong>is_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#IntPatientSeries.is_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series which is
contained in `other`.

See how to combine `is_in` with a codelist in
[the how-to guide](../how-to/examples.md/#does-each-patient-have-a-clinical-event-matching-a-code-in-a-codelist).

Example usage:
```python
medications.dmd_code.is_in(["39113311000001107", "39113611000001102"])
```

`other` accepts any of the standard "container" types (tuple, list, set, frozenset,
or dict) or another event series.
</div>

<div class="attr-heading" id="IntPatientSeries.is_not_in">
  <tt><strong>is_not_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#IntPatientSeries.is_not_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_in()` above.
</div>

<div class="attr-heading" id="IntPatientSeries.map_values">
  <tt><strong>map_values</strong>(<em>mapping</em>, <em>default=None</em>)</tt>
  <a class="headerlink" href="#IntPatientSeries.map_values" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a new series with _mapping_ applied to each value. _mapping_ should
be a dictionary mapping one set of values to another.

Example usage:
```python
school_year = patients.age_on("2020-09-01").map_values(
    {13: "Year 9", 14: "Year 10", 15: "Year 11"},
    default="N/A"
)
```
</div>

<div class="attr-heading" id="IntPatientSeries.as_int">
  <tt><strong>as_int</strong>()</tt>
  <a class="headerlink" href="#IntPatientSeries.as_int" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return each value in this series rounded down to the nearest integer.
</div>

<div class="attr-heading" id="IntPatientSeries.as_float">
  <tt><strong>as_float</strong>()</tt>
  <a class="headerlink" href="#IntPatientSeries.as_float" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return each value in this series as a float (e.g. 10 becomes 10.0).
</div>

</div>


<h4 class="attr-heading" id="IntEventSeries" data-toc-label="IntEventSeries" markdown>
  <tt><em>class</em> <strong>IntEventSeries</strong>()</tt>
</h4>

<div markdown="block" class="indent">
Multiple rows per patient series of type `integer`
<div class="attr-heading" id="IntEventSeries.eq">
  <tt><em>self</em> <strong>==</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntEventSeries.eq" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series comparing each value in this series with its
corresponding value in `other`.

Note that the result of comparing anything with NULL (including NULL itself) is NULL.

Example usage:
```python
patients.sex == "female"
```
</div>

<div class="attr-heading" id="IntEventSeries.ne">
  <tt><em>self</em> <strong>!=</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntEventSeries.ne" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `==` above.

Note that the same point regarding NULL applies here.

Example usage:
```python
patients.sex != "unknown"
```
</div>

<div class="attr-heading" id="IntEventSeries.lt">
  <tt><em>self</em> <strong>></strong> <em>other</em></tt>
  <a class="headerlink" href="#IntEventSeries.lt" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
strictly less than its corresponding value in `other` and False otherwise (or NULL
if either value is NULL).

Example usage:
```python
is_underage = patients.age_on("2020-01-01") < 18
```
</div>

<div class="attr-heading" id="IntEventSeries.le">
  <tt><em>self</em> <strong>>=</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntEventSeries.le" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is less
than or equal to its corresponding value in `other` and False otherwise (or NULL
if either value is NULL).

Example usage:
```python
is_underage = patients.age_on("2020-01-01") <= 17
```
</div>

<div class="attr-heading" id="IntEventSeries.ge">
  <tt><em>self</em> <strong><=</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntEventSeries.ge" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
greater than or equal to its corresponding value in `other` and False otherwise
(or NULL if either value is NULL).

Example usage:
```python
is_adult = patients.age_on("2020-01-01") >= 18
```
</div>

<div class="attr-heading" id="IntEventSeries.gt">
  <tt><em>self</em> <strong><</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntEventSeries.gt" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
strictly greater than its corresponding value in `other` and False otherwise (or
NULL if either value is NULL).

Example usage:
```python
is_adult = patients.age_on("2020-01-01") > 17
```
</div>

<div class="attr-heading" id="IntEventSeries.add">
  <tt><em>self</em> <strong>+</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntEventSeries.add" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the sum of each corresponding value in this series and `other` (or NULL
if either is NULL).
</div>

<div class="attr-heading" id="IntEventSeries.sub">
  <tt><em>self</em> <strong>-</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntEventSeries.sub" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return each value in this series with its corresponding value in `other`
subtracted (or NULL if either is NULL).
</div>

<div class="attr-heading" id="IntEventSeries.mul">
  <tt><em>self</em> <strong>*</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntEventSeries.mul" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the product of each corresponding value in this series and `other` (or
NULL if either is NULL).
</div>

<div class="attr-heading" id="IntEventSeries.truediv">
  <tt><em>self</em> <strong>/</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntEventSeries.truediv" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a series with each value in this series divided by its correponding value
in `other` (or NULL if either is NULL).

Note that the result is always if a float even if the inputs are integers.
</div>

<div class="attr-heading" id="IntEventSeries.floordiv">
  <tt><em>self</em> <strong>//</strong> <em>other</em></tt>
  <a class="headerlink" href="#IntEventSeries.floordiv" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a series with each value in this series divided by its correponding value
in `other` and then rounded **down** to the nearest integer value (or NULL if either
is NULL).

Note that the result is always if an integer even if the inputs are floats.
</div>

<div class="attr-heading" id="IntEventSeries.neg">
  <tt><em></em> <strong>-</strong> <em>self</em></tt>
  <a class="headerlink" href="#IntEventSeries.neg" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the negation of each value in this series.
</div>

<div class="attr-heading" id="IntEventSeries.is_null">
  <tt><strong>is_null</strong>()</tt>
  <a class="headerlink" href="#IntEventSeries.is_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each NULL value in this
series and False for each non-NULL value.

Example usage:
```python
patients.date_of_death.is_null()
```
</div>

<div class="attr-heading" id="IntEventSeries.is_not_null">
  <tt><strong>is_not_null</strong>()</tt>
  <a class="headerlink" href="#IntEventSeries.is_not_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_null()` above.

Example usage:
```python
patients.date_of_death.is_not_null()
```
</div>

<div class="attr-heading" id="IntEventSeries.when_null_then">
  <tt><strong>when_null_then</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#IntEventSeries.when_null_then" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Replace any NULL value in this series with the corresponding value in `other`.

Note that `other` must be of the same type as this series.

Example usage:
```python
(patients.date_of_death < "2020-01-01").when_null_then(False)
```
</div>

<div class="attr-heading" id="IntEventSeries.is_in">
  <tt><strong>is_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#IntEventSeries.is_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series which is
contained in `other`.

See how to combine `is_in` with a codelist in
[the how-to guide](../how-to/examples.md/#does-each-patient-have-a-clinical-event-matching-a-code-in-a-codelist).

Example usage:
```python
medications.dmd_code.is_in(["39113311000001107", "39113611000001102"])
```

`other` accepts any of the standard "container" types (tuple, list, set, frozenset,
or dict) or another event series.
</div>

<div class="attr-heading" id="IntEventSeries.is_not_in">
  <tt><strong>is_not_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#IntEventSeries.is_not_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_in()` above.
</div>

<div class="attr-heading" id="IntEventSeries.map_values">
  <tt><strong>map_values</strong>(<em>mapping</em>, <em>default=None</em>)</tt>
  <a class="headerlink" href="#IntEventSeries.map_values" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a new series with _mapping_ applied to each value. _mapping_ should
be a dictionary mapping one set of values to another.

Example usage:
```python
school_year = patients.age_on("2020-09-01").map_values(
    {13: "Year 9", 14: "Year 10", 15: "Year 11"},
    default="N/A"
)
```
</div>

<div class="attr-heading" id="IntEventSeries.as_int">
  <tt><strong>as_int</strong>()</tt>
  <a class="headerlink" href="#IntEventSeries.as_int" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return each value in this series rounded down to the nearest integer.
</div>

<div class="attr-heading" id="IntEventSeries.as_float">
  <tt><strong>as_float</strong>()</tt>
  <a class="headerlink" href="#IntEventSeries.as_float" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return each value in this series as a float (e.g. 10 becomes 10.0).
</div>

<div class="attr-heading" id="IntEventSeries.count_distinct_for_patient">
  <tt><strong>count_distinct_for_patient</strong>()</tt>
  <a class="headerlink" href="#IntEventSeries.count_distinct_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return an [integer patient series](#IntPatientSeries) counting the number of
distinct values for each patient in the series (ignoring any NULL values).

Note that if a patient has no values at all in the series the result will
be zero rather than NULL.

Example usage:
```python
medications.dmd_code.count_distinct_for_patient()
```
</div>

<div class="attr-heading" id="IntEventSeries.minimum_for_patient">
  <tt><strong>minimum_for_patient</strong>()</tt>
  <a class="headerlink" href="#IntEventSeries.minimum_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the minimum value in the series for each patient (or NULL if the patient
has no values).

Example usage:
```python
clinical_events.where(...).numeric_value.minimum_for_patient()
```
</div>

<div class="attr-heading" id="IntEventSeries.maximum_for_patient">
  <tt><strong>maximum_for_patient</strong>()</tt>
  <a class="headerlink" href="#IntEventSeries.maximum_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the maximum value in the series for each patient (or NULL if the patient
has no values).

Example usage:
```python
clinical_events.where(...).numeric_value.maximum_for_patient()
```
</div>

<div class="attr-heading" id="IntEventSeries.sum_for_patient">
  <tt><strong>sum_for_patient</strong>()</tt>
  <a class="headerlink" href="#IntEventSeries.sum_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the sum of all values in the series for each patient.
</div>

<div class="attr-heading" id="IntEventSeries.mean_for_patient">
  <tt><strong>mean_for_patient</strong>()</tt>
  <a class="headerlink" href="#IntEventSeries.mean_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the arithmetic mean of any non-NULL values in the series for each
patient.
</div>

</div>


<h4 class="attr-heading" id="FloatPatientSeries" data-toc-label="FloatPatientSeries" markdown>
  <tt><em>class</em> <strong>FloatPatientSeries</strong>()</tt>
</h4>

<div markdown="block" class="indent">
One row per patient series of type `float`
<div class="attr-heading" id="FloatPatientSeries.eq">
  <tt><em>self</em> <strong>==</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatPatientSeries.eq" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series comparing each value in this series with its
corresponding value in `other`.

Note that the result of comparing anything with NULL (including NULL itself) is NULL.

Example usage:
```python
patients.sex == "female"
```
</div>

<div class="attr-heading" id="FloatPatientSeries.ne">
  <tt><em>self</em> <strong>!=</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatPatientSeries.ne" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `==` above.

Note that the same point regarding NULL applies here.

Example usage:
```python
patients.sex != "unknown"
```
</div>

<div class="attr-heading" id="FloatPatientSeries.lt">
  <tt><em>self</em> <strong>></strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatPatientSeries.lt" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
strictly less than its corresponding value in `other` and False otherwise (or NULL
if either value is NULL).

Example usage:
```python
is_underage = patients.age_on("2020-01-01") < 18
```
</div>

<div class="attr-heading" id="FloatPatientSeries.le">
  <tt><em>self</em> <strong>>=</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatPatientSeries.le" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is less
than or equal to its corresponding value in `other` and False otherwise (or NULL
if either value is NULL).

Example usage:
```python
is_underage = patients.age_on("2020-01-01") <= 17
```
</div>

<div class="attr-heading" id="FloatPatientSeries.ge">
  <tt><em>self</em> <strong><=</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatPatientSeries.ge" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
greater than or equal to its corresponding value in `other` and False otherwise
(or NULL if either value is NULL).

Example usage:
```python
is_adult = patients.age_on("2020-01-01") >= 18
```
</div>

<div class="attr-heading" id="FloatPatientSeries.gt">
  <tt><em>self</em> <strong><</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatPatientSeries.gt" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
strictly greater than its corresponding value in `other` and False otherwise (or
NULL if either value is NULL).

Example usage:
```python
is_adult = patients.age_on("2020-01-01") > 17
```
</div>

<div class="attr-heading" id="FloatPatientSeries.add">
  <tt><em>self</em> <strong>+</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatPatientSeries.add" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the sum of each corresponding value in this series and `other` (or NULL
if either is NULL).
</div>

<div class="attr-heading" id="FloatPatientSeries.sub">
  <tt><em>self</em> <strong>-</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatPatientSeries.sub" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return each value in this series with its corresponding value in `other`
subtracted (or NULL if either is NULL).
</div>

<div class="attr-heading" id="FloatPatientSeries.mul">
  <tt><em>self</em> <strong>*</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatPatientSeries.mul" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the product of each corresponding value in this series and `other` (or
NULL if either is NULL).
</div>

<div class="attr-heading" id="FloatPatientSeries.truediv">
  <tt><em>self</em> <strong>/</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatPatientSeries.truediv" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a series with each value in this series divided by its correponding value
in `other` (or NULL if either is NULL).

Note that the result is always if a float even if the inputs are integers.
</div>

<div class="attr-heading" id="FloatPatientSeries.floordiv">
  <tt><em>self</em> <strong>//</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatPatientSeries.floordiv" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a series with each value in this series divided by its correponding value
in `other` and then rounded **down** to the nearest integer value (or NULL if either
is NULL).

Note that the result is always if an integer even if the inputs are floats.
</div>

<div class="attr-heading" id="FloatPatientSeries.neg">
  <tt><em></em> <strong>-</strong> <em>self</em></tt>
  <a class="headerlink" href="#FloatPatientSeries.neg" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the negation of each value in this series.
</div>

<div class="attr-heading" id="FloatPatientSeries.is_null">
  <tt><strong>is_null</strong>()</tt>
  <a class="headerlink" href="#FloatPatientSeries.is_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each NULL value in this
series and False for each non-NULL value.

Example usage:
```python
patients.date_of_death.is_null()
```
</div>

<div class="attr-heading" id="FloatPatientSeries.is_not_null">
  <tt><strong>is_not_null</strong>()</tt>
  <a class="headerlink" href="#FloatPatientSeries.is_not_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_null()` above.

Example usage:
```python
patients.date_of_death.is_not_null()
```
</div>

<div class="attr-heading" id="FloatPatientSeries.when_null_then">
  <tt><strong>when_null_then</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#FloatPatientSeries.when_null_then" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Replace any NULL value in this series with the corresponding value in `other`.

Note that `other` must be of the same type as this series.

Example usage:
```python
(patients.date_of_death < "2020-01-01").when_null_then(False)
```
</div>

<div class="attr-heading" id="FloatPatientSeries.is_in">
  <tt><strong>is_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#FloatPatientSeries.is_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series which is
contained in `other`.

See how to combine `is_in` with a codelist in
[the how-to guide](../how-to/examples.md/#does-each-patient-have-a-clinical-event-matching-a-code-in-a-codelist).

Example usage:
```python
medications.dmd_code.is_in(["39113311000001107", "39113611000001102"])
```

`other` accepts any of the standard "container" types (tuple, list, set, frozenset,
or dict) or another event series.
</div>

<div class="attr-heading" id="FloatPatientSeries.is_not_in">
  <tt><strong>is_not_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#FloatPatientSeries.is_not_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_in()` above.
</div>

<div class="attr-heading" id="FloatPatientSeries.map_values">
  <tt><strong>map_values</strong>(<em>mapping</em>, <em>default=None</em>)</tt>
  <a class="headerlink" href="#FloatPatientSeries.map_values" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a new series with _mapping_ applied to each value. _mapping_ should
be a dictionary mapping one set of values to another.

Example usage:
```python
school_year = patients.age_on("2020-09-01").map_values(
    {13: "Year 9", 14: "Year 10", 15: "Year 11"},
    default="N/A"
)
```
</div>

<div class="attr-heading" id="FloatPatientSeries.as_int">
  <tt><strong>as_int</strong>()</tt>
  <a class="headerlink" href="#FloatPatientSeries.as_int" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return each value in this series rounded down to the nearest integer.
</div>

<div class="attr-heading" id="FloatPatientSeries.as_float">
  <tt><strong>as_float</strong>()</tt>
  <a class="headerlink" href="#FloatPatientSeries.as_float" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return each value in this series as a float (e.g. 10 becomes 10.0).
</div>

</div>


<h4 class="attr-heading" id="FloatEventSeries" data-toc-label="FloatEventSeries" markdown>
  <tt><em>class</em> <strong>FloatEventSeries</strong>()</tt>
</h4>

<div markdown="block" class="indent">
Multiple rows per patient series of type `float`
<div class="attr-heading" id="FloatEventSeries.eq">
  <tt><em>self</em> <strong>==</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatEventSeries.eq" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series comparing each value in this series with its
corresponding value in `other`.

Note that the result of comparing anything with NULL (including NULL itself) is NULL.

Example usage:
```python
patients.sex == "female"
```
</div>

<div class="attr-heading" id="FloatEventSeries.ne">
  <tt><em>self</em> <strong>!=</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatEventSeries.ne" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `==` above.

Note that the same point regarding NULL applies here.

Example usage:
```python
patients.sex != "unknown"
```
</div>

<div class="attr-heading" id="FloatEventSeries.lt">
  <tt><em>self</em> <strong>></strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatEventSeries.lt" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
strictly less than its corresponding value in `other` and False otherwise (or NULL
if either value is NULL).

Example usage:
```python
is_underage = patients.age_on("2020-01-01") < 18
```
</div>

<div class="attr-heading" id="FloatEventSeries.le">
  <tt><em>self</em> <strong>>=</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatEventSeries.le" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is less
than or equal to its corresponding value in `other` and False otherwise (or NULL
if either value is NULL).

Example usage:
```python
is_underage = patients.age_on("2020-01-01") <= 17
```
</div>

<div class="attr-heading" id="FloatEventSeries.ge">
  <tt><em>self</em> <strong><=</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatEventSeries.ge" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
greater than or equal to its corresponding value in `other` and False otherwise
(or NULL if either value is NULL).

Example usage:
```python
is_adult = patients.age_on("2020-01-01") >= 18
```
</div>

<div class="attr-heading" id="FloatEventSeries.gt">
  <tt><em>self</em> <strong><</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatEventSeries.gt" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
strictly greater than its corresponding value in `other` and False otherwise (or
NULL if either value is NULL).

Example usage:
```python
is_adult = patients.age_on("2020-01-01") > 17
```
</div>

<div class="attr-heading" id="FloatEventSeries.add">
  <tt><em>self</em> <strong>+</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatEventSeries.add" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the sum of each corresponding value in this series and `other` (or NULL
if either is NULL).
</div>

<div class="attr-heading" id="FloatEventSeries.sub">
  <tt><em>self</em> <strong>-</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatEventSeries.sub" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return each value in this series with its corresponding value in `other`
subtracted (or NULL if either is NULL).
</div>

<div class="attr-heading" id="FloatEventSeries.mul">
  <tt><em>self</em> <strong>*</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatEventSeries.mul" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the product of each corresponding value in this series and `other` (or
NULL if either is NULL).
</div>

<div class="attr-heading" id="FloatEventSeries.truediv">
  <tt><em>self</em> <strong>/</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatEventSeries.truediv" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a series with each value in this series divided by its correponding value
in `other` (or NULL if either is NULL).

Note that the result is always if a float even if the inputs are integers.
</div>

<div class="attr-heading" id="FloatEventSeries.floordiv">
  <tt><em>self</em> <strong>//</strong> <em>other</em></tt>
  <a class="headerlink" href="#FloatEventSeries.floordiv" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a series with each value in this series divided by its correponding value
in `other` and then rounded **down** to the nearest integer value (or NULL if either
is NULL).

Note that the result is always if an integer even if the inputs are floats.
</div>

<div class="attr-heading" id="FloatEventSeries.neg">
  <tt><em></em> <strong>-</strong> <em>self</em></tt>
  <a class="headerlink" href="#FloatEventSeries.neg" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the negation of each value in this series.
</div>

<div class="attr-heading" id="FloatEventSeries.is_null">
  <tt><strong>is_null</strong>()</tt>
  <a class="headerlink" href="#FloatEventSeries.is_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each NULL value in this
series and False for each non-NULL value.

Example usage:
```python
patients.date_of_death.is_null()
```
</div>

<div class="attr-heading" id="FloatEventSeries.is_not_null">
  <tt><strong>is_not_null</strong>()</tt>
  <a class="headerlink" href="#FloatEventSeries.is_not_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_null()` above.

Example usage:
```python
patients.date_of_death.is_not_null()
```
</div>

<div class="attr-heading" id="FloatEventSeries.when_null_then">
  <tt><strong>when_null_then</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#FloatEventSeries.when_null_then" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Replace any NULL value in this series with the corresponding value in `other`.

Note that `other` must be of the same type as this series.

Example usage:
```python
(patients.date_of_death < "2020-01-01").when_null_then(False)
```
</div>

<div class="attr-heading" id="FloatEventSeries.is_in">
  <tt><strong>is_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#FloatEventSeries.is_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series which is
contained in `other`.

See how to combine `is_in` with a codelist in
[the how-to guide](../how-to/examples.md/#does-each-patient-have-a-clinical-event-matching-a-code-in-a-codelist).

Example usage:
```python
medications.dmd_code.is_in(["39113311000001107", "39113611000001102"])
```

`other` accepts any of the standard "container" types (tuple, list, set, frozenset,
or dict) or another event series.
</div>

<div class="attr-heading" id="FloatEventSeries.is_not_in">
  <tt><strong>is_not_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#FloatEventSeries.is_not_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_in()` above.
</div>

<div class="attr-heading" id="FloatEventSeries.map_values">
  <tt><strong>map_values</strong>(<em>mapping</em>, <em>default=None</em>)</tt>
  <a class="headerlink" href="#FloatEventSeries.map_values" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a new series with _mapping_ applied to each value. _mapping_ should
be a dictionary mapping one set of values to another.

Example usage:
```python
school_year = patients.age_on("2020-09-01").map_values(
    {13: "Year 9", 14: "Year 10", 15: "Year 11"},
    default="N/A"
)
```
</div>

<div class="attr-heading" id="FloatEventSeries.as_int">
  <tt><strong>as_int</strong>()</tt>
  <a class="headerlink" href="#FloatEventSeries.as_int" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return each value in this series rounded down to the nearest integer.
</div>

<div class="attr-heading" id="FloatEventSeries.as_float">
  <tt><strong>as_float</strong>()</tt>
  <a class="headerlink" href="#FloatEventSeries.as_float" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return each value in this series as a float (e.g. 10 becomes 10.0).
</div>

<div class="attr-heading" id="FloatEventSeries.count_distinct_for_patient">
  <tt><strong>count_distinct_for_patient</strong>()</tt>
  <a class="headerlink" href="#FloatEventSeries.count_distinct_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return an [integer patient series](#IntPatientSeries) counting the number of
distinct values for each patient in the series (ignoring any NULL values).

Note that if a patient has no values at all in the series the result will
be zero rather than NULL.

Example usage:
```python
medications.dmd_code.count_distinct_for_patient()
```
</div>

<div class="attr-heading" id="FloatEventSeries.minimum_for_patient">
  <tt><strong>minimum_for_patient</strong>()</tt>
  <a class="headerlink" href="#FloatEventSeries.minimum_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the minimum value in the series for each patient (or NULL if the patient
has no values).

Example usage:
```python
clinical_events.where(...).numeric_value.minimum_for_patient()
```
</div>

<div class="attr-heading" id="FloatEventSeries.maximum_for_patient">
  <tt><strong>maximum_for_patient</strong>()</tt>
  <a class="headerlink" href="#FloatEventSeries.maximum_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the maximum value in the series for each patient (or NULL if the patient
has no values).

Example usage:
```python
clinical_events.where(...).numeric_value.maximum_for_patient()
```
</div>

<div class="attr-heading" id="FloatEventSeries.sum_for_patient">
  <tt><strong>sum_for_patient</strong>()</tt>
  <a class="headerlink" href="#FloatEventSeries.sum_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the sum of all values in the series for each patient.
</div>

<div class="attr-heading" id="FloatEventSeries.mean_for_patient">
  <tt><strong>mean_for_patient</strong>()</tt>
  <a class="headerlink" href="#FloatEventSeries.mean_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the arithmetic mean of any non-NULL values in the series for each
patient.
</div>

</div>


<h4 class="attr-heading" id="DatePatientSeries" data-toc-label="DatePatientSeries" markdown>
  <tt><em>class</em> <strong>DatePatientSeries</strong>()</tt>
</h4>

<div markdown="block" class="indent">
One row per patient series of type `date`
<div class="attr-heading" id="DatePatientSeries.eq">
  <tt><em>self</em> <strong>==</strong> <em>other</em></tt>
  <a class="headerlink" href="#DatePatientSeries.eq" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series comparing each value in this series with its
corresponding value in `other`.

Note that the result of comparing anything with NULL (including NULL itself) is NULL.

Example usage:
```python
patients.sex == "female"
```
</div>

<div class="attr-heading" id="DatePatientSeries.ne">
  <tt><em>self</em> <strong>!=</strong> <em>other</em></tt>
  <a class="headerlink" href="#DatePatientSeries.ne" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `==` above.

Note that the same point regarding NULL applies here.

Example usage:
```python
patients.sex != "unknown"
```
</div>

<div class="attr-heading" id="DatePatientSeries.lt">
  <tt><em>self</em> <strong>></strong> <em>other</em></tt>
  <a class="headerlink" href="#DatePatientSeries.lt" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
strictly less than its corresponding value in `other` and False otherwise (or NULL
if either value is NULL).

Example usage:
```python
is_underage = patients.age_on("2020-01-01") < 18
```
</div>

<div class="attr-heading" id="DatePatientSeries.le">
  <tt><em>self</em> <strong>>=</strong> <em>other</em></tt>
  <a class="headerlink" href="#DatePatientSeries.le" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is less
than or equal to its corresponding value in `other` and False otherwise (or NULL
if either value is NULL).

Example usage:
```python
is_underage = patients.age_on("2020-01-01") <= 17
```
</div>

<div class="attr-heading" id="DatePatientSeries.ge">
  <tt><em>self</em> <strong><=</strong> <em>other</em></tt>
  <a class="headerlink" href="#DatePatientSeries.ge" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
greater than or equal to its corresponding value in `other` and False otherwise
(or NULL if either value is NULL).

Example usage:
```python
is_adult = patients.age_on("2020-01-01") >= 18
```
</div>

<div class="attr-heading" id="DatePatientSeries.gt">
  <tt><em>self</em> <strong><</strong> <em>other</em></tt>
  <a class="headerlink" href="#DatePatientSeries.gt" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
strictly greater than its corresponding value in `other` and False otherwise (or
NULL if either value is NULL).

Example usage:
```python
is_adult = patients.age_on("2020-01-01") > 17
```
</div>

<div class="attr-heading" id="DatePatientSeries.sub">
  <tt><em>self</em> <strong>-</strong> <em>other</em></tt>
  <a class="headerlink" href="#DatePatientSeries.sub" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a series giving the difference between each date in this series and
`other` (see [`DateDifference`](#DateDifference)).

Example usage:
```python
age_months = (date("2020-01-01") - patients.date_of_birth).months
```
</div>

<div class="attr-heading" id="DatePatientSeries.year">
  <tt><strong>year</strong></tt>
  <a class="headerlink" href="#DatePatientSeries.year" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return an integer series giving the year of each date in this series.
</div>

<div class="attr-heading" id="DatePatientSeries.month">
  <tt><strong>month</strong></tt>
  <a class="headerlink" href="#DatePatientSeries.month" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return an integer series giving the month (1-12) of each date in this series.
</div>

<div class="attr-heading" id="DatePatientSeries.day">
  <tt><strong>day</strong></tt>
  <a class="headerlink" href="#DatePatientSeries.day" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return an integer series giving the day of the month (1-31) of each date in this
series.
</div>

<div class="attr-heading" id="DatePatientSeries.is_null">
  <tt><strong>is_null</strong>()</tt>
  <a class="headerlink" href="#DatePatientSeries.is_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each NULL value in this
series and False for each non-NULL value.

Example usage:
```python
patients.date_of_death.is_null()
```
</div>

<div class="attr-heading" id="DatePatientSeries.is_not_null">
  <tt><strong>is_not_null</strong>()</tt>
  <a class="headerlink" href="#DatePatientSeries.is_not_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_null()` above.

Example usage:
```python
patients.date_of_death.is_not_null()
```
</div>

<div class="attr-heading" id="DatePatientSeries.when_null_then">
  <tt><strong>when_null_then</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#DatePatientSeries.when_null_then" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Replace any NULL value in this series with the corresponding value in `other`.

Note that `other` must be of the same type as this series.

Example usage:
```python
(patients.date_of_death < "2020-01-01").when_null_then(False)
```
</div>

<div class="attr-heading" id="DatePatientSeries.is_in">
  <tt><strong>is_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#DatePatientSeries.is_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series which is
contained in `other`.

See how to combine `is_in` with a codelist in
[the how-to guide](../how-to/examples.md/#does-each-patient-have-a-clinical-event-matching-a-code-in-a-codelist).

Example usage:
```python
medications.dmd_code.is_in(["39113311000001107", "39113611000001102"])
```

`other` accepts any of the standard "container" types (tuple, list, set, frozenset,
or dict) or another event series.
</div>

<div class="attr-heading" id="DatePatientSeries.is_not_in">
  <tt><strong>is_not_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#DatePatientSeries.is_not_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_in()` above.
</div>

<div class="attr-heading" id="DatePatientSeries.map_values">
  <tt><strong>map_values</strong>(<em>mapping</em>, <em>default=None</em>)</tt>
  <a class="headerlink" href="#DatePatientSeries.map_values" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a new series with _mapping_ applied to each value. _mapping_ should
be a dictionary mapping one set of values to another.

Example usage:
```python
school_year = patients.age_on("2020-09-01").map_values(
    {13: "Year 9", 14: "Year 10", 15: "Year 11"},
    default="N/A"
)
```
</div>

<div class="attr-heading" id="DatePatientSeries.to_first_of_year">
  <tt><strong>to_first_of_year</strong>()</tt>
  <a class="headerlink" href="#DatePatientSeries.to_first_of_year" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a date series with each date in this series replaced by the date of the
first day in its corresponding calendar year.

Example usage:
```python
patients.date_of_death.to_first_of_year()
```
</div>

<div class="attr-heading" id="DatePatientSeries.to_first_of_month">
  <tt><strong>to_first_of_month</strong>()</tt>
  <a class="headerlink" href="#DatePatientSeries.to_first_of_month" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a date series with each date in this series replaced by the date of the
first day in its corresponding calendar month.

Example usage:
```python
patients.date_of_death.to_first_of_month()
```
</div>

<div class="attr-heading" id="DatePatientSeries.is_before">
  <tt><strong>is_before</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#DatePatientSeries.is_before" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each date in this series that is
strictly earlier than its corresponding date in `other` and False otherwise
(or NULL if either value is NULL).

Example usage:
```python
medications.where(medications.date.is_before("2020-04-01"))
```
</div>

<div class="attr-heading" id="DatePatientSeries.is_on_or_before">
  <tt><strong>is_on_or_before</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#DatePatientSeries.is_on_or_before" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each date in this series that is
earlier than or the same as its corresponding value in `other` and False
otherwise (or NULL if either value is NULL).

Example usage:
```python
medications.where(medications.date.is_on_or_before("2020-03-31"))
```
</div>

<div class="attr-heading" id="DatePatientSeries.is_after">
  <tt><strong>is_after</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#DatePatientSeries.is_after" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each date in this series that is
strictly later than its corresponding date in `other` and False otherwise
(or NULL if either value is NULL).

Example usage:
```python
medications.where(medications.date.is_after("2020-03-31"))
```
</div>

<div class="attr-heading" id="DatePatientSeries.is_on_or_after">
  <tt><strong>is_on_or_after</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#DatePatientSeries.is_on_or_after" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each date in this series that is later
than or the same as its corresponding value in `other` and False otherwise (or
NULL if either value is NULL).

Example usage:
```python
medications.where(medications.date.is_on_or_after("2020-04-01"))
```
</div>

<div class="attr-heading" id="DatePatientSeries.is_between_but_not_on">
  <tt><strong>is_between_but_not_on</strong>(<em>start</em>, <em>end</em>)</tt>
  <a class="headerlink" href="#DatePatientSeries.is_between_but_not_on" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each date in this series which is
strictly between (i.e. not equal to) the corresponding dates in `start` and `end`,
and False otherwise.

Example usage:
```python
medications.where(medications.date.is_between_but_not_on("2020-03-31", "2021-04-01"))
```
For each trio of dates being compared, if any date is NULL the result is NULL.
</div>

<div class="attr-heading" id="DatePatientSeries.is_on_or_between">
  <tt><strong>is_on_or_between</strong>(<em>start</em>, <em>end</em>)</tt>
  <a class="headerlink" href="#DatePatientSeries.is_on_or_between" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each date in this series which is
between or the same as the corresponding dates in `start` and `end`, and
False otherwise.

Example usage:
```python
medications.where(medications.date.is_on_or_between("2020-04-01", "2021-03-31"))
```
For each trio of dates being compared, if any date is NULL the result is NULL.
</div>

<div class="attr-heading" id="DatePatientSeries.is_during">
  <tt><strong>is_during</strong>(<em>interval</em>)</tt>
  <a class="headerlink" href="#DatePatientSeries.is_during" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
The same as `is_on_or_between()` above, but allows supplying a start/end date
pair as single argument.

Example usage:
```python
study_period = ("2020-04-01", "2021-03-31")
medications.where(medications.date.is_during(study_period))
```

Also see the docs on using `is_during` with the
[`INTERVAL` placeholder](../explanation/measures.md/#the-interval-placeholder).
</div>

</div>


<h4 class="attr-heading" id="DateEventSeries" data-toc-label="DateEventSeries" markdown>
  <tt><em>class</em> <strong>DateEventSeries</strong>()</tt>
</h4>

<div markdown="block" class="indent">
Multiple rows per patient series of type `date`
<div class="attr-heading" id="DateEventSeries.eq">
  <tt><em>self</em> <strong>==</strong> <em>other</em></tt>
  <a class="headerlink" href="#DateEventSeries.eq" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series comparing each value in this series with its
corresponding value in `other`.

Note that the result of comparing anything with NULL (including NULL itself) is NULL.

Example usage:
```python
patients.sex == "female"
```
</div>

<div class="attr-heading" id="DateEventSeries.ne">
  <tt><em>self</em> <strong>!=</strong> <em>other</em></tt>
  <a class="headerlink" href="#DateEventSeries.ne" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `==` above.

Note that the same point regarding NULL applies here.

Example usage:
```python
patients.sex != "unknown"
```
</div>

<div class="attr-heading" id="DateEventSeries.lt">
  <tt><em>self</em> <strong>></strong> <em>other</em></tt>
  <a class="headerlink" href="#DateEventSeries.lt" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
strictly less than its corresponding value in `other` and False otherwise (or NULL
if either value is NULL).

Example usage:
```python
is_underage = patients.age_on("2020-01-01") < 18
```
</div>

<div class="attr-heading" id="DateEventSeries.le">
  <tt><em>self</em> <strong>>=</strong> <em>other</em></tt>
  <a class="headerlink" href="#DateEventSeries.le" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is less
than or equal to its corresponding value in `other` and False otherwise (or NULL
if either value is NULL).

Example usage:
```python
is_underage = patients.age_on("2020-01-01") <= 17
```
</div>

<div class="attr-heading" id="DateEventSeries.ge">
  <tt><em>self</em> <strong><=</strong> <em>other</em></tt>
  <a class="headerlink" href="#DateEventSeries.ge" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
greater than or equal to its corresponding value in `other` and False otherwise
(or NULL if either value is NULL).

Example usage:
```python
is_adult = patients.age_on("2020-01-01") >= 18
```
</div>

<div class="attr-heading" id="DateEventSeries.gt">
  <tt><em>self</em> <strong><</strong> <em>other</em></tt>
  <a class="headerlink" href="#DateEventSeries.gt" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series that is
strictly greater than its corresponding value in `other` and False otherwise (or
NULL if either value is NULL).

Example usage:
```python
is_adult = patients.age_on("2020-01-01") > 17
```
</div>

<div class="attr-heading" id="DateEventSeries.sub">
  <tt><em>self</em> <strong>-</strong> <em>other</em></tt>
  <a class="headerlink" href="#DateEventSeries.sub" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a series giving the difference between each date in this series and
`other` (see [`DateDifference`](#DateDifference)).

Example usage:
```python
age_months = (date("2020-01-01") - patients.date_of_birth).months
```
</div>

<div class="attr-heading" id="DateEventSeries.year">
  <tt><strong>year</strong></tt>
  <a class="headerlink" href="#DateEventSeries.year" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return an integer series giving the year of each date in this series.
</div>

<div class="attr-heading" id="DateEventSeries.month">
  <tt><strong>month</strong></tt>
  <a class="headerlink" href="#DateEventSeries.month" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return an integer series giving the month (1-12) of each date in this series.
</div>

<div class="attr-heading" id="DateEventSeries.day">
  <tt><strong>day</strong></tt>
  <a class="headerlink" href="#DateEventSeries.day" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return an integer series giving the day of the month (1-31) of each date in this
series.
</div>

<div class="attr-heading" id="DateEventSeries.is_null">
  <tt><strong>is_null</strong>()</tt>
  <a class="headerlink" href="#DateEventSeries.is_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each NULL value in this
series and False for each non-NULL value.

Example usage:
```python
patients.date_of_death.is_null()
```
</div>

<div class="attr-heading" id="DateEventSeries.is_not_null">
  <tt><strong>is_not_null</strong>()</tt>
  <a class="headerlink" href="#DateEventSeries.is_not_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_null()` above.

Example usage:
```python
patients.date_of_death.is_not_null()
```
</div>

<div class="attr-heading" id="DateEventSeries.when_null_then">
  <tt><strong>when_null_then</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#DateEventSeries.when_null_then" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Replace any NULL value in this series with the corresponding value in `other`.

Note that `other` must be of the same type as this series.

Example usage:
```python
(patients.date_of_death < "2020-01-01").when_null_then(False)
```
</div>

<div class="attr-heading" id="DateEventSeries.is_in">
  <tt><strong>is_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#DateEventSeries.is_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series which is
contained in `other`.

See how to combine `is_in` with a codelist in
[the how-to guide](../how-to/examples.md/#does-each-patient-have-a-clinical-event-matching-a-code-in-a-codelist).

Example usage:
```python
medications.dmd_code.is_in(["39113311000001107", "39113611000001102"])
```

`other` accepts any of the standard "container" types (tuple, list, set, frozenset,
or dict) or another event series.
</div>

<div class="attr-heading" id="DateEventSeries.is_not_in">
  <tt><strong>is_not_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#DateEventSeries.is_not_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_in()` above.
</div>

<div class="attr-heading" id="DateEventSeries.map_values">
  <tt><strong>map_values</strong>(<em>mapping</em>, <em>default=None</em>)</tt>
  <a class="headerlink" href="#DateEventSeries.map_values" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a new series with _mapping_ applied to each value. _mapping_ should
be a dictionary mapping one set of values to another.

Example usage:
```python
school_year = patients.age_on("2020-09-01").map_values(
    {13: "Year 9", 14: "Year 10", 15: "Year 11"},
    default="N/A"
)
```
</div>

<div class="attr-heading" id="DateEventSeries.to_first_of_year">
  <tt><strong>to_first_of_year</strong>()</tt>
  <a class="headerlink" href="#DateEventSeries.to_first_of_year" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a date series with each date in this series replaced by the date of the
first day in its corresponding calendar year.

Example usage:
```python
patients.date_of_death.to_first_of_year()
```
</div>

<div class="attr-heading" id="DateEventSeries.to_first_of_month">
  <tt><strong>to_first_of_month</strong>()</tt>
  <a class="headerlink" href="#DateEventSeries.to_first_of_month" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a date series with each date in this series replaced by the date of the
first day in its corresponding calendar month.

Example usage:
```python
patients.date_of_death.to_first_of_month()
```
</div>

<div class="attr-heading" id="DateEventSeries.is_before">
  <tt><strong>is_before</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#DateEventSeries.is_before" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each date in this series that is
strictly earlier than its corresponding date in `other` and False otherwise
(or NULL if either value is NULL).

Example usage:
```python
medications.where(medications.date.is_before("2020-04-01"))
```
</div>

<div class="attr-heading" id="DateEventSeries.is_on_or_before">
  <tt><strong>is_on_or_before</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#DateEventSeries.is_on_or_before" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each date in this series that is
earlier than or the same as its corresponding value in `other` and False
otherwise (or NULL if either value is NULL).

Example usage:
```python
medications.where(medications.date.is_on_or_before("2020-03-31"))
```
</div>

<div class="attr-heading" id="DateEventSeries.is_after">
  <tt><strong>is_after</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#DateEventSeries.is_after" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each date in this series that is
strictly later than its corresponding date in `other` and False otherwise
(or NULL if either value is NULL).

Example usage:
```python
medications.where(medications.date.is_after("2020-03-31"))
```
</div>

<div class="attr-heading" id="DateEventSeries.is_on_or_after">
  <tt><strong>is_on_or_after</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#DateEventSeries.is_on_or_after" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each date in this series that is later
than or the same as its corresponding value in `other` and False otherwise (or
NULL if either value is NULL).

Example usage:
```python
medications.where(medications.date.is_on_or_after("2020-04-01"))
```
</div>

<div class="attr-heading" id="DateEventSeries.is_between_but_not_on">
  <tt><strong>is_between_but_not_on</strong>(<em>start</em>, <em>end</em>)</tt>
  <a class="headerlink" href="#DateEventSeries.is_between_but_not_on" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each date in this series which is
strictly between (i.e. not equal to) the corresponding dates in `start` and `end`,
and False otherwise.

Example usage:
```python
medications.where(medications.date.is_between_but_not_on("2020-03-31", "2021-04-01"))
```
For each trio of dates being compared, if any date is NULL the result is NULL.
</div>

<div class="attr-heading" id="DateEventSeries.is_on_or_between">
  <tt><strong>is_on_or_between</strong>(<em>start</em>, <em>end</em>)</tt>
  <a class="headerlink" href="#DateEventSeries.is_on_or_between" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each date in this series which is
between or the same as the corresponding dates in `start` and `end`, and
False otherwise.

Example usage:
```python
medications.where(medications.date.is_on_or_between("2020-04-01", "2021-03-31"))
```
For each trio of dates being compared, if any date is NULL the result is NULL.
</div>

<div class="attr-heading" id="DateEventSeries.is_during">
  <tt><strong>is_during</strong>(<em>interval</em>)</tt>
  <a class="headerlink" href="#DateEventSeries.is_during" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
The same as `is_on_or_between()` above, but allows supplying a start/end date
pair as single argument.

Example usage:
```python
study_period = ("2020-04-01", "2021-03-31")
medications.where(medications.date.is_during(study_period))
```

Also see the docs on using `is_during` with the
[`INTERVAL` placeholder](../explanation/measures.md/#the-interval-placeholder).
</div>

<div class="attr-heading" id="DateEventSeries.count_distinct_for_patient">
  <tt><strong>count_distinct_for_patient</strong>()</tt>
  <a class="headerlink" href="#DateEventSeries.count_distinct_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return an [integer patient series](#IntPatientSeries) counting the number of
distinct values for each patient in the series (ignoring any NULL values).

Note that if a patient has no values at all in the series the result will
be zero rather than NULL.

Example usage:
```python
medications.dmd_code.count_distinct_for_patient()
```
</div>

<div class="attr-heading" id="DateEventSeries.minimum_for_patient">
  <tt><strong>minimum_for_patient</strong>()</tt>
  <a class="headerlink" href="#DateEventSeries.minimum_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the minimum value in the series for each patient (or NULL if the patient
has no values).

Example usage:
```python
clinical_events.where(...).numeric_value.minimum_for_patient()
```
</div>

<div class="attr-heading" id="DateEventSeries.maximum_for_patient">
  <tt><strong>maximum_for_patient</strong>()</tt>
  <a class="headerlink" href="#DateEventSeries.maximum_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the maximum value in the series for each patient (or NULL if the patient
has no values).

Example usage:
```python
clinical_events.where(...).numeric_value.maximum_for_patient()
```
</div>

<div class="attr-heading" id="DateEventSeries.count_episodes_for_patient">
  <tt><strong>count_episodes_for_patient</strong>(<em>maximum_gap</em>)</tt>
  <a class="headerlink" href="#DateEventSeries.count_episodes_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Counts the number of "episodes" for each patient where dates which are no more
than `maximum_gap` apart are considered part of the same episode. The
`maximum_gap` duration can be specified in [`days()`](#days) or
[`weeks()`](#weeks).

For example, suppose a patient has the following sequence of events:

Event ID | Date
-- | --
A | 2020-01-01
B | 2020-01-04
C | 2020-01-06
D | 2020-01-10
E | 2020-01-12

And suppose we count the episodes here using a maximum gap of three days:
```python
.count_episodes_for_patient(days(3))
```

We will get an episode count of two: events A, B and C are considered as one
episode and events D and E as another.

Note that events A and C are considered part of the same episode even though
they are more than three days apart because event B is no more than three days
apart from both of them. That is, the clock restarts with each new event in an
episode rather than running from the first event in an episode.
</div>

</div>


<h4 class="attr-heading" id="CodePatientSeries" data-toc-label="CodePatientSeries" markdown>
  <tt><em>class</em> <strong>CodePatientSeries</strong>()</tt>
</h4>

<div markdown="block" class="indent">
One row per patient series of type `code`
<div class="attr-heading" id="CodePatientSeries.eq">
  <tt><em>self</em> <strong>==</strong> <em>other</em></tt>
  <a class="headerlink" href="#CodePatientSeries.eq" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series comparing each value in this series with its
corresponding value in `other`.

Note that the result of comparing anything with NULL (including NULL itself) is NULL.

Example usage:
```python
patients.sex == "female"
```
</div>

<div class="attr-heading" id="CodePatientSeries.ne">
  <tt><em>self</em> <strong>!=</strong> <em>other</em></tt>
  <a class="headerlink" href="#CodePatientSeries.ne" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `==` above.

Note that the same point regarding NULL applies here.

Example usage:
```python
patients.sex != "unknown"
```
</div>

<div class="attr-heading" id="CodePatientSeries.is_null">
  <tt><strong>is_null</strong>()</tt>
  <a class="headerlink" href="#CodePatientSeries.is_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each NULL value in this
series and False for each non-NULL value.

Example usage:
```python
patients.date_of_death.is_null()
```
</div>

<div class="attr-heading" id="CodePatientSeries.is_not_null">
  <tt><strong>is_not_null</strong>()</tt>
  <a class="headerlink" href="#CodePatientSeries.is_not_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_null()` above.

Example usage:
```python
patients.date_of_death.is_not_null()
```
</div>

<div class="attr-heading" id="CodePatientSeries.when_null_then">
  <tt><strong>when_null_then</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#CodePatientSeries.when_null_then" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Replace any NULL value in this series with the corresponding value in `other`.

Note that `other` must be of the same type as this series.

Example usage:
```python
(patients.date_of_death < "2020-01-01").when_null_then(False)
```
</div>

<div class="attr-heading" id="CodePatientSeries.is_in">
  <tt><strong>is_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#CodePatientSeries.is_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series which is
contained in `other`.

See how to combine `is_in` with a codelist in
[the how-to guide](../how-to/examples.md/#does-each-patient-have-a-clinical-event-matching-a-code-in-a-codelist).

Example usage:
```python
medications.dmd_code.is_in(["39113311000001107", "39113611000001102"])
```

`other` accepts any of the standard "container" types (tuple, list, set, frozenset,
or dict) or another event series.
</div>

<div class="attr-heading" id="CodePatientSeries.is_not_in">
  <tt><strong>is_not_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#CodePatientSeries.is_not_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_in()` above.
</div>

<div class="attr-heading" id="CodePatientSeries.map_values">
  <tt><strong>map_values</strong>(<em>mapping</em>, <em>default=None</em>)</tt>
  <a class="headerlink" href="#CodePatientSeries.map_values" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a new series with _mapping_ applied to each value. _mapping_ should
be a dictionary mapping one set of values to another.

Example usage:
```python
school_year = patients.age_on("2020-09-01").map_values(
    {13: "Year 9", 14: "Year 10", 15: "Year 11"},
    default="N/A"
)
```
</div>

<div class="attr-heading" id="CodePatientSeries.to_category">
  <tt><strong>to_category</strong>(<em>categorisation</em>, <em>default=None</em>)</tt>
  <a class="headerlink" href="#CodePatientSeries.to_category" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
An alias for `map_values` which makes the intention clearer when working with
codelists. See [`codelist_from_csv()`](#codelist_from_csv).
</div>

</div>


<h4 class="attr-heading" id="CodeEventSeries" data-toc-label="CodeEventSeries" markdown>
  <tt><em>class</em> <strong>CodeEventSeries</strong>()</tt>
</h4>

<div markdown="block" class="indent">
Multiple rows per patient series of type `code`
<div class="attr-heading" id="CodeEventSeries.eq">
  <tt><em>self</em> <strong>==</strong> <em>other</em></tt>
  <a class="headerlink" href="#CodeEventSeries.eq" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series comparing each value in this series with its
corresponding value in `other`.

Note that the result of comparing anything with NULL (including NULL itself) is NULL.

Example usage:
```python
patients.sex == "female"
```
</div>

<div class="attr-heading" id="CodeEventSeries.ne">
  <tt><em>self</em> <strong>!=</strong> <em>other</em></tt>
  <a class="headerlink" href="#CodeEventSeries.ne" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `==` above.

Note that the same point regarding NULL applies here.

Example usage:
```python
patients.sex != "unknown"
```
</div>

<div class="attr-heading" id="CodeEventSeries.is_null">
  <tt><strong>is_null</strong>()</tt>
  <a class="headerlink" href="#CodeEventSeries.is_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each NULL value in this
series and False for each non-NULL value.

Example usage:
```python
patients.date_of_death.is_null()
```
</div>

<div class="attr-heading" id="CodeEventSeries.is_not_null">
  <tt><strong>is_not_null</strong>()</tt>
  <a class="headerlink" href="#CodeEventSeries.is_not_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_null()` above.

Example usage:
```python
patients.date_of_death.is_not_null()
```
</div>

<div class="attr-heading" id="CodeEventSeries.when_null_then">
  <tt><strong>when_null_then</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#CodeEventSeries.when_null_then" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Replace any NULL value in this series with the corresponding value in `other`.

Note that `other` must be of the same type as this series.

Example usage:
```python
(patients.date_of_death < "2020-01-01").when_null_then(False)
```
</div>

<div class="attr-heading" id="CodeEventSeries.is_in">
  <tt><strong>is_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#CodeEventSeries.is_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each value in this series which is
contained in `other`.

See how to combine `is_in` with a codelist in
[the how-to guide](../how-to/examples.md/#does-each-patient-have-a-clinical-event-matching-a-code-in-a-codelist).

Example usage:
```python
medications.dmd_code.is_in(["39113311000001107", "39113611000001102"])
```

`other` accepts any of the standard "container" types (tuple, list, set, frozenset,
or dict) or another event series.
</div>

<div class="attr-heading" id="CodeEventSeries.is_not_in">
  <tt><strong>is_not_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#CodeEventSeries.is_not_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_in()` above.
</div>

<div class="attr-heading" id="CodeEventSeries.map_values">
  <tt><strong>map_values</strong>(<em>mapping</em>, <em>default=None</em>)</tt>
  <a class="headerlink" href="#CodeEventSeries.map_values" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a new series with _mapping_ applied to each value. _mapping_ should
be a dictionary mapping one set of values to another.

Example usage:
```python
school_year = patients.age_on("2020-09-01").map_values(
    {13: "Year 9", 14: "Year 10", 15: "Year 11"},
    default="N/A"
)
```
</div>

<div class="attr-heading" id="CodeEventSeries.to_category">
  <tt><strong>to_category</strong>(<em>categorisation</em>, <em>default=None</em>)</tt>
  <a class="headerlink" href="#CodeEventSeries.to_category" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
An alias for `map_values` which makes the intention clearer when working with
codelists. See [`codelist_from_csv()`](#codelist_from_csv).
</div>

<div class="attr-heading" id="CodeEventSeries.count_distinct_for_patient">
  <tt><strong>count_distinct_for_patient</strong>()</tt>
  <a class="headerlink" href="#CodeEventSeries.count_distinct_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return an [integer patient series](#IntPatientSeries) counting the number of
distinct values for each patient in the series (ignoring any NULL values).

Note that if a patient has no values at all in the series the result will
be zero rather than NULL.

Example usage:
```python
medications.dmd_code.count_distinct_for_patient()
```
</div>

</div>


<h4 class="attr-heading" id="MultiCodeStringPatientSeries" data-toc-label="MultiCodeStringPatientSeries" markdown>
  <tt><em>class</em> <strong>MultiCodeStringPatientSeries</strong>()</tt>
</h4>

<div markdown="block" class="indent">
One row per patient series of type `multi code string`
<div class="attr-heading" id="MultiCodeStringPatientSeries.eq">
  <tt><em>self</em> <strong>==</strong> <em>other</em></tt>
  <a class="headerlink" href="#MultiCodeStringPatientSeries.eq" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
This operation is not allowed because it is unlikely you would want to match the
values in this field with an exact string e.g.
```python
apcs.all_diagnoses == "||I302, K201, J180 || I302, K200, M920"
```
Instead you should use the `contains` or `contains_any_of` methods.
</div>

<div class="attr-heading" id="MultiCodeStringPatientSeries.ne">
  <tt><em>self</em> <strong>!=</strong> <em>other</em></tt>
  <a class="headerlink" href="#MultiCodeStringPatientSeries.ne" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
See above
</div>

<div class="attr-heading" id="MultiCodeStringPatientSeries.is_null">
  <tt><strong>is_null</strong>()</tt>
  <a class="headerlink" href="#MultiCodeStringPatientSeries.is_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each NULL value in this
series and False for each non-NULL value.

Example usage:
```python
patients.date_of_death.is_null()
```
</div>

<div class="attr-heading" id="MultiCodeStringPatientSeries.is_not_null">
  <tt><strong>is_not_null</strong>()</tt>
  <a class="headerlink" href="#MultiCodeStringPatientSeries.is_not_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_null()` above.

Example usage:
```python
patients.date_of_death.is_not_null()
```
</div>

<div class="attr-heading" id="MultiCodeStringPatientSeries.when_null_then">
  <tt><strong>when_null_then</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#MultiCodeStringPatientSeries.when_null_then" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Replace any NULL value in this series with the corresponding value in `other`.

Note that `other` must be of the same type as this series.

Example usage:
```python
(patients.date_of_death < "2020-01-01").when_null_then(False)
```
</div>

<div class="attr-heading" id="MultiCodeStringPatientSeries.is_in">
  <tt><strong>is_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#MultiCodeStringPatientSeries.is_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
This operation is not allowed. To check for the presence of any codes in
a codelist, please use the `contains_any_of(codelist)` method instead.
</div>

<div class="attr-heading" id="MultiCodeStringPatientSeries.is_not_in">
  <tt><strong>is_not_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#MultiCodeStringPatientSeries.is_not_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
This operation is not allowed. To check for the absence of all codes in a codelist,
from a column called `column`, please use `~column.contains_any_of(codelist)`.
NB the `contains_any_of(codelist)` will provide any records that contain any of the
codes, which is then negated with the `~` operator.
</div>

<div class="attr-heading" id="MultiCodeStringPatientSeries.map_values">
  <tt><strong>map_values</strong>(<em>mapping</em>, <em>default=None</em>)</tt>
  <a class="headerlink" href="#MultiCodeStringPatientSeries.map_values" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a new series with _mapping_ applied to each value. _mapping_ should
be a dictionary mapping one set of values to another.

Example usage:
```python
school_year = patients.age_on("2020-09-01").map_values(
    {13: "Year 9", 14: "Year 10", 15: "Year 11"},
    default="N/A"
)
```
</div>

<div class="attr-heading" id="MultiCodeStringPatientSeries.contains">
  <tt><strong>contains</strong>(<em>code</em>)</tt>
  <a class="headerlink" href="#MultiCodeStringPatientSeries.contains" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Check if the list of codes contains a specific code string. This can
either be a string (and prefix matching works so e.g. "N17" in ICD-10
would match all acute renal failure), or a clinical code. E.g.
```python
all_diagnoses.contains("N17")
all_diagnoses.contains(ICD10Code("N170"))
```
</div>

<div class="attr-heading" id="MultiCodeStringPatientSeries.contains_any_of">
  <tt><strong>contains_any_of</strong>(<em>codelist</em>)</tt>
  <a class="headerlink" href="#MultiCodeStringPatientSeries.contains_any_of" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Returns true if any of the codes in the codelist occur in the multi code field.
As with the `contains(code)` method, the codelist can be a mixture of clinical
codes and string prefixes, so e.g. this would work:
```python
all_diagnoses.contains([ICD10Code("N170"), "N17"])
```
</div>

</div>


<h4 class="attr-heading" id="MultiCodeStringEventSeries" data-toc-label="MultiCodeStringEventSeries" markdown>
  <tt><em>class</em> <strong>MultiCodeStringEventSeries</strong>()</tt>
</h4>

<div markdown="block" class="indent">
Multiple rows per patient series of type `multi code string`
<div class="attr-heading" id="MultiCodeStringEventSeries.eq">
  <tt><em>self</em> <strong>==</strong> <em>other</em></tt>
  <a class="headerlink" href="#MultiCodeStringEventSeries.eq" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
This operation is not allowed because it is unlikely you would want to match the
values in this field with an exact string e.g.
```python
apcs.all_diagnoses == "||I302, K201, J180 || I302, K200, M920"
```
Instead you should use the `contains` or `contains_any_of` methods.
</div>

<div class="attr-heading" id="MultiCodeStringEventSeries.ne">
  <tt><em>self</em> <strong>!=</strong> <em>other</em></tt>
  <a class="headerlink" href="#MultiCodeStringEventSeries.ne" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
See above
</div>

<div class="attr-heading" id="MultiCodeStringEventSeries.is_null">
  <tt><strong>is_null</strong>()</tt>
  <a class="headerlink" href="#MultiCodeStringEventSeries.is_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a boolean series which is True for each NULL value in this
series and False for each non-NULL value.

Example usage:
```python
patients.date_of_death.is_null()
```
</div>

<div class="attr-heading" id="MultiCodeStringEventSeries.is_not_null">
  <tt><strong>is_not_null</strong>()</tt>
  <a class="headerlink" href="#MultiCodeStringEventSeries.is_not_null" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return the inverse of `is_null()` above.

Example usage:
```python
patients.date_of_death.is_not_null()
```
</div>

<div class="attr-heading" id="MultiCodeStringEventSeries.when_null_then">
  <tt><strong>when_null_then</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#MultiCodeStringEventSeries.when_null_then" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Replace any NULL value in this series with the corresponding value in `other`.

Note that `other` must be of the same type as this series.

Example usage:
```python
(patients.date_of_death < "2020-01-01").when_null_then(False)
```
</div>

<div class="attr-heading" id="MultiCodeStringEventSeries.is_in">
  <tt><strong>is_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#MultiCodeStringEventSeries.is_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
This operation is not allowed. To check for the presence of any codes in
a codelist, please use the `contains_any_of(codelist)` method instead.
</div>

<div class="attr-heading" id="MultiCodeStringEventSeries.is_not_in">
  <tt><strong>is_not_in</strong>(<em>other</em>)</tt>
  <a class="headerlink" href="#MultiCodeStringEventSeries.is_not_in" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
This operation is not allowed. To check for the absence of all codes in a codelist,
from a column called `column`, please use `~column.contains_any_of(codelist)`.
NB the `contains_any_of(codelist)` will provide any records that contain any of the
codes, which is then negated with the `~` operator.
</div>

<div class="attr-heading" id="MultiCodeStringEventSeries.map_values">
  <tt><strong>map_values</strong>(<em>mapping</em>, <em>default=None</em>)</tt>
  <a class="headerlink" href="#MultiCodeStringEventSeries.map_values" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a new series with _mapping_ applied to each value. _mapping_ should
be a dictionary mapping one set of values to another.

Example usage:
```python
school_year = patients.age_on("2020-09-01").map_values(
    {13: "Year 9", 14: "Year 10", 15: "Year 11"},
    default="N/A"
)
```
</div>

<div class="attr-heading" id="MultiCodeStringEventSeries.contains">
  <tt><strong>contains</strong>(<em>code</em>)</tt>
  <a class="headerlink" href="#MultiCodeStringEventSeries.contains" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Check if the list of codes contains a specific code string. This can
either be a string (and prefix matching works so e.g. "N17" in ICD-10
would match all acute renal failure), or a clinical code. E.g.
```python
all_diagnoses.contains("N17")
all_diagnoses.contains(ICD10Code("N170"))
```
</div>

<div class="attr-heading" id="MultiCodeStringEventSeries.contains_any_of">
  <tt><strong>contains_any_of</strong>(<em>codelist</em>)</tt>
  <a class="headerlink" href="#MultiCodeStringEventSeries.contains_any_of" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Returns true if any of the codes in the codelist occur in the multi code field.
As with the `contains(code)` method, the codelist can be a mixture of clinical
codes and string prefixes, so e.g. this would work:
```python
all_diagnoses.contains([ICD10Code("N170"), "N17"])
```
</div>

<div class="attr-heading" id="MultiCodeStringEventSeries.count_distinct_for_patient">
  <tt><strong>count_distinct_for_patient</strong>()</tt>
  <a class="headerlink" href="#MultiCodeStringEventSeries.count_distinct_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return an [integer patient series](#IntPatientSeries) counting the number of
distinct values for each patient in the series (ignoring any NULL values).

Note that if a patient has no values at all in the series the result will
be zero rather than NULL.

Example usage:
```python
medications.dmd_code.count_distinct_for_patient()
```
</div>

</div>
