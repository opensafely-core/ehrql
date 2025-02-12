<h4 class="attr-heading" id="PatientFrame" data-toc-label="PatientFrame" markdown>
  <tt><em>class</em> <strong>PatientFrame</strong>()</tt>
</h4>

<div markdown="block" class="indent">
Frame containing at most one row per patient.
<div class="attr-heading" id="PatientFrame.exists_for_patient">
  <tt><strong>exists_for_patient</strong>()</tt>
  <a class="headerlink" href="#PatientFrame.exists_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a [boolean patient series](#BoolPatientSeries) which is True for each
patient that has a row in this frame and False otherwise.

Example usage:
```python
pratice_registrations.for_patient_on("2020-01-01").exists_for_patient()
```
</div>

<div class="attr-heading" id="PatientFrame.count_for_patient">
  <tt><strong>count_for_patient</strong>()</tt>
  <a class="headerlink" href="#PatientFrame.count_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return an [integer patient series](#IntPatientSeries) giving the number of rows each
patient has in this frame.

Note this will be 0 rather than NULL if the patient has no rows at all in the frame.

Example usage:
```python
clinical_events.where(clinical_events.date.year == 2020).count_for_patient()
```
</div>

</div>


<h4 class="attr-heading" id="EventFrame" data-toc-label="EventFrame" markdown>
  <tt><em>class</em> <strong>EventFrame</strong>()</tt>
</h4>

<div markdown="block" class="indent">
Frame which may contain multiple rows per patient.
<div class="attr-heading" id="EventFrame.where">
  <tt><strong>where</strong>(<em>condition</em>)</tt>
  <a class="headerlink" href="#EventFrame.where" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a new frame containing only the rows in this frame for which `condition`
evaluates True.

Note that this excludes any rows for which `condition` is NULL.

Example usage:
```python
clinical_events.where(clinical_events.date >= "2020-01-01")
```
</div>

<div class="attr-heading" id="EventFrame.except_where">
  <tt><strong>except_where</strong>(<em>condition</em>)</tt>
  <a class="headerlink" href="#EventFrame.except_where" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a new frame containing only the rows in this frame for which `condition`
evaluates False or NULL i.e. the exact inverse of the rows included by
`where()`.

Example usage:
```python
practice_registrations.except_where(practice_registrations.end_date < "2020-01-01")
```

Note that `except_where()` is not the same as `where()` with an inverted condition,
as the latter would exclude rows where `condition` is NULL.
</div>

<div class="attr-heading" id="EventFrame.sort_by">
  <tt><strong>sort_by</strong>(<em>*sort_values</em>)</tt>
  <a class="headerlink" href="#EventFrame.sort_by" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Returns a new frame with the rows sorted for each patient, by
each of the supplied `sort_values`.

Where more than one sort value is supplied then the first (i.e. left-most) value
has highest priority and each subsequent sort value will only be used as a
tie-breaker in case of an exact match among previous values.

Note that NULL is considered smaller than any other value, so you may wish to
filter out NULL values before sorting.

Example usage:
```python
clinical_events.sort_by(clinical_events.date, clinical_events.snomedct_code)
```
</div>

<div class="attr-heading" id="EventFrame.exists_for_patient">
  <tt><strong>exists_for_patient</strong>()</tt>
  <a class="headerlink" href="#EventFrame.exists_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a [boolean patient series](#BoolPatientSeries) which is True for each
patient that has a row in this frame and False otherwise.

Example usage:
```python
pratice_registrations.for_patient_on("2020-01-01").exists_for_patient()
```
</div>

<div class="attr-heading" id="EventFrame.count_for_patient">
  <tt><strong>count_for_patient</strong>()</tt>
  <a class="headerlink" href="#EventFrame.count_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return an [integer patient series](#IntPatientSeries) giving the number of rows each
patient has in this frame.

Note this will be 0 rather than NULL if the patient has no rows at all in the frame.

Example usage:
```python
clinical_events.where(clinical_events.date.year == 2020).count_for_patient()
```
</div>

</div>


