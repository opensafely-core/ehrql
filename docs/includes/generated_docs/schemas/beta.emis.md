# <strong>beta.emis</strong> schema

Available on backends: [**EMIS**](../../backends#emis)

This schema defines the data (both primary care and externally linked) available in the
OpenSAFELY-EMIS backend. For more information about this backend, see
"[EMIS Primary Care](https://docs.opensafely.org/data-sources/emis/)".

``` {.python .copy title='To use this schema in an ehrQL file:'}
from ehrql.tables.beta.emis import (
    clinical_events,
    patients,
)
```

<p class="dimension-indicator"><code>many rows per patient</code></p>
## clinical_events

Each record corresponds to a single clinical or consultation event for a patient.

Note that event codes do not change in this table. If an event code in the coding
system becomes inactive, the event will still be coded to the inactive code.
As such, codelists should include all relevant inactive codes.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
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
  <dt id="clinical_events.snomedct_code">
    <strong>snomedct_code</strong>
    <a class="headerlink" href="#clinical_events.snomedct_code" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
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
</div>


<p class="dimension-indicator"><code>one row per patient</code></p>
## patients

Patients in primary care.

### Representativeness

You can find out more about the representativeness of these data in the
OpenSAFELY-TPP backend in:

> The OpenSAFELY Collaborative, Colm D. Andrews, Anna Schultze, Helen J. Curtis, William J. Hulme, John Tazare, Stephen J. W. Evans, _et al._ 2022.
> "OpenSAFELY: Representativeness of Electronic Health Record Platform OpenSAFELY-TPP Data Compared to the Population of England."
> Wellcome Open Res 2022, 7:191.
> <https://doi.org/10.12688/wellcomeopenres.18010.1>


### Orphan records

If a practice becomes aware that a patient has moved house,
then the practice _deducts_, or removes, the patient's records from their register.
If the patient doesn't register with a new practice within a given amount of time
(normally from four to eight weeks),
then the patient's records are permanently deducted and are _orphan records_.
There are roughly 1.6 million orphan records.

### Recording of death in primary care

In England, it is the statutory duty of the doctor who had attended in the last
illness to complete a medical certificate of cause of death (MCCD). ONS death data
are considered the gold standard for identifying patient deaths because they are
based on these MCCDs.

There is generally a lag between the death being recorded in ONS data and it
appearing in the primary care record, but the coverage or recorded death is almost
complete and the date of death is usually reliable when it appears. There is
also a lag in ONS death recording (see [`ons_deaths`](/reference/schemas/beta.core/#ons_deaths) below
for more detail). You can find out more about the accuracy of date of death
recording in primary care in:

> Gallagher, A. M., Dedman, D., Padmanabhan, S., Leufkens, H. G. M. & de Vries, F 2019. The accuracy of date of death recording in the Clinical
> Practice Research Datalink GOLD database in England compared with the Office for National Statistics death registrations.
> Pharmacoepidemiol. Drug Saf. 28, 563–569.
> <https://doi.org/10.1002/pds.4747>

By contrast, cause of death is often not accurate in the primary care record so we
don't make it available to query here.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="patients.date_of_birth">
    <strong>date_of_birth</strong>
    <a class="headerlink" href="#patients.date_of_birth" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Patient's date of birth.

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
Patient's sex.

 * Possible values: `female`, `male`, `intersex`, `unknown`
 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="patients.date_of_death">
    <strong>date_of_death</strong>
    <a class="headerlink" href="#patients.date_of_death" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Patient's date of death.

  </dd>
</div>

  </dl>
</div>
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Methods</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="patients.age_on">
    <strong>age_on(</strong>date<strong>)</strong>
    <a class="headerlink" href="#patients.age_on" title="Permanent link">🔗</a>
    <code></code>
  </dt>
  <dd markdown="block">
Patient's age as an integer, in whole elapsed calendar years, as it would be on
the given date.

This method takes no account of whether the patient is alive on the given date.
In particular, it may return negative values if the given date is before the
patient's date of birth.
    <details markdown="block">
    <summary>View method definition</summary>
```py
return (date - patients.date_of_birth).years

```
    </details>
  </dd>
</div>

  </dl>
</div>
