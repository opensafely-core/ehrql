import json
from pathlib import Path

from databuilder.query_language import Dataset

from . import codelists, schema
from .variables_lib import (
    age_as_of,
    create_sequential_variables,
    date_deregistered_from_all_supported_practices,
    has_a_continuous_practice_registration_spanning,
    practice_registration_as_of,
)

dataset = Dataset()


#######################################################################################
# Import study dates defined in "./lib/design/study-dates.R" script and then exported
# to JSON
#######################################################################################
study_dates = json.loads(
    Path(__file__).parent.joinpath("study-dates.json").read_text(),
)

# Change these in design.R if necessary
firstpossiblevax_date = study_dates["firstpossiblevax_date"]
studystart_date = study_dates["studystart_date"]
studyend_date = study_dates["studyend_date"]
followupend_date = study_dates["followupend_date"]
firstpfizer_date = study_dates["firstpfizer_date"]
firstaz_date = study_dates["firstaz_date"]
firstmoderna_date = study_dates["firstmoderna_date"]


#######################################################################################
# Covid vaccine dates
#######################################################################################

# The old study def used 1900 as a minimum date so we replicate that here; but I think
# it only did this because it had to supply _some_ minimum date, which we don't need to
# here, so maybe we can drop this.
vax = schema.vaccinations.take(schema.vaccinations.date.is_after("1900-01-01"))

# Pfizer
create_sequential_variables(
    dataset,
    "covid_vax_pfizer_{n}_date",
    num_variables=4,
    events=vax.take(
        vax.product_name
        == "COVID-19 mRNA Vaccine Comirnaty 30micrograms/0.3ml dose conc for susp for inj MDV (Pfizer)"
    ),
    column="date",
)

# AZ
create_sequential_variables(
    dataset,
    "covid_vax_az_{n}_date",
    num_variables=4,
    events=vax.take(
        vax.product_name
        == "COVID-19 Vac AstraZeneca (ChAdOx1 S recomb) 5x10000000000 viral particles/0.5ml dose sol for inj MDV"
    ),
    column="date",
)

# Moderna
create_sequential_variables(
    dataset,
    "covid_vax_moderna_{n}_date",
    num_variables=4,
    events=vax.take(
        vax.product_name
        == "COVID-19 mRNA Vaccine Spikevax (nucleoside modified) 0.1mg/0.5mL dose disp for inj MDV (Moderna)"
    ),
    column="date",
)

# Any covid vaccine
create_sequential_variables(
    dataset,
    "covid_vax_disease_{n}_date",
    num_variables=4,
    events=vax.take(vax.target_disease == "SARS-2 CORONAVIRUS"),
    column="date",
)


#######################################################################################
# Aliases and common functions
#######################################################################################

boosted_date = dataset.covid_vax_disease_3_date
# We define baseline variables on the day _before_ the study date (start date = day of
# first possible booster vaccination)
baseline_date = boosted_date.subtract_days(1)

events = schema.coded_events
prior_events = events.take(events.date.is_on_or_before(baseline_date))


def has_prior_event(codelist):
    matching = prior_events.take(prior_events.snomedct_code.is_in(codelist))
    return matching.exists_for_patient()


#######################################################################################
# Admin and demographics
#######################################################################################

dataset.has_follow_up_previous_6weeks = has_a_continuous_practice_registration_spanning(
    start_date=boosted_date.subtract_days(6 * 7),
    end_date=boosted_date,
)

dataset.dereg_date = date_deregistered_from_all_supported_practices()

dataset.age = age_as_of(baseline_date)
# For JCVI group definitions
dataset.age_august2021 = age_as_of("2020-08-31")

dataset.sex = schema.patients.sex

