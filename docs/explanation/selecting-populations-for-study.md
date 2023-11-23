This page is aimed at researchers working with NHS England patient record data
as provided by the OpenSAFELY backends.

## Continuity of patient data

Within the NHS in England, it is usually assumed that
a patient's current primary care record is complete:
when a patient moves practice, their record moves with them.

However, a given NHS data source may only cover a subset of patients in England:
for example, only those included in a particular EHR vendor's database.
Therefore, where a patient has moved to a practice outside the database,
that patient would usually be censored from that date onwards.

Specifically, note that:

* From the time a patient leaves an NHS data source,
  we cannot be confident of any facts about the patient relating to that data source,
  unless they are completely transferred to another data source
  available in the same backend.
* A patient's total period of registration at one or more practices
  comprises the entire period over which we can expect their data
  to appear in other NHS data sources.
  Researchers may wish to select patients with a continuous registration
  over the time period of interest.

!!! note
    For TPP, there is a [method to select patients with a continuous registration](../reference/schemas/beta.tpp.md#practice_registrations.has_a_continuous_practice_registration_spanning)
