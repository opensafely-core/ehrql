import ehrql.tables.core
from ehrql.tables import table


@table
class patients(ehrql.tables.core.patients.__class__):
    """
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

    Dates of death appear in two places in the data made available via OpenSAFELY: the
    primary care record, and the death certificate data supplied by the ONS.

    ONS death data are considered the gold standard for identifying patient death in
    England because they are based on the MCCDs (Medical Certificate of Cause of Death)
    which the last attending doctor has a statutory duty to complete.

    While there is generally a lag between the death being recorded in ONS data and it
    appearing in the primary care record, the coverage of recorded death is almost
    complete and the date of death is usually reliable when it appears. There is also a
    lag in ONS death recording (see [`ons_deaths`](#ons_deaths) below for more detail).

    By contrast, _cause_ of death is often not accurate in the primary care record so we
    don't make it available to query here.

    [Example ehrQL usage of patients](../../how-to/examples.md#patients)
    """


@table
class clinical_events(ehrql.tables.core.clinical_events.__class__):
    """
    Each record corresponds to a single clinical or consultation event for a patient.

    Note that event codes do not change in this table. If an event code in the coding
    system becomes inactive, the event will still be coded to the inactive code.
    As such, codelists should include all relevant inactive codes.

    By default, only events with a consultation `date` on or before the date of the patient's
    last de-registration from an activated GP practice (a practice that has acknowledged the
    new non-COVID directions) are included.

    [Example ehrQL usage of clinical_events](../../how-to/examples.md#clinical-events)
    """


@table
class medications(ehrql.tables.core.medications.__class__):
    """
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

    By default, only medications with a consultation `date` on or before the date of the patient's
    last de-registration from an activated GP practice (a practice that has acknowledged the
    new non-COVID directions) are included.

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

    Examples of using ehrQL to calculation such periods can be found in the documentation
    on how to
    [use ehrQL to answer specific questions using the medications table](../../how-to/examples.md#medications)
    """