#    # https://github.com/opensafely/risk-factors-research/issues/51
#    bmi=patients.categorised_as(
#      {
#        "Not obese": "DEFAULT",
#        "Obese I (30-34.9)": """ bmi_value >= 30 AND bmi_value < 35""",
#        "Obese II (35-39.9)": """ bmi_value >= 35 AND bmi_value < 40""",
#        "Obese III (40+)": """ bmi_value >= 40 AND bmi_value < 100""",
#        # set maximum to avoid any impossibly extreme values being classified as obese
#      },
#      bmi_value=patients.most_recent_bmi(
#        on_or_after="covid_vax_disease_3_date - 5 years",
#        minimum_age_at_measurement=16
#      ),
#      return_expectations={
#        "rate": "universal",
#        "category": {
#          "ratios": {
#            "Not obese": 0.7,
#            "Obese I (30-34.9)": 0.1,
#            "Obese II (35-39.9)": 0.1,
#            "Obese III (40+)": 0.1,
#          }
#        },
#      },
#    ),

# Ethnicity in 6 categories
dataset.ethnicity = (
    events.take(events.ctv3_code.is_in(codelists.ethnicity))
    .sort_by(events.date)
    .last_for_patient()
    .ctv3_code.to_category(codelists.ethnicity.Grouping_6)
)

#
#    # ethnicity variable that takes data from SUS
#    ethnicity_6_sus = patients.with_ethnicity_from_sus(
#      returning="group_6",
#      use_most_frequent_code=True,
#      return_expectations={
#        "category": {"ratios": {"1": 0.2, "2": 0.2, "3": 0.2, "4": 0.2, "5": 0.2}},
#        "incidence": 0.8,
#      },
#    ),


#######################################################################################
# Practice and patient ID variables
#######################################################################################

dataset.practice_id = practice_registration_as_of(baseline_date).practice_pseudo_id

#
#    # msoa
#    msoa=patients.address_as_of(
#      "covid_vax_disease_3_date - 1 day",
#      returning="msoa",
#      return_expectations={
#        "rate": "universal",
#        "category": {"ratios": {"E02000001": 0.0625, "E02000002": 0.0625, "E02000003": 0.0625, "E02000004": 0.0625,
#          "E02000005": 0.0625, "E02000007": 0.0625, "E02000008": 0.0625, "E02000009": 0.0625,
#          "E02000010": 0.0625, "E02000011": 0.0625, "E02000012": 0.0625, "E02000013": 0.0625,
#          "E02000014": 0.0625, "E02000015": 0.0625, "E02000016": 0.0625, "E02000017": 0.0625}},
#      },
#    ),
#
#    # stp is an NHS administration region based on geography
#    stp=patients.registered_practice_as_of(
#      "covid_vax_disease_3_date - 1 day",
#      returning="stp_code",
#      return_expectations={
#        "rate": "universal",
#        "category": {
#          "ratios": {
#            "STP1": 0.1,
#            "STP2": 0.1,
#            "STP3": 0.1,
#            "STP4": 0.1,
#            "STP5": 0.1,
#            "STP6": 0.1,
#            "STP7": 0.1,
#            "STP8": 0.1,
#            "STP9": 0.1,
#            "STP10": 0.1,
#          }
#        },
#      },
#    ),
#    # NHS administrative region
#    region=patients.registered_practice_as_of(
#      "covid_vax_disease_3_date - 1 day",
#      returning="nuts1_region_name",
#      return_expectations={
#        "rate": "universal",
#        "category": {
#          "ratios": {
#            "North East": 0.1,
#            "North West": 0.1,
#            "Yorkshire and The Humber": 0.2,
#            "East Midlands": 0.1,
#            "West Midlands": 0.1,
#            "East": 0.1,
#            "London": 0.1,
#            "South East": 0.1,
#            "South West": 0.1
#            #"" : 0.01
#          },
#        },
#      },
#    ),
#
#    ## IMD - quintile
#
#    imd=patients.address_as_of(
#      "covid_vax_disease_3_date - 1 day",
#      returning="index_of_multiple_deprivation",
#      round_to_nearest=100,
#      return_expectations={
#        "category": {"ratios": {c: 1/320 for c in range(100, 32100, 100)}}
#      }
#    ),
#
#    #rurality
#    rural_urban=patients.address_as_of(
#      "covid_vax_disease_3_date - 1 day",
#      returning="rural_urban_classification",
#      return_expectations={
#        "rate": "universal",
#        "category": {"ratios": {1: 0.125, 2: 0.125, 3: 0.125, 4: 0.125, 5: 0.125, 6: 0.125, 7: 0.125, 8: 0.125}},
#      },
#    ),
#
#
#
#    ################################################################################################
#    ## occupation / residency
#    ################################################################################################
#
#
#    # health or social care worker
#    hscworker = patients.with_healthcare_worker_flag_on_covid_vaccine_record(returning="binary_flag"),
#
#    care_home_type=patients.care_home_status_as_of(
#        "covid_vax_disease_3_date - 1 day",
#        categorised_as={
#            "Carehome": """
#              IsPotentialCareHome
#              AND LocationDoesNotRequireNursing='Y'
#              AND LocationRequiresNursing='N'
#            """,
#            "Nursinghome": """
#              IsPotentialCareHome
#              AND LocationDoesNotRequireNursing='N'
#              AND LocationRequiresNursing='Y'
#            """,
#            "Mixed": "IsPotentialCareHome",
#            "": "DEFAULT",  # use empty string
#        },
#        return_expectations={
#            "category": {"ratios": {"Carehome": 0.05, "Nursinghome": 0.05, "Mixed": 0.05, "": 0.85, }, },
#            "incidence": 1,
#        },
#    ),
#
#    # simple care home flag
#    care_home_tpp=patients.satisfying(
#        """care_home_type""",
#        return_expectations={"incidence": 0.01},
#    ),
#

