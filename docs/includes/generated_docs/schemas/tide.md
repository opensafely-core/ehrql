
# <strong>tide</strong> schema

Available on backends: [**TIDE**](../backends.md#tide)

This schema defines the data available in the
OpenSAFELY-TIDE backend for education datasets.

``` {.python .copy title='To use this schema in an ehrQL file:'}
from ehrql.tables.tide import (
    assessments,
    pupils,
)
```

<p class="dimension-indicator"><code>many rows per patient</code></p>
## assessments

Assessment records for pupils.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="assessments.date">
    <strong>date</strong>
    <a class="headerlink" href="#assessments.date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date the assessment was taken.

  </dd>
</div>

<div markdown="block">
  <dt id="assessments.teacher_id">
    <strong>teacher_id</strong>
    <a class="headerlink" href="#assessments.teacher_id" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
Identifier for the teacher who taught the pupil.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="assessments.subject">
    <strong>subject</strong>
    <a class="headerlink" href="#assessments.subject" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
The subject of the assessment.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="assessments.result">
    <strong>result</strong>
    <a class="headerlink" href="#assessments.result" title="Permanent link">🔗</a>
    <code>float</code>
  </dt>
  <dd markdown="block">
The assessment result as a percentage (0-100), or null if no result recorded.

 * Always >= 0 and <= 100
  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>one row per patient</code></p>
## pupils

Pupils in the education dataset.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="pupils.mat_id">
    <strong>mat_id</strong>
    <a class="headerlink" href="#pupils.mat_id" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
Multi-Academy Trust identifier for the pupil.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="pupils.gender">
    <strong>gender</strong>
    <a class="headerlink" href="#pupils.gender" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
Pupil's gender.

 * Possible values: `female`, `male`, `unknown`
 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="pupils.date_of_birth">
    <strong>date_of_birth</strong>
    <a class="headerlink" href="#pupils.date_of_birth" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Pupil's date of birth.

 * Always the first day of a month
 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="pupils.eal">
    <strong>eal</strong>
    <a class="headerlink" href="#pupils.eal" title="Permanent link">🔗</a>
    <code>boolean</code>
  </dt>
  <dd markdown="block">
Whether the pupil has English as an Additional Language (EAL).

  </dd>
</div>

<div markdown="block">
  <dt id="pupils.send">
    <strong>send</strong>
    <a class="headerlink" href="#pupils.send" title="Permanent link">🔗</a>
    <code>boolean</code>
  </dt>
  <dd markdown="block">
Whether the pupil has Special Educational Needs and Disabilities (SEND).

  </dd>
</div>

<div markdown="block">
  <dt id="pupils.pupil_premium">
    <strong>pupil_premium</strong>
    <a class="headerlink" href="#pupils.pupil_premium" title="Permanent link">🔗</a>
    <code>boolean</code>
  </dt>
  <dd markdown="block">
Whether the pupil is eligible for pupil premium funding.

  </dd>
</div>

<div markdown="block">
  <dt id="pupils.attendance">
    <strong>attendance</strong>
    <a class="headerlink" href="#pupils.attendance" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
Pupil's attendance percentage.

 * Always >= 0 and <= 100
  </dd>
</div>

  </dl>
</div>
