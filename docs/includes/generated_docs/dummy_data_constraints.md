### `ehrql.tables.core`

#### `practice_registrations`

<div markdown="block" class="indent">

`end_date`

* Always `None`

</div>

<div markdown="block" class="indent">

`practice_pseudo_id`

* Always `>= 0` and `<= 999`

</div>


### `ehrql.tables.tpp`

#### `addresses`

<div markdown="block" class="indent">

`end_date`

* Date must be on or after `start_date`

</div>

#### `apcs`

<div markdown="block" class="indent">

`discharge_date`

* Date must be on or after `admission_date`

</div>

#### `apcs_cost`

<div markdown="block" class="indent">

`discharge_date`

* Date must be on or after `admission_date`

</div>

#### `appointments`

<div markdown="block" class="indent">

`start_date`

* Date must be on or after `booked_date`

</div>

<div markdown="block" class="indent">

`seen_date`

* Date must be on or after `booked_date`, `start_date`

</div>

#### `ec_cost`

<div markdown="block" class="indent">

`arrival_date`

* Date must be on or after `ec_injury_date`

</div>

<div markdown="block" class="indent">

`ec_decision_to_admit_date`

* Date must be on or after `ec_injury_date`, `arrival_date`

</div>

#### `opa`

<div markdown="block" class="indent">

`appointment_date`

* Date must be on or after `referral_request_received_date`

</div>

#### `opa_cost`

<div markdown="block" class="indent">

`appointment_date`

* Date must be on or after `referral_request_received_date`

</div>

#### `opa_diag`

<div markdown="block" class="indent">

`appointment_date`

* Date must be on or after `referral_request_received_date`

</div>

#### `opa_proc`

<div markdown="block" class="indent">

`appointment_date`

* Date must be on or after `referral_request_received_date`

</div>

#### `practice_registrations`

<div markdown="block" class="indent">

`end_date`

* Always `None`

</div>

<div markdown="block" class="indent">

`practice_pseudo_id`

* Always `>= 0` and `<= 999`

</div>

#### `sgss_covid_all_tests`

<div markdown="block" class="indent">

`lab_report_date`

* Date must be on or after `specimen_taken_date`

</div>

#### `wl_clockstops`

<div markdown="block" class="indent">

`referral_to_treatment_period_end_date`

* Date must be on or after `referral_to_treatment_period_start_date`

</div>

#### `wl_openpathways`

<div markdown="block" class="indent">

`referral_to_treatment_period_end_date`

* Date must be on or after `referral_to_treatment_period_start_date`

</div>


### `ehrql.tables.emis`

#### `practice_registrations`

<div markdown="block" class="indent">

`end_date`

* Always `None`

</div>

<div markdown="block" class="indent">

`practice_pseudo_id`

* Always `>= 0` and `<= 999`

</div>