# Patients in long-stay nursing and residential care
dataset.care_home_code = has_prior_event(codelists.carehome)


#    ################################################################################################
#    ## Pre-baseline events where event date is of interest
#    ################################################################################################
#
#
#    # Positive case identification prior to study start date
#    primary_care_covid_case_0_date=patients.with_these_clinical_events(
#      combine_codelists(
#        codelists.covid_primary_care_code,
#        codelists.covid_primary_care_positive_test,
#        codelists.covid_primary_care_sequelae,
#      ),
#      returning="date",
#      date_format="YYYY-MM-DD",
#      on_or_before="covid_vax_disease_3_date - 1 day",
#      find_last_match_in_period=True,
#    ),
#
#    # covid PCR test dates from SGSS
#    covid_test_0_date=patients.with_test_result_in_sgss(
#      pathogen="SARS-CoV-2",
#      test_result="any",
#      on_or_before="covid_vax_disease_3_date - 1 day",
#      returning="date",
#      date_format="YYYY-MM-DD",
#      find_last_match_in_period=True,
#      restrict_to_earliest_specimen_date=False,
#    ),
#
#
#    # positive covid test
#    postest_0_date=patients.with_test_result_in_sgss(
#        pathogen="SARS-CoV-2",
#        test_result="positive",
#        returning="date",
#        date_format="YYYY-MM-DD",
#        on_or_before="covid_vax_disease_3_date - 1 day",
#        find_last_match_in_period=True,
#        restrict_to_earliest_specimen_date=False,
#    ),
#
#    # emergency attendance for covid
#    covidemergency_0_date=patients.attended_emergency_care(
#      returning="date_arrived",
#      on_or_before="covid_vax_disease_3_date - 1 day",
#      with_these_diagnoses = codelists.covid_emergency,
#      date_format="YYYY-MM-DD",
#      find_last_match_in_period=True,
#    ),
#
#      # Positive covid admission prior to study start date
#    covidadmitted_0_date=patients.admitted_to_hospital(
#      returning="date_admitted",
#      with_admission_method=["21", "22", "23", "24", "25", "2A", "2B", "2C", "2D", "28"],
#      with_these_diagnoses=codelists.covid_icd10,
#      on_or_before="covid_vax_disease_3_date - 1 day",
#      date_format="YYYY-MM-DD",
#      find_last_match_in_period=True,
#    ),


