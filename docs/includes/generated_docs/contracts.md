## Universal/patients



| Column name | Description | Type | Constraints |
| ----------- | ----------- | ---- | ----------- |
| date_of_birth | Patient's date of birth, rounded to first of month | date | Always the first day of a month, never `null`. |
| sex | Patient's sex | str | Never `null`, possible values: `female`, `male`, `intersex`, `unknown`. |
| date_of_death | Patient's date of death | date | . |




## Wip/clinical_events

TODO.

| Column name | Description | Type | Constraints |
| ----------- | ----------- | ---- | ----------- |
| code |  | str | . |
| system |  | str | . |
| date |  | date | . |
| numeric_value |  | float | . |




## Wip/covid_test_results

TODO.

| Column name | Description | Type | Constraints |
| ----------- | ----------- | ---- | ----------- |
| date |  | date | . |
| positive_result |  | bool | . |




## Wip/hospital_admissions

TODO.

| Column name | Description | Type | Constraints |
| ----------- | ----------- | ---- | ----------- |
| admission_date |  | date | . |
| primary_diagnosis |  | str | . |
| admission_method |  | int | . |
| episode_is_finished |  | bool | . |
| spell_id |  | int | . |




## Wip/hospitalisations

TODO.

| Column name | Description | Type | Constraints |
| ----------- | ----------- | ---- | ----------- |
| date |  | date | . |
| code |  | str | . |
| system |  | str | . |




## Wip/hospitalisations_without_system

TODO.

| Column name | Description | Type | Constraints |
| ----------- | ----------- | ---- | ----------- |
| code |  | str | . |




## Wip/patient_address

TODO.

| Column name | Description | Type | Constraints |
| ----------- | ----------- | ---- | ----------- |
| patientaddress_id |  | int | . |
| date_start |  | date | . |
| date_end |  | date | . |
| index_of_multiple_deprivation_rounded |  | int | . |
| has_postcode |  | bool | . |




## Wip/patients

TODO.

| Column name | Description | Type | Constraints |
| ----------- | ----------- | ---- | ----------- |
| date_of_birth |  | date | . |




## Wip/practice_registrations

TODO.

| Column name | Description | Type | Constraints |
| ----------- | ----------- | ---- | ----------- |
| pseudo_id |  | int | . |
| nuts1_region_name |  | str | . |
| date_start |  | date | . |
| date_end |  | date | . |




## Wip/prescriptions

TODO.

| Column name | Description | Type | Constraints |
| ----------- | ----------- | ---- | ----------- |
| prescribed_dmd_code |  | str | . |
| processing_date |  | date | . |