<h4 class="attr-heading" id="SortedEventFrame" data-toc-label="SortedEventFrame" markdown>
  <tt><em>class</em> <strong>SortedEventFrame</strong>()</tt>
</h4>

<div markdown="block" class="indent">
Frame which contains multiple rows per patient and has had one or more sort
operations applied.
<div class="attr-heading" id="SortedEventFrame.where">
  <tt><strong>where</strong>(<em>condition</em>)</tt>
  <a class="headerlink" href="#SortedEventFrame.where" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a new frame containing only the rows in this frame for which `condition`
evaluates True.

Note that this excludes any rows for which `condition` is NULL.

Example usage:
```python
clinical_events.where(clinical_events.date >= "2020-01-01")
```
</div>

<div class="attr-heading" id="SortedEventFrame.except_where">
  <tt><strong>except_where</strong>(<em>condition</em>)</tt>
  <a class="headerlink" href="#SortedEventFrame.except_where" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a new frame containing only the rows in this frame for which `condition`
evaluates False or NULL i.e. the exact inverse of the rows included by
`where()`.

Example usage:
```python
practice_registrations.except_where(practice_registrations.end_date < "2020-01-01")
```

Note that `except_where()` is not the same as `where()` with an inverted condition,
as the latter would exclude rows where `condition` is NULL.
</div>

<div class="attr-heading" id="SortedEventFrame.sort_by">
  <tt><strong>sort_by</strong>(<em>*sort_values</em>)</tt>
  <a class="headerlink" href="#SortedEventFrame.sort_by" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Returns a new frame with the rows sorted for each patient, by
each of the supplied `sort_values`.

Where more than one sort value is supplied then the first (i.e. left-most) value
has highest priority and each subsequent sort value will only be used as a
tie-breaker in case of an exact match among previous values.

Note that NULL is considered smaller than any other value, so you may wish to
filter out NULL values before sorting.

Example usage:
```python
clinical_events.sort_by(clinical_events.date, clinical_events.snomedct_code)
```
</div>

<div class="attr-heading" id="SortedEventFrame.exists_for_patient">
  <tt><strong>exists_for_patient</strong>()</tt>
  <a class="headerlink" href="#SortedEventFrame.exists_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a [boolean patient series](#BoolPatientSeries) which is True for each
patient that has a row in this frame and False otherwise.

Example usage:
```python
pratice_registrations.for_patient_on("2020-01-01").exists_for_patient()
```
</div>

<div class="attr-heading" id="SortedEventFrame.count_for_patient">
  <tt><strong>count_for_patient</strong>()</tt>
  <a class="headerlink" href="#SortedEventFrame.count_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return an [integer patient series](#IntPatientSeries) giving the number of rows each
patient has in this frame.

Note this will be 0 rather than NULL if the patient has no rows at all in the frame.

Example usage:
```python
clinical_events.where(clinical_events.date.year == 2020).count_for_patient()
```
</div>

<div class="attr-heading" id="SortedEventFrame.first_for_patient">
  <tt><strong>first_for_patient</strong>()</tt>
  <a class="headerlink" href="#SortedEventFrame.first_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a PatientFrame containing, for each patient, the first matching row
according to whatever sort order has been applied.

Note that where there are multiple rows tied for first place then the specific
row returned is picked arbitrarily but consistently i.e. you shouldn't depend on
getting any particular result, but the result you do get shouldn't change unless
the data changes.

Example usage:
```python
medications.sort_by(medications.date).first_for_patient()
```
</div>

<div class="attr-heading" id="SortedEventFrame.last_for_patient">
  <tt><strong>last_for_patient</strong>()</tt>
  <a class="headerlink" href="#SortedEventFrame.last_for_patient" title="Permanent link">🔗</a>
</div>
<div markdown="block" class="indent">
Return a PatientFrame containing, for each patient, the last matching row
according to whatever sort order has been applied.

Note that where there are multiple rows tied for last place then the specific
row returned is picked arbitrarily but consistently i.e. you shouldn't depend on
getting any particular result, but the result you do get shouldn't change unless
the data changes.

Example usage:
```python
medications.sort_by(medications.date).last_for_patient()
```
</div>

</div>
