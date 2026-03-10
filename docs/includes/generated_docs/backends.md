## TPP
<small class="subtitle">
  <a href="https://github.com/opensafely-core/ehrql/blob/main/ehrql/backends/tpp.py">
    <code>ehrql.backends.tpp.TPPBackend</code>
  </a>
</small>

[TPP](https://tpp-uk.com/) are the developers and operators of the
[SystmOne](https://tpp-uk.com/products/) EHR platform. The ehrQL TPP backend
provides access to primary care data from SystmOne, plus data linked from other
sources.

### Patients included in the TPP backend

SystmOne is a primary care clinical information system
used by roughly one third of GP practices in England,
with records for approximately 44% of the English population.

Only patients with a full GMS (General Medical Services) registration are included.

We have registration history for:

* all patients currently registered at a TPP practice
* all patients registered at a TPP practice any time from 1 Jan 2009 onwards:
    * who have since de-registered
    * who have since died

A patient can be registered with zero, one, or more than one practices at a given
time. For instance, students are often registered with a practice at home and a
practice at university.

Patients with [Type 1 Opt Outs](https://docs.opensafely.org/type-one-opt-outs/) or
[National Data Opt Outs](https://docs.opensafely.org/national-data-opt-outs/) are
excluded unless an OpenSAFELY project has permission to access these data. For further
information, see the [OpenSAFELY data](https://docs.opensafely.org/opensafely-data/)
documentation.

!!! warning
    Refer to the [discussion of selecting populations for studies](../explanation/selecting-populations-for-study.md).

This backend implements the following table schemas:

 * [core](schemas/core.md)
 * [raw.core](schemas/raw.core.md)
 * [tpp](schemas/tpp.md)
 * [raw.tpp](schemas/raw.tpp.md)
 * [smoketest](schemas/smoketest.md)

## EMIS
<small class="subtitle">
  <a href="https://github.com/opensafely-core/ehrql/blob/main/ehrql/backends/emis.py">
    <code>ehrql.backends.emis.EMISBackend</code>
  </a>
</small>

!!! warning
    Research access to the backend provided by EMIS is temporarily paused, pending
    completion of contracting between NHS England and Optum/EMIS. Examples of whole
    population work delivered using this service include research on [coding of long
    COVID](https://pubmed.ncbi.nlm.nih.gov/34340970/), and on changes in [primary
    care activity](https://pubmed.ncbi.nlm.nih.gov/37498081/) and [medication
    safety](https://pubmed.ncbi.nlm.nih.gov/37303488/) during the pandemic. We will
    update on the news pages when NHS England have completed their contract.

[Optum](https://www.optum.co.uk/) are the developers and operators of the [EMIS
Web](https://www.emishealth.com/emis-web) EHR platform. The ehrQL EMIS backend
provides access to primary care data from EMIS Web, plus data linked from other
sources.

This backend implements the following table schemas:

 * [core](schemas/core.md)
 * [raw.core](schemas/raw.core.md)
 * [raw.emis](schemas/raw.emis.md)
 * [emis](schemas/emis.md)
 * [smoketest](schemas/smoketest.md)