#######################################################################################
# Clinical information as at (day before) 3rd / booster dose date
#######################################################################################

# From PRIMIS

# Asthma Admission codes
astadm = has_prior_event(codelists.astadm)
# Asthma Diagnosis code
ast = has_prior_event(codelists.ast)

#    asthma = patients.satisfying(
#      """
#        astadm OR
#        (ast AND astrxm1 AND astrxm2 AND astrxm3)
#        """,
#      # Asthma systemic steroid prescription code in month 1
#      astrxm1=patients.with_these_medications(
#        codelists.astrx,
#        returning="binary_flag",
#        between=["covid_vax_disease_3_date - 30 days", "covid_vax_disease_3_date - 1 day"],
#      ),
#      # Asthma systemic steroid prescription code in month 2
#      astrxm2=patients.with_these_medications(
#        codelists.astrx,
#        returning="binary_flag",
#        between=["covid_vax_disease_3_date - 60 days", "covid_vax_disease_3_date - 31 days"],
#      ),
#      # Asthma systemic steroid prescription code in month 3
#      astrxm3=patients.with_these_medications(
#        codelists.astrx,
#        returning="binary_flag",
#        between= ["covid_vax_disease_3_date - 90 days", "covid_vax_disease_3_date - 61 days"],
#      ),
#
#    ),

# Chronic Neurological Disease including Significant Learning Disorder
dataset.chronic_neuro_disease = has_prior_event(codelists.cns_cov)

# Chronic Respiratory Disease
resp_cov = has_prior_event(codelists.resp_cov)

#    chronic_resp_disease = patients.satisfying(
#      "asthma OR resp_cov",
#    ),

#
#    sev_obesity = patients.satisfying(
#      """
#        sev_obesity_date > bmi_date OR
#        bmi_value1 >= 40
#        """,
#
#      bmi_stage_date=patients.with_these_clinical_events(
#        codelists.bmi_stage,
#        returning="date",
#        find_last_match_in_period=True,
#        on_or_before="covid_vax_disease_3_date - 1 day",
#        date_format="YYYY-MM-DD",
#      ),
#
#      sev_obesity_date=patients.with_these_clinical_events(
#        codelists.sev_obesity,
#        returning="date",
#        find_last_match_in_period=True,
#        ignore_missing_values=True,
#        between= ["bmi_stage_date", "covid_vax_disease_3_date - 1 day"],
#        date_format="YYYY-MM-DD",
#      ),
#
#      bmi_date=patients.with_these_clinical_events(
#        codelists.bmi,
#        returning="date",
#        ignore_missing_values=True,
#        find_last_match_in_period=True,
#        on_or_before="covid_vax_disease_3_date - 1 day",
#        date_format="YYYY-MM-DD",
#      ),
#
#      bmi_value1=patients.with_these_clinical_events(
#        codelists.bmi,
#        returning="numeric_value",
#        ignore_missing_values=True,
#        find_last_match_in_period=True,
#        on_or_before="covid_vax_disease_3_date - 1 day",
#      ),
#
#    ),
#
#    diabetes = patients.satisfying(
#      "(dmres_date < diab_date) OR (diab_date AND (NOT dmres_date))",
#
#      diab_date=patients.with_these_clinical_events(
#        codelists.diab,
#        returning="date",
#        find_last_match_in_period=True,
#        on_or_before="covid_vax_disease_3_date - 1 day",
#        date_format="YYYY-MM-DD",
#      ),
#
#      dmres_date=patients.with_these_clinical_events(
#        codelists.dmres,
#        returning="date",
#        find_last_match_in_period=True,
#        on_or_before="covid_vax_disease_3_date - 1 day",
#        date_format="YYYY-MM-DD",
#      ),
#    ),
#
#    sev_mental=patients.satisfying(
#      "(smhres_date < sev_mental_date) OR (sev_mental_date AND (NOT smhres_date))",
#
#      # Severe Mental Illness codes
#      sev_mental_date=patients.with_these_clinical_events(
#        codelists.sev_mental,
#        returning="date",
#        find_last_match_in_period=True,
#        on_or_before="covid_vax_disease_3_date - 1 day",
#        date_format="YYYY-MM-DD",
#      ),
#      # Remission codes relating to Severe Mental Illness
#      smhres_date=patients.with_these_clinical_events(
#        codelists.smhres,
#        returning="date",
#        find_last_match_in_period=True,
#        on_or_before="covid_vax_disease_3_date - 1 day",
#        date_format="YYYY-MM-DD",
#      ),
#    ),

