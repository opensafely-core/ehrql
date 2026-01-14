---
search:
  boost: 0.5
---

# <strong>raw.tpp</strong> schema

Available on backends: [**TPP**](../backends.md#tpp)

This schema defines the data (both primary care and externally linked) available in the
OpenSAFELY-TPP backend. For more information about this backend, see
"[SystmOne Primary Care](https://docs.opensafely.org/data-sources/systmone/)".

The data provided by this schema are minimally transformed. They are very close to the
data provided by the underlying database tables. They are provided for data development
and data curation purposes.

``` {.python .copy title='To use this schema in an ehrQL file:'}
from ehrql.tables.raw.tpp import (
    apcs_cost_historical,
    apcs_historical,
    isaric,
    medications,
    ons_deaths,
    repeat_medications,
    wl_clockstops,
    wl_openpathways,
)
```

<p class="dimension-indicator"><code>many rows per patient</code></p>
## apcs_cost_historical

This table contains some historical APCS cost data.

It has been exposed to users for data exploration, and may be removed in future.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="apcs_cost_historical.apcs_ident" markdown="block">
   <strong>apcs_ident</strong>
   <a class="headerlink" href="#apcs_cost_historical.apcs_ident" title="Permanent link">🔗</a>
   <code markdown="block">[integer](../language.md#IntEventSeries)</code>
  </dt>
  <dd markdown="block">


 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="apcs_cost_historical.grand_total_payment_mff" markdown="block">
   <strong>grand_total_payment_mff</strong>
   <a class="headerlink" href="#apcs_cost_historical.grand_total_payment_mff" title="Permanent link">🔗</a>
   <code markdown="block">[float](../language.md#FloatEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="apcs_cost_historical.tariff_initial_amount" markdown="block">
   <strong>tariff_initial_amount</strong>
   <a class="headerlink" href="#apcs_cost_historical.tariff_initial_amount" title="Permanent link">🔗</a>
   <code markdown="block">[float](../language.md#FloatEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="apcs_cost_historical.tariff_total_payment" markdown="block">
   <strong>tariff_total_payment</strong>
   <a class="headerlink" href="#apcs_cost_historical.tariff_total_payment" title="Permanent link">🔗</a>
   <code markdown="block">[float](../language.md#FloatEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="apcs_cost_historical.admission_date" markdown="block">
   <strong>admission_date</strong>
   <a class="headerlink" href="#apcs_cost_historical.admission_date" title="Permanent link">🔗</a>
   <code markdown="block">[date](../language.md#DateEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="apcs_cost_historical.discharge_date" markdown="block">
   <strong>discharge_date</strong>
   <a class="headerlink" href="#apcs_cost_historical.discharge_date" title="Permanent link">🔗</a>
   <code markdown="block">[date](../language.md#DateEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## apcs_historical

This table contains some historical APCS data.

It has been exposed to users for data exploration, and may be removed in future.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="apcs_historical.apcs_ident" markdown="block">
   <strong>apcs_ident</strong>
   <a class="headerlink" href="#apcs_historical.apcs_ident" title="Permanent link">🔗</a>
   <code markdown="block">[integer](../language.md#IntEventSeries)</code>
  </dt>
  <dd markdown="block">


 * Never `NULL`
  </dd>
</div>

<div markdown="block">
  <dt id="apcs_historical.admission_date" markdown="block">
   <strong>admission_date</strong>
   <a class="headerlink" href="#apcs_historical.admission_date" title="Permanent link">🔗</a>
   <code markdown="block">[date](../language.md#DateEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="apcs_historical.discharge_date" markdown="block">
   <strong>discharge_date</strong>
   <a class="headerlink" href="#apcs_historical.discharge_date" title="Permanent link">🔗</a>
   <code markdown="block">[date](../language.md#DateEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="apcs_historical.spell_core_hrg_sus" markdown="block">
   <strong>spell_core_hrg_sus</strong>
   <a class="headerlink" href="#apcs_historical.spell_core_hrg_sus" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## isaric

!!! warning "Access to this table requires the `isaric` permission"

    Access to ISARIC data is usually agreed at the project application stage.  If
    you're unsure as to whether you do or should have access please speak to your
    co-pilot or to OpenSAFELY support.

ISARIC is a dataset of COVID-19-related hospital admissions,
with coverage across the majority of hospitals across the UK,
including much richer clinical information
than collected in national Hospital Episode Statistics datasets.

The data in this table covers a subset of the ISARIC data columns available in TPP,
sourced from the [ISARIC COVID-19 Clinical Database][isaric_clinical_database].

All columns included have deliberately been taken as strings while in a preliminary phase.

Descriptions taken from [CCP_REDCap_ISARIC_data_dictionary_codebook.pdf][isaric_ddc_pdf]
which also has information on the data expected for each column.

!!! warning
    ISARIC data can only be used in collaboration with ISARIC researchers
    who must be involved in working on the study and writing it up.

Refer to the [OpenSAFELY database build report][opensafely_database_build_report]
to see when this data was last updated.

[isaric_ddc_pdf]: https://github.com/isaric4c/wiki/blob/d6b87d59a277cf2f6deedeb5e8c1a970dbb970a3/ISARIC/CCP_REDCap_ISARIC_data_dictionary_codebook.pdf
[isaric_clinical_database]: https://isaric.org/research/covid-19-clinical-research-resources/covid-19-data-management-hosting/
[opensafely_database_build_report]: https://reports.opensafely.org/reports/opensafely-tpp-database-builds/
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="isaric.age" markdown="block">
   <strong>age</strong>
   <a class="headerlink" href="#isaric.age" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Age

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.age_factor" markdown="block">
   <strong>age_factor</strong>
   <a class="headerlink" href="#isaric.age_factor" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
TODO

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.calc_age" markdown="block">
   <strong>calc_age</strong>
   <a class="headerlink" href="#isaric.calc_age" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Calculated age (comparing date of birth with date of enrolment). May be inaccurate if a date of February 29 is used.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.sex" markdown="block">
   <strong>sex</strong>
   <a class="headerlink" href="#isaric.sex" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Sex at birth.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.ethnic___1" markdown="block">
   <strong>ethnic___1</strong>
   <a class="headerlink" href="#isaric.ethnic___1" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Ethnic group: Arab.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.ethnic___2" markdown="block">
   <strong>ethnic___2</strong>
   <a class="headerlink" href="#isaric.ethnic___2" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Ethnic group: Black.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.ethnic___3" markdown="block">
   <strong>ethnic___3</strong>
   <a class="headerlink" href="#isaric.ethnic___3" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Ethnic group: East Asian.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.ethnic___4" markdown="block">
   <strong>ethnic___4</strong>
   <a class="headerlink" href="#isaric.ethnic___4" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Ethnic group: South Asian.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.ethnic___5" markdown="block">
   <strong>ethnic___5</strong>
   <a class="headerlink" href="#isaric.ethnic___5" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Ethnic group: West Asian.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.ethnic___6" markdown="block">
   <strong>ethnic___6</strong>
   <a class="headerlink" href="#isaric.ethnic___6" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Ethnic group: Latin American.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.ethnic___7" markdown="block">
   <strong>ethnic___7</strong>
   <a class="headerlink" href="#isaric.ethnic___7" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Ethnic group: White.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.ethnic___8" markdown="block">
   <strong>ethnic___8</strong>
   <a class="headerlink" href="#isaric.ethnic___8" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Ethnic group: Aboriginal/First Nations.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.ethnic___9" markdown="block">
   <strong>ethnic___9</strong>
   <a class="headerlink" href="#isaric.ethnic___9" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Ethnic group: Other.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.ethnic___10" markdown="block">
   <strong>ethnic___10</strong>
   <a class="headerlink" href="#isaric.ethnic___10" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Ethnic group: N/A.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.covid19_vaccine" markdown="block">
   <strong>covid19_vaccine</strong>
   <a class="headerlink" href="#isaric.covid19_vaccine" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Has the patient received a Covid-19 vaccine (open label licenced product)?

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.covid19_vaccined" markdown="block">
   <strong>covid19_vaccined</strong>
   <a class="headerlink" href="#isaric.covid19_vaccined" title="Permanent link">🔗</a>
   <code markdown="block">[date](../language.md#DateEventSeries)</code>
  </dt>
  <dd markdown="block">
Date first vaccine given (Covid-19) if known.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.covid19_vaccine2d" markdown="block">
   <strong>covid19_vaccine2d</strong>
   <a class="headerlink" href="#isaric.covid19_vaccine2d" title="Permanent link">🔗</a>
   <code markdown="block">[date](../language.md#DateEventSeries)</code>
  </dt>
  <dd markdown="block">
Date second vaccine given (Covid-19) if known.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.covid19_vaccined_nk" markdown="block">
   <strong>covid19_vaccined_nk</strong>
   <a class="headerlink" href="#isaric.covid19_vaccined_nk" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
First vaccine given (Covid-19) but date not known.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.corona_ieorres" markdown="block">
   <strong>corona_ieorres</strong>
   <a class="headerlink" href="#isaric.corona_ieorres" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Suspected or proven infection with pathogen of public health interest.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.coriona_ieorres2" markdown="block">
   <strong>coriona_ieorres2</strong>
   <a class="headerlink" href="#isaric.coriona_ieorres2" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Proven or high likelihood of infection with pathogen of public health interest.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.coriona_ieorres3" markdown="block">
   <strong>coriona_ieorres3</strong>
   <a class="headerlink" href="#isaric.coriona_ieorres3" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Proven infection with pathogen of public health interest.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.inflammatory_mss" markdown="block">
   <strong>inflammatory_mss</strong>
   <a class="headerlink" href="#isaric.inflammatory_mss" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Adult or child who meets case definition for inflammatory multi-system syndrome (MIS-C/MIS-A).

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.cestdat" markdown="block">
   <strong>cestdat</strong>
   <a class="headerlink" href="#isaric.cestdat" title="Permanent link">🔗</a>
   <code markdown="block">[date](../language.md#DateEventSeries)</code>
  </dt>
  <dd markdown="block">
Onset date of first/earliest symptom.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.chrincard" markdown="block">
   <strong>chrincard</strong>
   <a class="headerlink" href="#isaric.chrincard" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Chronic cardiac disease, including congenital heart disease (not hypertension).

 * Possible values: `YES`, `NO`, `Unknown`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.hypertension_mhyn" markdown="block">
   <strong>hypertension_mhyn</strong>
   <a class="headerlink" href="#isaric.hypertension_mhyn" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Hypertension (physician diagnosed).

 * Possible values: `YES`, `NO`, `Unknown`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.chronicpul_mhyn" markdown="block">
   <strong>chronicpul_mhyn</strong>
   <a class="headerlink" href="#isaric.chronicpul_mhyn" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Chronic pulmonary disease (not asthma).

 * Possible values: `YES`, `NO`, `Unknown`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.asthma_mhyn" markdown="block">
   <strong>asthma_mhyn</strong>
   <a class="headerlink" href="#isaric.asthma_mhyn" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Asthma (physician diagnosed).

 * Possible values: `YES`, `NO`, `Unknown`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.renal_mhyn" markdown="block">
   <strong>renal_mhyn</strong>
   <a class="headerlink" href="#isaric.renal_mhyn" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Chronic kidney disease.

 * Possible values: `YES`, `NO`, `Unknown`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.mildliver" markdown="block">
   <strong>mildliver</strong>
   <a class="headerlink" href="#isaric.mildliver" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Mild liver disease.

 * Possible values: `YES`, `NO`, `Unknown`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.modliv" markdown="block">
   <strong>modliv</strong>
   <a class="headerlink" href="#isaric.modliv" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Moderate or severe liver disease

 * Possible values: `YES`, `NO`, `Unknown`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.chronicneu_mhyn" markdown="block">
   <strong>chronicneu_mhyn</strong>
   <a class="headerlink" href="#isaric.chronicneu_mhyn" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Chronic neurological disorder.

 * Possible values: `YES`, `NO`, `Unknown`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.malignantneo_mhyn" markdown="block">
   <strong>malignantneo_mhyn</strong>
   <a class="headerlink" href="#isaric.malignantneo_mhyn" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Malignant neoplasm.

 * Possible values: `YES`, `NO`, `Unknown`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.chronichaemo_mhyn" markdown="block">
   <strong>chronichaemo_mhyn</strong>
   <a class="headerlink" href="#isaric.chronichaemo_mhyn" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Chronic haematologic disease.

 * Possible values: `YES`, `NO`, `Unknown`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.aidshiv_mhyn" markdown="block">
   <strong>aidshiv_mhyn</strong>
   <a class="headerlink" href="#isaric.aidshiv_mhyn" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
AIDS/HIV.

 * Possible values: `YES`, `NO`, `Unknown`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.obesity_mhyn" markdown="block">
   <strong>obesity_mhyn</strong>
   <a class="headerlink" href="#isaric.obesity_mhyn" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Obesity (as defined by clinical staff).

 * Possible values: `YES`, `NO`, `Unknown`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.diabetes_type_mhyn" markdown="block">
   <strong>diabetes_type_mhyn</strong>
   <a class="headerlink" href="#isaric.diabetes_type_mhyn" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Diabetes and type.

 * Possible values: `NO`, `1`, `2`, `N/K`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.diabetescom_mhyn" markdown="block">
   <strong>diabetescom_mhyn</strong>
   <a class="headerlink" href="#isaric.diabetescom_mhyn" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Diabetes with complications.

 * Possible values: `YES`, `NO`, `Unknown`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.diabetes_mhyn" markdown="block">
   <strong>diabetes_mhyn</strong>
   <a class="headerlink" href="#isaric.diabetes_mhyn" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Diabetes without complications.

 * Possible values: `YES`, `NO`, `Unknown`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.rheumatologic_mhyn" markdown="block">
   <strong>rheumatologic_mhyn</strong>
   <a class="headerlink" href="#isaric.rheumatologic_mhyn" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Rheumatologic disorder.

 * Possible values: `YES`, `NO`, `Unknown`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.dementia_mhyn" markdown="block">
   <strong>dementia_mhyn</strong>
   <a class="headerlink" href="#isaric.dementia_mhyn" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Dementia.

 * Possible values: `YES`, `NO`, `Unknown`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.malnutrition_mhyn" markdown="block">
   <strong>malnutrition_mhyn</strong>
   <a class="headerlink" href="#isaric.malnutrition_mhyn" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Malnutrition.

 * Possible values: `YES`, `NO`, `Unknown`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.smoking_mhyn" markdown="block">
   <strong>smoking_mhyn</strong>
   <a class="headerlink" href="#isaric.smoking_mhyn" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Smoking.

 * Possible values: `Yes`, `Never Smoked`, `Former Smoker`, `N/K`
  </dd>
</div>

<div markdown="block">
  <dt id="isaric.hostdat" markdown="block">
   <strong>hostdat</strong>
   <a class="headerlink" href="#isaric.hostdat" title="Permanent link">🔗</a>
   <code markdown="block">[date](../language.md#DateEventSeries)</code>
  </dt>
  <dd markdown="block">
Admission date at this facility.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.hooccur" markdown="block">
   <strong>hooccur</strong>
   <a class="headerlink" href="#isaric.hooccur" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Transfer from other facility?

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.hostdat_transfer" markdown="block">
   <strong>hostdat_transfer</strong>
   <a class="headerlink" href="#isaric.hostdat_transfer" title="Permanent link">🔗</a>
   <code markdown="block">[date](../language.md#DateEventSeries)</code>
  </dt>
  <dd markdown="block">
Admission date at previous facility.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.hostdat_transfernk" markdown="block">
   <strong>hostdat_transfernk</strong>
   <a class="headerlink" href="#isaric.hostdat_transfernk" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Admission date at previous facility not known.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.readm_cov19" markdown="block">
   <strong>readm_cov19</strong>
   <a class="headerlink" href="#isaric.readm_cov19" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Is the patient being readmitted with Covid-19?

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.dsstdat" markdown="block">
   <strong>dsstdat</strong>
   <a class="headerlink" href="#isaric.dsstdat" title="Permanent link">🔗</a>
   <code markdown="block">[date](../language.md#DateEventSeries)</code>
  </dt>
  <dd markdown="block">
Date of enrolment.

  </dd>
</div>

<div markdown="block">
  <dt id="isaric.dsstdtc" markdown="block">
   <strong>dsstdtc</strong>
   <a class="headerlink" href="#isaric.dsstdtc" title="Permanent link">🔗</a>
   <code markdown="block">[date](../language.md#DateEventSeries)</code>
  </dt>
  <dd markdown="block">
Outcome date.

  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## medications

This table is an extension of the [`tpp.medications`](../schemas/tpp.md#medications) table.

It contains additional fields whose contents are not yet well understood, with the
aim of facilitating exploratory analysis for data development and data curation
purposes.

By default, only medications with a consultation `date`on or before the date of the patient's
last de-registration from an activated GP practice (a practice that has acknowledged the
new non-COVID directions) are included.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="medications.date" markdown="block">
   <strong>date</strong>
   <a class="headerlink" href="#medications.date" title="Permanent link">🔗</a>
   <code markdown="block">[date](../language.md#DateEventSeries)</code>
  </dt>
  <dd markdown="block">
Date of the consultation associated with this event

  </dd>
</div>

<div markdown="block">
  <dt id="medications.dmd_code" markdown="block">
   <strong>dmd_code</strong>
   <a class="headerlink" href="#medications.dmd_code" title="Permanent link">🔗</a>
   <code markdown="block">[dm+d code](../language.md#CodeEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="medications.consultation_id" markdown="block">
   <strong>consultation_id</strong>
   <a class="headerlink" href="#medications.consultation_id" title="Permanent link">🔗</a>
   <code markdown="block">[integer](../language.md#IntEventSeries)</code>
  </dt>
  <dd markdown="block">
ID of the consultation associated with this event

  </dd>
</div>

<div markdown="block">
  <dt id="medications.medication_status" markdown="block">
   <strong>medication_status</strong>
   <a class="headerlink" href="#medications.medication_status" title="Permanent link">🔗</a>
   <code markdown="block">[integer](../language.md#IntEventSeries)</code>
  </dt>
  <dd markdown="block">
Medication status. The values might map to the descriptions below from the
data dictionary.  Note that this still needs to be confirmed.

* 0 - Normal
* 4 - Historical
* 5 - Blue script
* 6 - Private
* 7 - Not in possession
* 8 - Repeat dispensed
* 9 - In possession
* 10 - Dental
* 11 - Hospital
* 12 - Problem substance
* 13 - From patient group direction
* 14 - To take out
* 15 - On admission
* 16 - Regular medication
* 17 - As required medication
* 18 - Variable dose medication
* 19 - Rate-controlled single regular
* 20 - Only once
* 21 - Outpatient
* 22 - Rate-controlled multiple regular
* 23 - Rate-controlled multiple only once
* 24 - Rate-controlled single only once
* 25 - Placeholder
* 26 - Unconfirmed
* 27 - Infusion
* 28 - Reducing dose blue script

 * Always >= 0 and <= 28
  </dd>
</div>

<div markdown="block">
  <dt id="medications.quantity" markdown="block">
   <strong>quantity</strong>
   <a class="headerlink" href="#medications.quantity" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Quantity as structured text. The precise structure is yet to be determined and
it may be that historical records are less well structured than more recent
ones. Examples of the kinds of value you might find are:
```
10ml - 0.5%
100 mililitres
1 pack of 28 capsule(s)
63 tablet
21 tablet(s) - 400mg
1 op - 8.75 cm x 1 m (e)
```

  </dd>
</div>

<div markdown="block">
  <dt id="medications.repeat_medication_id" markdown="block">
   <strong>repeat_medication_id</strong>
   <a class="headerlink" href="#medications.repeat_medication_id" title="Permanent link">🔗</a>
   <code markdown="block">[integer](../language.md#IntEventSeries)</code>
  </dt>
  <dd markdown="block">
ID of the associated repeat medication record (zero if none exists)

  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## ons_deaths

Registered deaths

Date and cause of death based on information recorded when deaths are
certified and registered in England and Wales from February 2019 onwards.
The data provider is the Office for National Statistics (ONS).
This table is updated approximately weekly in OpenSAFELY.

This table includes the underlying cause of death, place of death, and up to
15 medical conditions mentioned on the death certificate.
These codes (`cause_of_death_01` to `cause_of_death_15`) are not ordered meaningfully.

More information about this table can be found in following documents provided by the ONS:

- [Information collected at death registration](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/methodologies/userguidetomortalitystatisticsjuly2017#information-collected-at-death-registration)
- [User guide to mortality statistics](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/methodologies/userguidetomortalitystatisticsjuly2017)
- [How death registrations are recorded and stored by ONS](https://www.ons.gov.uk/aboutus/transparencyandgovernance/freedomofinformationfoi/howdeathregistrationsarerecordedandstoredbyons)

In the associated database table [ONS_Deaths](https://reports.opensafely.org/reports/opensafely-tpp-database-schema/#ONS_Deaths),
a small number of patients have multiple registered deaths.
This table contains all registered deaths.
The `ehrql.tables.ons_deaths` table contains the earliest registered death.

!!! tip
    To return one row per patient from `ehrql.tables.raw.tpp.ons_deaths`,
    for example the latest registered death, you can use:

    ```py
    ons_deaths.sort_by(ons_deaths.date).last_for_patient()
    ```
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="ons_deaths.date" markdown="block">
   <strong>date</strong>
   <a class="headerlink" href="#ons_deaths.date" title="Permanent link">🔗</a>
   <code markdown="block">[date](../language.md#DateEventSeries)</code>
  </dt>
  <dd markdown="block">
Patient's date of death.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.place" markdown="block">
   <strong>place</strong>
   <a class="headerlink" href="#ons_deaths.place" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Patient's place of death.

 * Possible values: `Care Home`, `Elsewhere`, `Home`, `Hospice`, `Hospital`, `Other communal establishment`
  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.underlying_cause_of_death" markdown="block">
   <strong>underlying_cause_of_death</strong>
   <a class="headerlink" href="#ons_deaths.underlying_cause_of_death" title="Permanent link">🔗</a>
   <code markdown="block">[ICD-10 code](../language.md#CodeEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_01" markdown="block">
   <strong>cause_of_death_01</strong>
   <a class="headerlink" href="#ons_deaths.cause_of_death_01" title="Permanent link">🔗</a>
   <code markdown="block">[ICD-10 code](../language.md#CodeEventSeries)</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_02" markdown="block">
   <strong>cause_of_death_02</strong>
   <a class="headerlink" href="#ons_deaths.cause_of_death_02" title="Permanent link">🔗</a>
   <code markdown="block">[ICD-10 code](../language.md#CodeEventSeries)</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_03" markdown="block">
   <strong>cause_of_death_03</strong>
   <a class="headerlink" href="#ons_deaths.cause_of_death_03" title="Permanent link">🔗</a>
   <code markdown="block">[ICD-10 code](../language.md#CodeEventSeries)</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_04" markdown="block">
   <strong>cause_of_death_04</strong>
   <a class="headerlink" href="#ons_deaths.cause_of_death_04" title="Permanent link">🔗</a>
   <code markdown="block">[ICD-10 code](../language.md#CodeEventSeries)</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_05" markdown="block">
   <strong>cause_of_death_05</strong>
   <a class="headerlink" href="#ons_deaths.cause_of_death_05" title="Permanent link">🔗</a>
   <code markdown="block">[ICD-10 code](../language.md#CodeEventSeries)</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_06" markdown="block">
   <strong>cause_of_death_06</strong>
   <a class="headerlink" href="#ons_deaths.cause_of_death_06" title="Permanent link">🔗</a>
   <code markdown="block">[ICD-10 code](../language.md#CodeEventSeries)</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_07" markdown="block">
   <strong>cause_of_death_07</strong>
   <a class="headerlink" href="#ons_deaths.cause_of_death_07" title="Permanent link">🔗</a>
   <code markdown="block">[ICD-10 code](../language.md#CodeEventSeries)</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_08" markdown="block">
   <strong>cause_of_death_08</strong>
   <a class="headerlink" href="#ons_deaths.cause_of_death_08" title="Permanent link">🔗</a>
   <code markdown="block">[ICD-10 code](../language.md#CodeEventSeries)</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_09" markdown="block">
   <strong>cause_of_death_09</strong>
   <a class="headerlink" href="#ons_deaths.cause_of_death_09" title="Permanent link">🔗</a>
   <code markdown="block">[ICD-10 code](../language.md#CodeEventSeries)</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_10" markdown="block">
   <strong>cause_of_death_10</strong>
   <a class="headerlink" href="#ons_deaths.cause_of_death_10" title="Permanent link">🔗</a>
   <code markdown="block">[ICD-10 code](../language.md#CodeEventSeries)</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_11" markdown="block">
   <strong>cause_of_death_11</strong>
   <a class="headerlink" href="#ons_deaths.cause_of_death_11" title="Permanent link">🔗</a>
   <code markdown="block">[ICD-10 code](../language.md#CodeEventSeries)</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_12" markdown="block">
   <strong>cause_of_death_12</strong>
   <a class="headerlink" href="#ons_deaths.cause_of_death_12" title="Permanent link">🔗</a>
   <code markdown="block">[ICD-10 code](../language.md#CodeEventSeries)</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_13" markdown="block">
   <strong>cause_of_death_13</strong>
   <a class="headerlink" href="#ons_deaths.cause_of_death_13" title="Permanent link">🔗</a>
   <code markdown="block">[ICD-10 code](../language.md#CodeEventSeries)</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_14" markdown="block">
   <strong>cause_of_death_14</strong>
   <a class="headerlink" href="#ons_deaths.cause_of_death_14" title="Permanent link">🔗</a>
   <code markdown="block">[ICD-10 code](../language.md#CodeEventSeries)</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

<div markdown="block">
  <dt id="ons_deaths.cause_of_death_15" markdown="block">
   <strong>cause_of_death_15</strong>
   <a class="headerlink" href="#ons_deaths.cause_of_death_15" title="Permanent link">🔗</a>
   <code markdown="block">[ICD-10 code](../language.md#CodeEventSeries)</code>
  </dt>
  <dd markdown="block">
Medical condition mentioned on the death certificate.

  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## repeat_medications

This table is exposed for data development and data curation purposes. Its contents
and not yet well understood and so it should not yet be used for research.

By default, only repeat medications with a consultation `date` on or before the date of the patient's
last de-registration from an activated GP practice (a practice that has acknowledged the
new non-COVID directions) are included.
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="repeat_medications.date" markdown="block">
   <strong>date</strong>
   <a class="headerlink" href="#repeat_medications.date" title="Permanent link">🔗</a>
   <code markdown="block">[date](../language.md#DateEventSeries)</code>
  </dt>
  <dd markdown="block">
Date of the consultation associated with this event

  </dd>
</div>

<div markdown="block">
  <dt id="repeat_medications.dmd_code" markdown="block">
   <strong>dmd_code</strong>
   <a class="headerlink" href="#repeat_medications.dmd_code" title="Permanent link">🔗</a>
   <code markdown="block">[dm+d code](../language.md#CodeEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="repeat_medications.consultation_id" markdown="block">
   <strong>consultation_id</strong>
   <a class="headerlink" href="#repeat_medications.consultation_id" title="Permanent link">🔗</a>
   <code markdown="block">[integer](../language.md#IntEventSeries)</code>
  </dt>
  <dd markdown="block">
ID of the consultation associated with this event

  </dd>
</div>

<div markdown="block">
  <dt id="repeat_medications.repeat_medication_id" markdown="block">
   <strong>repeat_medication_id</strong>
   <a class="headerlink" href="#repeat_medications.repeat_medication_id" title="Permanent link">🔗</a>
   <code markdown="block">[integer](../language.md#IntEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="repeat_medications.medication_status" markdown="block">
   <strong>medication_status</strong>
   <a class="headerlink" href="#repeat_medications.medication_status" title="Permanent link">🔗</a>
   <code markdown="block">[integer](../language.md#IntEventSeries)</code>
  </dt>
  <dd markdown="block">
Medication status. The values might map to the descriptions below from the
data dictionary.  Note that this still needs to be confirmed.

* 0 - Normal
* 4 - Historical
* 5 - Blue script
* 6 - Private
* 7 - Not in possession
* 8 - Repeat dispensed
* 9 - In possession
* 10 - Dental
* 11 - Hospital
* 12 - Problem substance
* 13 - From patient group direction
* 14 - To take out
* 15 - On admission
* 16 - Regular medication
* 17 - As required medication
* 18 - Variable dose medication
* 19 - Rate-controlled single regular
* 20 - Only once
* 21 - Outpatient
* 22 - Rate-controlled multiple regular
* 23 - Rate-controlled multiple only once
* 24 - Rate-controlled single only once
* 25 - Placeholder
* 26 - Unconfirmed
* 27 - Infusion
* 28 - Reducing dose blue script

 * Always >= 0 and <= 28
  </dd>
</div>

<div markdown="block">
  <dt id="repeat_medications.quantity" markdown="block">
   <strong>quantity</strong>
   <a class="headerlink" href="#repeat_medications.quantity" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">
Quantity as structured text. The precise structure is yet to be determined and
it may be that historical records are less well structured than more recent
ones. Examples of the kinds of value you might find are:
```
10ml - 0.5%
100 mililitres
1 pack of 28 capsule(s)
63 tablet
21 tablet(s) - 400mg
1 op - 8.75 cm x 1 m (e)
```

  </dd>
</div>

<div markdown="block">
  <dt id="repeat_medications.start_date" markdown="block">
   <strong>start_date</strong>
   <a class="headerlink" href="#repeat_medications.start_date" title="Permanent link">🔗</a>
   <code markdown="block">[date](../language.md#DateEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="repeat_medications.end_date" markdown="block">
   <strong>end_date</strong>
   <a class="headerlink" href="#repeat_medications.end_date" title="Permanent link">🔗</a>
   <code markdown="block">[date](../language.md#DateEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## wl_clockstops

National Waiting List Clock Stops

!!! warning "Access to this table requires the `waiting_list` permission"

    Access to Waiting List data is usually agreed at the project application stage.
    If you're unsure as to whether you do or should have access please speak to your
    co-pilot or to OpenSAFELY support.

The columns in this table have the same data types as the columns in [the associated
database table][wl_clockstops_raw_1]. The three "pseudo" columns are small
exceptions, as they are converted from binary columns to string columns.

[wl_clockstops_raw_1]: https://reports.opensafely.org/reports/opensafely-tpp-database-schema/#WL_ClockStops
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="wl_clockstops.activity_treatment_function_code" markdown="block">
   <strong>activity_treatment_function_code</strong>
   <a class="headerlink" href="#wl_clockstops.activity_treatment_function_code" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.priority_type_code" markdown="block">
   <strong>priority_type_code</strong>
   <a class="headerlink" href="#wl_clockstops.priority_type_code" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.pseudo_organisation_code_patient_pathway_identifier_issuer" markdown="block">
   <strong>pseudo_organisation_code_patient_pathway_identifier_issuer</strong>
   <a class="headerlink" href="#wl_clockstops.pseudo_organisation_code_patient_pathway_identifier_issuer" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.pseudo_patient_pathway_identifier" markdown="block">
   <strong>pseudo_patient_pathway_identifier</strong>
   <a class="headerlink" href="#wl_clockstops.pseudo_patient_pathway_identifier" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.pseudo_referral_identifier" markdown="block">
   <strong>pseudo_referral_identifier</strong>
   <a class="headerlink" href="#wl_clockstops.pseudo_referral_identifier" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.referral_request_received_date" markdown="block">
   <strong>referral_request_received_date</strong>
   <a class="headerlink" href="#wl_clockstops.referral_request_received_date" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.referral_to_treatment_period_end_date" markdown="block">
   <strong>referral_to_treatment_period_end_date</strong>
   <a class="headerlink" href="#wl_clockstops.referral_to_treatment_period_end_date" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.referral_to_treatment_period_start_date" markdown="block">
   <strong>referral_to_treatment_period_start_date</strong>
   <a class="headerlink" href="#wl_clockstops.referral_to_treatment_period_start_date" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.source_of_referral_for_outpatients" markdown="block">
   <strong>source_of_referral_for_outpatients</strong>
   <a class="headerlink" href="#wl_clockstops.source_of_referral_for_outpatients" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.waiting_list_type" markdown="block">
   <strong>waiting_list_type</strong>
   <a class="headerlink" href="#wl_clockstops.waiting_list_type" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_clockstops.week_ending_date" markdown="block">
   <strong>week_ending_date</strong>
   <a class="headerlink" href="#wl_clockstops.week_ending_date" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

  </dl>
</div>


<p class="dimension-indicator"><code>many rows per patient</code></p>
## wl_openpathways

National Waiting List Open Pathways

!!! warning "Access to this table requires the `waiting_list` permission"

    Access to Waiting List data is usually agreed at the project application stage.
    If you're unsure as to whether you do or should have access please speak to your
    co-pilot or to OpenSAFELY support.

The columns in this table have the same data types as the columns in [the associated
database table][wl_openpathways_raw_1]. The three "pseudo" columns are small
exceptions, as they are converted from binary columns to string columns.

[wl_openpathways_raw_1]: https://reports.opensafely.org/reports/opensafely-tpp-database-schema/#WL_OpenPathways
<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="wl_openpathways.activity_treatment_function_code" markdown="block">
   <strong>activity_treatment_function_code</strong>
   <a class="headerlink" href="#wl_openpathways.activity_treatment_function_code" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.current_pathway_period_start_date" markdown="block">
   <strong>current_pathway_period_start_date</strong>
   <a class="headerlink" href="#wl_openpathways.current_pathway_period_start_date" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.priority_type_code" markdown="block">
   <strong>priority_type_code</strong>
   <a class="headerlink" href="#wl_openpathways.priority_type_code" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.pseudo_organisation_code_patient_pathway_identifier_issuer" markdown="block">
   <strong>pseudo_organisation_code_patient_pathway_identifier_issuer</strong>
   <a class="headerlink" href="#wl_openpathways.pseudo_organisation_code_patient_pathway_identifier_issuer" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.pseudo_patient_pathway_identifier" markdown="block">
   <strong>pseudo_patient_pathway_identifier</strong>
   <a class="headerlink" href="#wl_openpathways.pseudo_patient_pathway_identifier" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.pseudo_referral_identifier" markdown="block">
   <strong>pseudo_referral_identifier</strong>
   <a class="headerlink" href="#wl_openpathways.pseudo_referral_identifier" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.referral_request_received_date" markdown="block">
   <strong>referral_request_received_date</strong>
   <a class="headerlink" href="#wl_openpathways.referral_request_received_date" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.referral_to_treatment_period_end_date" markdown="block">
   <strong>referral_to_treatment_period_end_date</strong>
   <a class="headerlink" href="#wl_openpathways.referral_to_treatment_period_end_date" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.referral_to_treatment_period_start_date" markdown="block">
   <strong>referral_to_treatment_period_start_date</strong>
   <a class="headerlink" href="#wl_openpathways.referral_to_treatment_period_start_date" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.source_of_referral" markdown="block">
   <strong>source_of_referral</strong>
   <a class="headerlink" href="#wl_openpathways.source_of_referral" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.waiting_list_type" markdown="block">
   <strong>waiting_list_type</strong>
   <a class="headerlink" href="#wl_openpathways.waiting_list_type" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

<div markdown="block">
  <dt id="wl_openpathways.week_ending_date" markdown="block">
   <strong>week_ending_date</strong>
   <a class="headerlink" href="#wl_openpathways.week_ending_date" title="Permanent link">🔗</a>
   <code markdown="block">[string](../language.md#StrEventSeries)</code>
  </dt>
  <dd markdown="block">


  </dd>
</div>

  </dl>
</div>
