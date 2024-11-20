We can now move on to implementing some of the QOF business rules.

In this tutorial, we'll look at rule DM\_006, which is about finding the percentage of patients on the register, with a diagnosis of clinical proteinuria or micro-albuminuria who are currently treated with angiotensin-converting enzymes (ACEs) or angiotensin II receptor blockers (ARBs).

The QOF rules define "currently treated" to mean having a medication within 180 days of the index date.

To do this, we'll use these codelists: [`PRT_COD`][1], [`MAL_COD`][2], [`ACE_COD`][3], and [`ARB_COD`][4].

## Medications

We have already seen how to determine whether a patient has a clinical event matching a code in a codelist.
Medications are recorded in a similar way to clinical events, and can be queried using the same kinds of ehrQL.

```ehrql
from ehrql import codelist_from_csv, days
from ehrql.tables.core import clinical_events, medications


index_date = "2024-03-31"

proteinuria_codes = codelist_from_csv("codelists/prt_cod.csv", column="code")
microalbuminuria_codes = codelist_from_csv("codelists/mal_cod.csv", column="code")
ace_codes = codelist_from_csv("codelists/ace_cod.csv", column="code")
arb_codes = codelist_from_csv("codelists/arb_cod.csv", column="code")

previous_events = clinical_events.where(clinical_events.is_before(index_date))
recent_meds = medications.where(medications.date.is_between(index_date - days(180), index_date))

has_proteinuria_diagnosis = (
    previous_events
    .where(clinical_events.snomedct_code.is_in(proteinuria_codes))
    .exists_for_patient()
)

has_microalbuminuria_diagnosis = (
    previous_events
    .where(clinical_events.snomedct_code.is_in(microalbuminuria_codes))
    .exists_for_patient()
)

has_arb_treatment = (
    recent_meds
    .where(medications.dmd_code.is_in(arb_codes))
    .exists_for_patient()
)

has_ace_treatment = (
    recent_meds
    .where(medications.dmd_code.is_in(ace_codes))
    .exists_for_patient()
)

debug(
    has_proteinuria_diagnosis,
    has_microalbuminuria_diagnosis,
    has_arb_treatment,
    has_ace_treatment,
)
```

Notice that we've added a couple of intermediate variables (`previous_events` and `recent_meds`) to reduce duplication in our code.

## Datasets

So far, we've been using `debug()` to show us what our queries return when running against dummy data.

But we can't use `debug()` to extract data for a real study!

Instead, we need to define a dataset.  As a reminder: a dataset is a new table containing one row per patient, and a dataset definition consists of a population definition and a set of column definitions.

We then use `dataset = create_dataset()` to create a new dataset object, `dataset.set_population(...)` to define the population, and `dataset.column_name = ...` to define the columns:


```ehrql
from ehrql import create_dataset, codelist_from_csv, days
from ehrql.tables.core import patients, practice_registrations, clinical_events, medications

index_date = "2024-03-31"

diabetes_codes = codelist_from_csv("codelists/dm_cod.csv", column="code")
resolved_codes = codelist_from_csv("codelists/dmres_cod.csv", column="code")
proteinuria_codes = codelist_from_csv("codelists/prt_cod.csv", column="code")
microalbuminuria_codes = codelist_from_csv("codelists/mal_cod.csv", column="code")
ace_codes = codelist_from_csv("codelists/ace_cod.csv", column="code")
arb_codes = codelist_from_csv("codelists/arb_cod.csv", column="code")

previous_events = clinical_events.where(clinical_events.is_before(index_date))
recent_meds = medications.where(medications.date.is_between(index_date - days(180), index_date))

aged_17_or_older = (index_date - patients.date_of_birth).years >= 17
was_alive = patients.date_of_death.is_null() | (patients.date_of_death < index_date)
was_registered = (
    practice_registrations.where(practice_registrations.start_date < index_date)
    .except_where(practice_registrations.end_date < index_date)
    .exists_for_patient()
)

last_diagnosis_date = (
    previous_events
    .where(clinical_events.snomedct_code.is_in(diabetes_codes))
    .sort_by("date")
    .last_for_patient()
    .date
)
last_resolved_date = (
    previous_events
    .where(clinical_events.snomedct_code.is_in(resolved_codes))
    .sort_by("date")
    .last_for_patient()
    .date
)

has_unresolved_diabetes = last_diagnosis_date.is_not_null() & (
    last_resolved_date.is_null() | (last_resolved_date < last_diagnosis_date)
)

on_register = aged_17_or_older & was_alive & was_registered & has_undiagnosed_diabetes

has_proteinuria_diagnosis = (
    previous_events
    .where(clinical_events.snomedct_code.is_in(proteinuria_codes))
    .exists_for_patient()
)

has_microalbuminuria_diagnosis = (
    previous_events
    .where(clinical_events.snomedct_code.is_in(microalbuminuria_codes))
    .exists_for_patient()
)

has_arb_treatment = (
    recent_meds
    .where(medications.dmd_code.is_in(arb_codes))
    .exists_for_patient()
)

has_ace_treatment = (
    recent_meds
    .where(medications.dmd_code.is_in(ace_codes))
    .exists_for_patient()
)

dataset = create_dataset()
dataset.set_population(on_register)

dataset.prt_or_mal = has_proteinuria_diagnosis | has_microalbuminuria_diagnosis
dataset.ace_or_arb = has_arb_treatment | has_ace_treatment

debug(dataset)
```

Note that it is essential that the dataset you create is given the name `dataset`.

> Question: what happens if you try to set the dataset's population to something that is not a boolean patient series?
>
> Question: what happens if you try to set a dataset column to something that is not a patient series?
>
> Question: what happens if you try to reuse a name for a dataset's column?



[1]: https://www.opencodelists.org/codelist/nhsd-primary-care-domain-refsets/prt_cod/
[2]: https://www.opencodelists.org/codelist/nhsd-primary-care-domain-refsets/mal_cod/
[3]: https://www.opencodelists.org/codelist/nhsd-primary-care-domain-refsets/ace_cod/
[4]: https://www.opencodelists.org/codelist/nhsd-primary-care-domain-refsets/arb_cod/