# Chronic heart disease codes
dataset.chronic_heart_disease = has_prior_event(codelists.chd_cov)

# Chronic kidney disease diagnostic codes
ckd = has_prior_event(codelists.ckd_cov)

#    chronic_kidney_disease=patients.satisfying(
#      """
#        ckd OR
#        (ckd15_date AND ckd35_date >= ckd15_date)
#        """,
#
#      # Chronic kidney disease codes - all stages
#      ckd15_date=patients.with_these_clinical_events(
#        codelists.ckd15,
#        returning="date",
#        find_last_match_in_period=True,
#        on_or_before="covid_vax_disease_3_date - 1 day",
#        date_format="YYYY-MM-DD",
#      ),
#
#      # Chronic kidney disease codes-stages 3 - 5
#      ckd35_date=patients.with_these_clinical_events(
#        codelists.ckd35,
#        returning="date",
#        find_last_match_in_period=True,
#        on_or_before="covid_vax_disease_3_date - 1 day",
#        date_format="YYYY-MM-DD",
#      ),
#    ),

# Chronic Liver disease codes
dataset.chronic_liver_disease = has_prior_event(codelists.cld)

# Immunosuppression diagnosis codes
immdx = has_prior_event(codelists.immdx_cov)

#    immunosuppressed=patients.satisfying(
#      "immrx OR immdx",
#
#      # Immunosuppression medication codes
#      immrx=patients.with_these_medications(
#        codelists.immrx,
#        returning="binary_flag",
#        between=["covid_vax_disease_3_date - 182 days", "covid_vax_disease_3_date - 1 day"]
#      ),
#    ),

# Asplenia or Dysfunction of the Spleen codes
dataset.asplenia = has_prior_event(codelists.spln_cov)

# Wider Learning Disability
dataset.learndis = has_prior_event(codelists.learndis)

#    # to represent household contact of shielding individual
#    # hhld_imdef_dat=patients.with_these_clinical_events(
#    #   codelists.hhld_imdef,
#    #   returning="date",
#    #   find_last_match_in_period=True,
#    #   on_or_before="covid_vax_disease_3_date - 1 day",
#    #   date_format="YYYY-MM-DD",
#    # ),
#    #
#    # #####################################
#    # # primis employment codelists
#    # #####################################
#    #
#    # # Carer codes
#    # carer_date=patients.with_these_clinical_events(
#    #   codelists.carer,
#    #   returning="date",
#    #   find_last_match_in_period=True,
#    #   on_or_before="covid_vax_disease_3_date - 1 day",
#    #   date_format="YYYY-MM-DD",
#    # ),
#    # # No longer a carer codes
#    # notcarer_date=patients.with_these_clinical_events(
#    #   codelists.notcarer,
#    #   returning="date",
#    #   find_last_match_in_period=True,
#    #   on_or_before="covid_vax_disease_3_date - 1 day",
#    #   date_format="YYYY-MM-DD",
#    # ),
#    # # Employed by Care Home codes
#    # carehome_date=patients.with_these_clinical_events(
#    #   codelists.carehomeemployee,
#    #   returning="date",
#    #   find_last_match_in_period=True,
#    #   on_or_before="covid_vax_disease_3_date - 1 day",
#    #   date_format="YYYY-MM-DD",
#    # ),
#    # # Employed by nursing home codes
#    # nursehome_date=patients.with_these_clinical_events(
#    #   codelists.nursehomeemployee,
#    #   returning="date",
#    #   find_last_match_in_period=True,
#    #   on_or_before="covid_vax_disease_3_date - 1 day",
#    #   date_format="YYYY-MM-DD",
#    # ),
#    # # Employed by domiciliary care provider codes
#    # domcare_date=patients.with_these_clinical_events(
#    #   codelists.domcareemployee,
#    #   returning="date",
#    #   find_last_match_in_period=True,
#    #   on_or_before="covid_vax_disease_3_date - 1 day",
#    #   date_format="YYYY-MM-DD",
#    # ),

