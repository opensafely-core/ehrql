# <strong>examples.tutorial</strong> schema

_This schema is for development or testing purposes and is not available on any backend._

This example schema is for use in the ehrQL tutorial.

``` {.python .copy title='To use this schema in an ehrQL file:'}
from ehrql.tables.examples.tutorial import (
    clinical_events,
    hospitalisations,
    patient_address,
    patients,
    prescriptions,
)
```

<p class="dimension-indicator"><code>many rows per patient</code></p>
## clinical_events

TODO.

<dl markdown="block" class="schema-column-list">
<div markdown="block">
  <dt id="clinical_events.code">
    <strong>code</strong>
    <a class="headerlink" href="#clinical_events.code" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="clinical_events.system">
    <strong>system</strong>
    <a class="headerlink" href="#clinical_events.system" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="clinical_events.date">
    <strong>date</strong>
    <a class="headerlink" href="#clinical_events.date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="clinical_events.numeric_value">
    <strong>numeric_value</strong>
    <a class="headerlink" href="#clinical_events.numeric_value" title="Permanent link">🔗</a>
    <code>float</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

</dl>

<p class="dimension-indicator"><code>many rows per patient</code></p>
## hospitalisations

TODO.

<dl markdown="block" class="schema-column-list">
<div markdown="block">
  <dt id="hospitalisations.date">
    <strong>date</strong>
    <a class="headerlink" href="#hospitalisations.date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="hospitalisations.code">
    <strong>code</strong>
    <a class="headerlink" href="#hospitalisations.code" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="hospitalisations.system">
    <strong>system</strong>
    <a class="headerlink" href="#hospitalisations.system" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

</dl>

<p class="dimension-indicator"><code>many rows per patient</code></p>
## patient_address

TODO.

<dl markdown="block" class="schema-column-list">
<div markdown="block">
  <dt id="patient_address.patientaddress_id">
    <strong>patientaddress_id</strong>
    <a class="headerlink" href="#patient_address.patientaddress_id" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="patient_address.date_start">
    <strong>date_start</strong>
    <a class="headerlink" href="#patient_address.date_start" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="patient_address.date_end">
    <strong>date_end</strong>
    <a class="headerlink" href="#patient_address.date_end" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="patient_address.index_of_multiple_deprivation_rounded">
    <strong>index_of_multiple_deprivation_rounded</strong>
    <a class="headerlink" href="#patient_address.index_of_multiple_deprivation_rounded" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="patient_address.has_postcode">
    <strong>has_postcode</strong>
    <a class="headerlink" href="#patient_address.has_postcode" title="Permanent link">🔗</a>
    <code>boolean</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

</dl>

<p class="dimension-indicator"><code>one row per patient</code></p>
## patients



<dl markdown="block" class="schema-column-list">
<div markdown="block">
  <dt id="patients.date_of_birth">
    <strong>date_of_birth</strong>
    <a class="headerlink" href="#patients.date_of_birth" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Patient's date of birth, rounded to first of month

 * Always the first day of a month
 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="patients.sex">
    <strong>sex</strong>
    <a class="headerlink" href="#patients.sex" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
Patient's sex

 * Never `NULL`
 * Possible values: `female`, `male`, `intersex`, `unknown`
  </dd>
</div>

<div markdown="block">
  <dt id="patients.date_of_death">
    <strong>date_of_death</strong>
    <a class="headerlink" href="#patients.date_of_death" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Patient's date of death

  </dd>
</div>

</dl>

<p class="dimension-indicator"><code>many rows per patient</code></p>
## prescriptions

TODO.

<dl markdown="block" class="schema-column-list">
<div markdown="block">
  <dt id="prescriptions.prescribed_dmd_code">
    <strong>prescribed_dmd_code</strong>
    <a class="headerlink" href="#prescriptions.prescribed_dmd_code" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="prescriptions.processing_date">
    <strong>processing_date</strong>
    <a class="headerlink" href="#prescriptions.processing_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

</dl>
