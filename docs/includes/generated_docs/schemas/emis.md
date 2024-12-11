# <strong>emis</strong> schema

Available on backends: [**EMIS**](../backends.md#emis)

This schema defines the data (both primary care and externally linked) available in the
OpenSAFELY-EMIS backend. For more information about this backend, see
"[EMIS Primary Care](https://docs.opensafely.org/data-sources/emis/)".

``` {.python .copy title='To use this schema in an ehrQL file:'}
from ehrql.tables.emis import (
    clinical_events,
    medications,
    ons_deaths,
    patients,
    practice_registrations,
    vaccinations,
)
```

<p class="dimension-indicator"><code>many rows per patient</code></p>
## clinical_events

Each record corresponds to a single clinical or consultation event for a patient.

Note that event codes do not change in this table. If an event code in the coding
system becomes inactive, the event will still be coded to the inactive code.
As such, codelists should include all relevant inactive codes.

### Example usage

[Example ehrQL usage of clinical_events](../../../how-to/examples/#clinical-events)
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


<p class="dimension-indicator"><code>many rows per patient</code></p>
## medications

The medications table provides data about prescribed medications in primary care.

Prescribing data, including the contents of the medications table are standardised
across clinical information systems such as SystmOne (TPP). This is a requirement
for data transfer through the
[Electronic Prescription Service](https://digital.nhs.uk/services/electronic-prescription-service/)
in which data passes from the prescriber to the pharmacy for dispensing.

Medications are coded using
[dm+d codes](https://www.bennett.ox.ac.uk/blog/2019/08/what-is-the-dm-d-the-nhs-dictionary-of-medicines-and-devices/).
The medications table is structured similarly to the [clinical_events](#clinical_events)
table, and each row in the table is made up of a patient identifier, an event (dm+d)
code, and an event date. For this table, the event refers to the issue of a medication
(coded as a dm+d code), and the event date, the date the prescription was issued.

### Factors to consider when using medications data

Depending on the specific area of research, you may wish to exclude medications
in particular periods. For example, in order to ensure medication data is stable
following a change of practice, you may want to exclude patients for a period after
the start of their practice registration . You may also want to
exclude medications for patients for a period prior to their leaving a practice.
Alternatively, for research looking at a specific period of
interest, you may simply want to ensure that all included patients were registered
at a single practice for a minimum time prior to the study period, and were
registered at the same practice for the duration of the study period.

### Example usage

Examples of using ehrQL to calculation such periods can be found in the documentation
on how to
[use ehrQL to answer specific questions using the medications table](../../../how-to/examples/#clinical-events)
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="medications.date">
    <strong>date</strong>
    <a class="headerlink" href="#medications.date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="medications.dmd_code">
    <strong>dmd_code</strong>
    <a class="headerlink" href="#medications.dmd_code" title="Permanent link">🔗</a>
    <code>dm+d code</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>one row per patient</code></p>
## ons_deaths

Registered deaths

Date and cause of death based on information recorded when deaths are
certified and registered in England and Wales from February 2019 onwards.
The data provider is the Office for National Statistics (ONS).
This table is updated approximately weekly in OpenSAFELY.

This table includes the underlying cause of death and up to 15 medical conditions
mentioned on the death certificate.  These codes (`cause_of_death_01` to
`cause_of_death_15`) are not ordered meaningfully.

More information about this table can be found in following documents provided by the ONS:

- [Information collected at death registration](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/methodologies/userguidetomortalitystatisticsjuly2017#information-collected-at-death-registration)
- [User guide to mortality statistics](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/methodologies/userguidetomortalitystatisticsjuly2017)
- [How death registrations are recorded and stored by ONS](https://www.ons.gov.uk/aboutus/transparencyandgovernance/freedomofinformationfoi/howdeathregistrationsarerecordedandstoredbyons)

In the associated database table [ONS_Deaths](https://reports.opensafely.org/reports/opensafely-tpp-database-schema/#ONS_Deaths),
a small number of patients have multiple registered deaths.
This table contains the earliest registered death.
The `ehrql.tables.raw.core.ons_deaths` table contains all registered deaths.

!!! warning
    There is also a lag in ONS death recording caused amongst other things by things
    like autopsies and inquests delaying reporting on cause of death. This is
    evident in the [OpenSAFELY historical database coverage
    report](https://reports.opensafely.org/reports/opensafely-tpp-database-history/#ons_deaths)

### Example usage

[Example ehrQL usage of ons_deaths](../../../how-to/examples/#ons-deaths)
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="ons_deaths.date">
    <strong>date</strong>
    <a class="headerlink" href="#ons_deaths.date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Patient's date of death.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.underlying_cause_of_death">
    <strong>underlying_cause_of_death</strong>
    <a class="headerlink" href="#ons_deaths.underlying_cause_of_death" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Patient's underlying cause of death.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_01">
    <strong>cause_of_death_01</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_01" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_02">
    <strong>cause_of_death_02</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_02" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_03">
    <strong>cause_of_death_03</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_03" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_04">
    <strong>cause_of_death_04</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_04" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_05">
    <strong>cause_of_death_05</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_05" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_06">
    <strong>cause_of_death_06</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_06" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_07">
    <strong>cause_of_death_07</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_07" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_08">
    <strong>cause_of_death_08</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_08" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_09">
    <strong>cause_of_death_09</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_09" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_10">
    <strong>cause_of_death_10</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_10" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_11">
    <strong>cause_of_death_11</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_11" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_12">
    <strong>cause_of_death_12</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_12" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_13">
    <strong>cause_of_death_13</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_13" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_14">
    <strong>cause_of_death_14</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_14" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_15">
    <strong>cause_of_death_15</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_15" title="Permanent link">🔗</a>
    <code>ICD-10 code</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

  </dl>
</div>
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Methods</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="ons_deaths.cause_of_death_is_in">
    <strong>cause_of_death_is_in(</strong>codelist<strong>)</strong>
    <a class="headerlink" href="#ons_deaths.cause_of_death_is_in" title="Permanent link">🔗</a>
    <code></code>
  </dt>
  <dd markdown="block">
Match `codelist` against the `underlying_cause_of_death` field and all 15
separate `cause_of_death` fields.

This method evaluates as `True` if _any_ code in the codelist matches _any_ of
these fields.
    <details markdown="block">
    <summary>View method definition</summary>
```py
columns = [
    "underlying_cause_of_death",
    *[f"cause_of_death_{i:02d}" for i in range(1, 16)],
]
conditions = [getattr(ons_deaths, column).is_in(codelist) for column in columns]
return functools.reduce(operator.or_, conditions)

```
    </details>
  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>one row per patient</code></p>
## patients

Patients in primary care.

In the EMIS backend, this table also includes information about the patient's
current practice registration. Historical practice registration data is not
currently available.

### Recording of death in primary care

In England, it is the statutory duty of the doctor who had attended in the last
illness to complete a medical certificate of cause of death (MCCD). ONS death data
are considered the gold standard for identifying patient deaths because they are
based on these MCCDs.

There is generally a lag between the death being recorded in ONS data and it
appearing in the primary care record, but the coverage or recorded death is almost
complete and the date of death is usually reliable when it appears. There is
also a lag in ONS death recording (see [`ons_deaths`](core.md#ons_deaths)
for more detail). You can find out more about the accuracy of date of death
recording in primary care in:

> Gallagher, A. M., Dedman, D., Padmanabhan, S., Leufkens, H. G. M. & de Vries, F 2019. The accuracy of date of death recording in the Clinical
> Practice Research Datalink GOLD database in England compared with the Office for National Statistics death registrations.
> Pharmacoepidemiol. Drug Saf. 28, 563–569.
> <https://doi.org/10.1002/pds.4747>
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

 * Possible values: `female`, `male`, `unknown`
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

<div markdown="block">
  <dt id="patients.registration_start_date">
    <strong>registration_start_date</strong>
    <a class="headerlink" href="#patients.registration_start_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Date patient joined practice.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="patients.registration_end_date">
    <strong>registration_end_date</strong>
    <a class="headerlink" href="#patients.registration_end_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Date patient left practice.

  </dd>
</div>

<div markdown="block">
  <dt id="patients.practice_pseudo_id">
    <strong>practice_pseudo_id</strong>
    <a class="headerlink" href="#patients.practice_pseudo_id" title="Permanent link">🔗</a>
    <code>string</code>
  </dt>
  <dd markdown="block">
Pseudonymised practice identifier.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="patients.rural_urban_classification">
    <strong>rural_urban_classification</strong>
    <a class="headerlink" href="#patients.rural_urban_classification" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
Rural urban classification:

* 1 - Urban major conurbation
* 2 - Urban minor conurbation
* 3 - Urban city and town
* 4 - Urban city and town in a sparse setting
* 5 - Rural town and fringe
* 6 - Rural town and fringe in a sparse setting
* 7 - Rural village and dispersed
* 8 - Rural village and dispersed in a sparse setting

 * Always >= 1 and <= 8
  </dd>
</div>

<div markdown="block">
  <dt id="patients.imd_rounded">
    <strong>imd_rounded</strong>
    <a class="headerlink" href="#patients.imd_rounded" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
[Index of Multiple Deprivation][addresses_imd] (IMD)
rounded to the nearest 100, where lower values represent more deprived areas.

[addresses_imd]: https://www.gov.uk/government/statistics/english-indices-of-deprivation-2019

 * Always >= 0, <= 32800, and a multiple of 100
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

<div markdown="block">
  <dt id="patients.has_practice_registration_spanning">
    <strong>has_practice_registration_spanning(</strong>start_date, end_date<strong>)</strong>
    <a class="headerlink" href="#patients.has_practice_registration_spanning" title="Permanent link">🔗</a>
    <code></code>
  </dt>
  <dd markdown="block">
Whether a patient's registration spans the entire period between
`start_date` and `end_date`.
    <details markdown="block">
    <summary>View method definition</summary>
```py
return patients.registration_start_date.is_on_or_before(start_date) & (
    patients.registration_end_date.is_after(end_date)
    | patients.registration_end_date.is_null()
)

```
    </details>
  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## practice_registrations

Each record corresponds to a patient's registration with a practice.

### Example usage

[Example ehrQL usage of practice_registrations](../../../how-to/examples/#practice-registrations)

### EMIS specific information

!!! warning
    At present, the EMIS database contains only the patient's current practice
    registration and does not include their full registration history.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="practice_registrations.start_date">
    <strong>start_date</strong>
    <a class="headerlink" href="#practice_registrations.start_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Date patient joined practice.

 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="practice_registrations.end_date">
    <strong>end_date</strong>
    <a class="headerlink" href="#practice_registrations.end_date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
Date patient left practice.

  </dd>
</div>

<div markdown="block">
  <dt id="practice_registrations.practice_pseudo_id">
    <strong>practice_pseudo_id</strong>
    <a class="headerlink" href="#practice_registrations.practice_pseudo_id" title="Permanent link">🔗</a>
    <code>integer</code>
  </dt>
  <dd markdown="block">
Pseudonymised practice identifier.

 * Never `NULL`
  </dd>
</div>

  </dl>
</div>
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Methods</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="practice_registrations.for_patient_on">
    <strong>for_patient_on(</strong>date<strong>)</strong>
    <a class="headerlink" href="#practice_registrations.for_patient_on" title="Permanent link">🔗</a>
    <code></code>
  </dt>
  <dd markdown="block">
Return each patient's practice registration as it was on the supplied date.

Where a patient is registered with multiple practices we prefer the most recent
registration and then, if there are multiple of these, the one with the longest
duration. If there's still an exact tie we choose arbitrarily based on the
practice ID.
    <details markdown="block">
    <summary>View method definition</summary>
```py
spanning_regs = practice_registrations.where(practice_registrations.start_date <= date).except_where(
    practice_registrations.end_date < date
)
ordered_regs = spanning_regs.sort_by(
    practice_registrations.start_date,
    practice_registrations.end_date,
    practice_registrations.practice_pseudo_id,
)
return ordered_regs.last_for_patient()

```
    </details>
  </dd>
</div>

<div markdown="block">
  <dt id="practice_registrations.exists_for_patient_on">
    <strong>exists_for_patient_on(</strong>date<strong>)</strong>
    <a class="headerlink" href="#practice_registrations.exists_for_patient_on" title="Permanent link">🔗</a>
    <code></code>
  </dt>
  <dd markdown="block">
Returns whether a person was registered with a practice on the supplied date.

NB. The implementation currently uses `spanning()`. It would also have been
valid to implement as
`practice_registrations.for_patient_on(date).exists_for_patient()`, but for
internal reasons that is less efficient.
    <details markdown="block">
    <summary>View method definition</summary>
```py
return practice_registrations.spanning(date, date).exists_for_patient()

```
    </details>
  </dd>
</div>

<div markdown="block">
  <dt id="practice_registrations.spanning">
    <strong>spanning(</strong>start_date, end_date<strong>)</strong>
    <a class="headerlink" href="#practice_registrations.spanning" title="Permanent link">🔗</a>
    <code></code>
  </dt>
  <dd markdown="block">
Filter registrations to just those spanning the entire period between
`start_date` and `end_date`.
    <details markdown="block">
    <summary>View method definition</summary>
```py
return practice_registrations.where(
    practice_registrations.start_date.is_on_or_before(start_date)
    & (practice_registrations.end_date.is_after(end_date) | practice_registrations.end_date.is_null())
)

```
    </details>
  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## vaccinations

This table contains information on administered vaccinations,
identified using SNOMED-CT codes for the vaccination procedure.

Vaccinations may also be queried by product code using the
[medications table](#medications).

Vaccinations that were administered at work or in a pharmacy might not be
included in this table.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="vaccinations.date">
    <strong>date</strong>
    <a class="headerlink" href="#vaccinations.date" title="Permanent link">🔗</a>
    <code>date</code>
  </dt>
  <dd markdown="block">
The date the vaccination was administered.

  </dd>
</div>

<div markdown="block">
  <dt id="vaccinations.procedure_code">
    <strong>procedure_code</strong>
    <a class="headerlink" href="#vaccinations.procedure_code" title="Permanent link">🔗</a>
    <code>SNOMED-CT code</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

  </dl>
</div>
