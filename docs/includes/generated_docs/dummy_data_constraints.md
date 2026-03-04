### `ehrql.tables.core`

#### `ons_deaths`

<div markdown="block" class="indent">

`date`

* Always `>= 2019-02-01`

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


### `ehrql.tables.tpp`

#### `addresses`

<div markdown="block" class="indent">

`end_date`

* Date must be on or after `start_date`

</div>

#### `apcs`

<div markdown="block" class="indent">

`admission_date`

* Always `>= 2016-04-01`

</div>

<div markdown="block" class="indent">

`discharge_date`

* Always `>= 2016-04-01`
* Date must be on or after `admission_date`

</div>

#### `apcs_cost`

<div markdown="block" class="indent">

`admission_date`

* Always `>= 2016-04-01`

</div>

<div markdown="block" class="indent">

`discharge_date`

* Always `>= 2016-04-01`
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

#### `decision_support_values`

<div markdown="block" class="indent">

`calculation_date`

* Never `NULL`
* Always `2020-12-08`

</div>

#### `ec`

<div markdown="block" class="indent">

`arrival_date`

* Always `>= 2017-10-01`

</div>

#### `ec_cost`

<div markdown="block" class="indent">

`arrival_date`

* Always `>= 2017-10-01`
* Date must be on or after `ec_injury_date`

</div>

<div markdown="block" class="indent">

`ec_decision_to_admit_date`

* Always `>= 2017-10-01`
* Date must be on or after `ec_injury_date`, `arrival_date`

</div>

<div markdown="block" class="indent">

`ec_injury_date`

* Always `>= 2017-10-01`

</div>

#### `emergency_care_attendances`

<div markdown="block" class="indent">

`arrival_date`

* Always `>= 2017-10-01`

</div>

#### `ons_deaths`

<div markdown="block" class="indent">

`date`

* Always `>= 2019-02-01`

</div>

#### `opa`

<div markdown="block" class="indent">

`appointment_date`

* Always `>= 2019-04-01`
* Date must be on or after `referral_request_received_date`

</div>

<div markdown="block" class="indent">

`referral_request_received_date`

* Always `>= 2019-04-01`

</div>

#### `opa_cost`

<div markdown="block" class="indent">

`appointment_date`

* Always `>= 2019-04-01`
* Date must be on or after `referral_request_received_date`

</div>

<div markdown="block" class="indent">

`referral_request_received_date`

* Always `>= 2019-04-01`

</div>

#### `opa_diag`

<div markdown="block" class="indent">

`appointment_date`

* Always `>= 2019-04-01`
* Date must be on or after `referral_request_received_date`

</div>

<div markdown="block" class="indent">

`referral_request_received_date`

* Always `>= 2019-04-01`

</div>

#### `opa_proc`

<div markdown="block" class="indent">

`appointment_date`

* Always `>= 2019-04-01`
* Date must be on or after `referral_request_received_date`

</div>

<div markdown="block" class="indent">

`referral_request_received_date`

* Always `>= 2019-04-01`

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

`specimen_taken_date`

* Always `>= 2020-01-01`

</div>

<div markdown="block" class="indent">

`lab_report_date`

* Always `>= 2020-01-01`
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

#### `ons_deaths`

<div markdown="block" class="indent">

`date`

* Always `>= 2019-02-01`

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
