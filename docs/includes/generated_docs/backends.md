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

!!! warning
    Refer to the [discussion of selecting populations for studies](../../explanation/selecting-populations-for-study.md).

This backend implements the following table schemas:

 * [core](../schemas/core/)
 * [raw.core](../schemas/raw.core/)
 * [tpp](../schemas/tpp/)
 * [raw.tpp](../schemas/raw.tpp/)
 * [smoketest](../schemas/smoketest/)

## EMIS
<small class="subtitle">
  <a href="https://github.com/opensafely-core/ehrql/blob/main/ehrql/backends/emis.py">
    <code>ehrql.backends.emis.EMISBackend</code>
  </a>
</small>

!!! warning
    Research access to the backend provided by EMIS is temporarily unavailable,
    pending funding arrangements between NHS England and EMIS.
    When funding has been secured,
    we will publish a timeline for gradually reopening access.

[EMIS Health](https://www.emishealth.com/) are the developers and operators of the
[EMIS Web](https://www.emishealth.com/products/emis-web) EHR platform. The ehrQL
EMIS backend provides access to primary care data from EMIS Web, plus data linked
from other sources.

This backend implements the following table schemas:

 * [core](../schemas/core/)
 * [raw.core](../schemas/raw.core/)
 * [raw.emis](../schemas/raw.emis/)
 * [emis](../schemas/emis/)
 * [smoketest](../schemas/smoketest/)