# Ever coded as Clinically Extremely Vulnerable
dataset.cev_ever = has_prior_event(codelists.shield)

#    cev = patients.satisfying(
#      """severely_clinically_vulnerable AND NOT less_vulnerable""",
#      ##### The shielded patient list was retired in March/April 2021 when shielding ended
#      ##### so it might be worth using that as the end date instead of index_date, as we're not sure
#      ##### what has happened to these codes since then, e.g. have doctors still been adding new
#      ##### shielding flags or low-risk flags? Depends what you're looking for really. Could investigate separately.
#
#      ### SHIELDED GROUP - first flag all patients with "high risk" codes
#      severely_clinically_vulnerable = patients.with_these_clinical_events(
#        codelists.shield,
#        returning="binary_flag",
#        on_or_before = "covid_vax_disease_3_date - 1 day",
#        find_last_match_in_period = True,
#      ),
#
#      # find date at which the high risk code was added
#      date_severely_clinically_vulnerable = patients.date_of(
#        "severely_clinically_vulnerable",
#        date_format="YYYY-MM-DD",
#      ),
#
#      ### NOT SHIELDED GROUP (medium and low risk) - only flag if later than 'shielded'
#      less_vulnerable = patients.with_these_clinical_events(
#        codelists.nonshield,
#        between=["date_severely_clinically_vulnerable + 1 day", "covid_vax_disease_3_date - 1 day",],
#      ),
#
#    ),

endoflife_coding = has_prior_event(codelists.eol)

