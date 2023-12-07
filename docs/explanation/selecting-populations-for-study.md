This page is aimed at researchers working with NHS England patient record data
as provided by the OpenSAFELY backends.

## Continuity of patient data

Within the NHS in England, it is usually assumed that
a patient's current primary care record is complete:
when a patient moves practice to another practice in England,
their record moves with them.
The electronic health records of patients transferring between practices in England
should automatically get transferred via the GP2GP system.

Known caveats are that:

* not all data may be transferred; for example, appointment data
* not all data may be available at once; for example, information on repeat prescriptions

Refer to the [GP2GP site](https://digital.nhs.uk/services/gp2gp)
and the [GP2GP Key Activities documentation (PDF)](https://digital.nhs.uk/binaries/content/assets/website-assets/services/gp2gp/gp2gp_key_activities_2017_v0_4.pdf)
for further details of this transfer process.

!!! note
    Researchers using OpenSAFELY may wish to select patients
    with a continuous registration.
    "Continuous registration" here means that
    a patient did not change practice during a time period of interest.

    For TPP,
    there is a [method to select patients with a continuous registration](../reference/schemas/tpp.md#practice_registrations.has_a_continuous_practice_registration_spanning).
