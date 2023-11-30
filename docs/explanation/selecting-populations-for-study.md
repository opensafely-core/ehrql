This page is aimed at researchers working with NHS England patient record data
as provided by the OpenSAFELY backends.

## Continuity of patient data

Within the NHS in England, it is usually assumed that
a patient's current primary care record is complete:
when a patient moves practice, their record moves with them.

However, a given NHS data source may only cover a subset of patients in England:
for example, only those included in a particular EHR vendor's database.
Therefore, where a patient has moved to a practice outside the database,
we may not be confident of any facts about the patient relating to that database:

* Sometimes, patients will move practices within the same database.
  For example, the new practice could use the same EHR software.
  In that case, patient EHR data is completely transferred within the same database,
  and we can still be confident about that information.
* Researchers may wish to select patients
  with a continuous registration over the time period of interest.
  "Continuous registration" here means that
  a patient did not change practices during the time period of interest.

!!! note
    For TPP,
    there is a [method to select patients with a continuous registration](../reference/schemas/beta.tpp.md#practice_registrations.has_a_continuous_practice_registration_spanning).