#    endoflife = patients.satisfying(
#      """
#      midazolam OR
#      endoflife_coding
#      """,
#
#      midazolam = patients.with_these_medications(
#        codelists.midazolam,
#        returning="binary_flag",
#        on_or_before = "covid_vax_disease_3_date - 1 day",
#      ),
#
#    ),
#
#    housebound = patients.satisfying(
#      """housebound_date
#      AND NOT no_longer_housebound
#      AND NOT moved_into_care_home
#      """,
#
#      housebound_date=patients.with_these_clinical_events(
#        codelists.housebound,
#        on_or_before="covid_vax_disease_3_date - 1 day",
#        find_last_match_in_period = True,
#        returning="date",
#        date_format="YYYY-MM-DD",
#      ),
#      no_longer_housebound=patients.with_these_clinical_events(
#        codelists.no_longer_housebound,
#        on_or_after="housebound_date",
#      ),
#      moved_into_care_home=patients.with_these_clinical_events(
#        codelists.carehome,
#        on_or_after="housebound_date",
#      ),
#    ),
#
#    prior_covid_test_frequency=patients.with_test_result_in_sgss(
#      pathogen="SARS-CoV-2",
#      test_result="any",
#      between=["covid_vax_disease_3_date - 182 days", "covid_vax_disease_3_date - 1 day"], # 182 days = 26 weeks
#      returning="number_of_matches_in_period",
#      date_format="YYYY-MM-DD",
#      restrict_to_earliest_specimen_date=False,
#    ),
#
#    # unplanned hospital admission at time of 3rd / booster dose
#    inhospital_unplanned = patients.satisfying(
#
#      "discharged_unplanned_0_date >= covid_vax_disease_3_date",
#
#      discharged_unplanned_0_date=patients.admitted_to_hospital(
#        returning="date_discharged",
#        on_or_before="covid_vax_disease_3_date - 1 day", #FIXME -- need to decide whether to include admissions discharged on the same day as booster dose or not
#        # see https://github.com/opensafely-core/cohort-extractor/pull/497 for codes
#        # see https://docs.opensafely.org/study-def-variables/#sus for more info
#        with_admission_method=["21", "22", "23", "24", "25", "2A", "2B", "2C", "2D", "28"],
#        with_patient_classification = ["1"], # ordinary admissions only
#        date_format="YYYY-MM-DD",
#        find_last_match_in_period=True,
#      ),
#    ),
#
#    # planned hospital admission at time of 3rd / booster dose
#    inhospital_planned = patients.satisfying(
#
#      "discharged_planned_0_date >= covid_vax_disease_3_date",
#
#      discharged_planned_0_date=patients.admitted_to_hospital(
#        returning="date_discharged",
#        on_or_before="covid_vax_disease_3_date - 1 day", #FIXME -- need to decide whether to include admissions discharged on the same day as booster dose or not
#        # see https://github.com/opensafely-core/cohort-extractor/pull/497 for codes
#        # see https://docs.opensafely.org/study-def-variables/#sus for more info
#        with_admission_method=["11", "12", "13", "81"],
#        with_patient_classification = ["1"], # ordinary admissions only
#        date_format="YYYY-MM-DD",
#        find_last_match_in_period=True
#      ),
#
#    ),
#
#
#    ############################################################
#    ## Post-baseline variables (outcomes)
#    ############################################################
#
#
#    # Positive case identification after study start date
#    primary_care_covid_case_date=patients.with_these_clinical_events(
#      combine_codelists(
#        codelists.covid_primary_care_code,
#        codelists.covid_primary_care_positive_test,
#        codelists.covid_primary_care_sequelae,
#      ),
#      returning="date",
#      date_format="YYYY-MM-DD",
#      on_or_after="covid_vax_disease_3_date",
#      find_first_match_in_period=True,
#    ),
#
#
#    # covid PCR test dates from SGSS
#    covid_test_date=patients.with_test_result_in_sgss(
#      pathogen="SARS-CoV-2",
#      test_result="any",
#      on_or_after="covid_vax_disease_3_date",
#      find_first_match_in_period=True,
#      restrict_to_earliest_specimen_date=False,
#      returning="date",
#      date_format="YYYY-MM-DD",
#    ),
#
#    # positive covid test
#    postest_date=patients.with_test_result_in_sgss(
#        pathogen="SARS-CoV-2",
#        test_result="positive",
#        returning="date",
#        date_format="YYYY-MM-DD",
#        on_or_after="covid_vax_disease_3_date",
#        find_first_match_in_period=True,
#        restrict_to_earliest_specimen_date=False,
#    ),
#
#    # emergency attendance for covid, as per discharge diagnosis
#    covidemergency_date=patients.attended_emergency_care(
#      returning="date_arrived",
#      date_format="YYYY-MM-DD",
#      on_or_after="covid_vax_disease_3_date",
#      with_these_diagnoses = codelists.covid_emergency,
#      find_first_match_in_period=True,
#    ),
#
#    # emergency attendance for covid, as per discharge diagnosis, resulting in discharge to hospital
#    covidemergencyhosp_date=patients.attended_emergency_care(
#      returning="date_arrived",
#      date_format="YYYY-MM-DD",
#      on_or_after="covid_vax_disease_3_date",
#      find_first_match_in_period=True,
#      with_these_diagnoses = codelists.covid_emergency,
#      discharged_to = codelists.discharged_to_hospital,
#    ),
#
#    # emergency attendance for respiratory illness
#    # FIXME -- need to define codelist
#    # respemergency_date=patients.attended_emergency_care(
#    #   returning="date_arrived",
#    #   date_format="YYYY-MM-DD",
#    #   on_or_after="covid_vax_disease_3_date",
#    #   with_these_diagnoses = codelists.resp_emergency,
#    #   find_first_match_in_period=True,
#    # ),
#
#    # emergency attendance for respiratory illness, resulting in discharge to hospital
#    # FIXME -- need to define codelist
#    # respemergencyhosp_date=patients.attended_emergency_care(
#    #   returning="date_arrived",
#    #   date_format="YYYY-MM-DD",
#    #   on_or_after="covid_vax_disease_3_date",
#    #   find_first_match_in_period=True,
#    #   with_these_diagnoses = codelists.resp_emergency,
#    #   discharged_to = codelists.discharged_to_hospital,
#    # ),
#
#    # any emergency attendance
#    emergency_date=patients.attended_emergency_care(
#      returning="date_arrived",
#      on_or_after="covid_vax_disease_3_date",
#      date_format="YYYY-MM-DD",
#      find_first_match_in_period=True,
#    ),
#
#    # emergency attendance resulting in discharge to hospital
#    emergencyhosp_date=patients.attended_emergency_care(
#      returning="date_arrived",
#      on_or_after="covid_vax_disease_3_date",
#      date_format="YYYY-MM-DD",
#      find_last_match_in_period=True,
#      discharged_to = codelists.discharged_to_hospital,
#    ),
#
#
#    # unplanned hospital admission
#    admitted_unplanned_date=patients.admitted_to_hospital(
#      returning="date_admitted",
#      on_or_after="covid_vax_disease_3_date",
#      # see https://github.com/opensafely-core/cohort-extractor/pull/497 for codes
#      # see https://docs.opensafely.org/study-def-variables/#sus for more info
#      with_admission_method=["21", "22", "23", "24", "25", "2A", "2B", "2C", "2D", "28"],
#      with_patient_classification = ["1"], # ordinary admissions only
#      date_format="YYYY-MM-DD",
#      find_first_match_in_period=True,
#    ),
#
#    # planned hospital admission
#    admitted_planned_date=patients.admitted_to_hospital(
#      returning="date_admitted",
#      on_or_after="covid_vax_disease_3_date",
#      # see https://github.com/opensafely-core/cohort-extractor/pull/497 for codes
#      # see https://docs.opensafely.org/study-def-variables/#sus for more info
#      with_admission_method=["11", "12", "13", "81"],
#      with_patient_classification = ["1"], # ordinary admissions only
#      date_format="YYYY-MM-DD",
#      find_first_match_in_period=True,
#    ),
#
#    # Positive covid admission prior to study start date
#    covidadmitted_date=patients.admitted_to_hospital(
#      returning="date_admitted",
#      with_admission_method=["21", "22", "23", "24", "25", "2A", "2B", "2C", "2D", "28"],
#      with_these_diagnoses=codelists.covid_icd10,
#      on_or_after="covid_vax_disease_3_date",
#      date_format="YYYY-MM-DD",
#      find_first_match_in_period=True,
#    ),
#
#    **critcare_dates(
#      name = "potentialcovidcritcare",
#      on_or_after = "covid_vax_disease_3_date",
#      n = 3,
#      with_admission_method = ["21", "22", "23", "24", "25", "2A", "2B", "2C", "2D", "28"],
#      with_these_diagnoses = codelists.covid_icd10
#    ),
#
#    # Covid-related death
#    coviddeath_date=patients.with_these_codes_on_death_certificate(
#      codelists.covid_icd10,
#      returning="date_of_death",
#      date_format="YYYY-MM-DD",
#    ),
#
#    # All-cause death
#    death_date=patients.died_from_any_cause(
#      returning="date_of_death",
#      date_format="YYYY-MM-DD",
#    ),


#######################################################################################
# Population
#######################################################################################

registered = practice_registration_as_of(baseline_date).exists_for_patient()

deaths = schema.ons_deaths
has_died = deaths.take(deaths.date.is_on_or_before(baseline_date)).exists_for_patient()

dataset.set_population(
    registered
    & (dataset.age_august2021 >= 18)
    & ~has_died
    & boosted_date.is_on_or_after(studystart_date)
    & boosted_date.is_on_or_before(studyend_date)
)
