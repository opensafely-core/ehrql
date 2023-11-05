from databuilder.ehrql import codelist_from_csv

# 1. Long COVID
# # import different long COVID codelists:
long_covid_assessment_codes = codelist_from_csv(
    "codelists/opensafely-assessment-instruments-and-outcome-measures-for-long-covid.csv",
    column="code"
)     
    
long_covid_dx_codes = codelist_from_csv(
    "codelists/opensafely-nice-managing-the-long-term-effects-of-covid-19.csv",
    column="code"
) 

long_covid_referral_codes = codelist_from_csv(
    "codelists/opensafely-referral-and-signposting-for-long-covid.csv",
    column="code"
) 

# # Combine long covid codelists
lc_codelists_combined = (
    long_covid_dx_codes
    + long_covid_referral_codes
    + long_covid_assessment_codes
)

# 2. Ethnicities: 

ethnicity = codelist_from_csv(
    "codelists/opensafely-ethnicity.csv",
    column="Code",
    category_column="Grouping_6",
)

# 3. Mental issues:
psychosis_schizophrenia_bipolar_codes = codelist_from_csv(
    "codelists/opensafely-psychosis-schizophrenia-bipolar-affective-disease.csv",
    column="CTV3Code",
)
depression_codes = codelist_from_csv(
    "codelists/opensafely-depression.csv", column="CTV3Code"
)

mental_health_all = (
    psychosis_schizophrenia_bipolar_codes
    + depression_codes
)

# 3. COVID hospitalisation
hosp_covid = codelist_from_csv(
  "codelists/opensafely-covid-identification.csv",
  column="icd10_code"
)

# 4. Cancer codelist
lung_cancer = codelist_from_csv(
    "codelists/opensafely-lung-cancer.csv",
    column="CTV3ID",
)

other_cancer = codelist_from_csv(
    "codelists/opensafely-cancer-excluding-lung-and-haematological.csv",
    column="CTV3ID",    
)

haema_cancer = codelist_from_csv(
    "codelists/opensafely-haematological-cancer.csv",
    column="CTV3ID",        
)
cancer_all_combined__codelist = (
    lung_cancer 
    + other_cancer
    + haema_cancer
)

asthma = codelist_from_csv(
    "codelists/opensafely-asthma-diagnosis.csv",
    column="CTV3ID",
)

copd = codelist_from_csv(
    "codelists/opensafely-chronic-respiratory-disease.csv",
    column="CTV3ID",
)

organ_transplant_code = codelist_from_csv(
    "codelists/opensafely-solid-organ-transplantation.csv",
    column="CTV3ID",
)

chronic_cardiac_diseases_code = codelist_from_csv(
    "codelists/opensafely-chronic-cardiac-disease.csv",
    column="CTV3ID",    
)

chronic_liver_disease_code = codelist_from_csv(
    "codelists/opensafely-chronic-liver-disease.csv",
    column="CTV3ID",        
)

stroke_code = codelist_from_csv(
    "codelists/opensafely-stroke-updated.csv",
    column="CTV3ID",
)

dementia_code = codelist_from_csv(
    "codelists/opensafely-dementia.csv",
    column="CTV3ID",
)

other_neuro_code = codelist_from_csv(
    "codelists/opensafely-other-neurological-conditions.csv",
    column="CTV3ID",
)

ra_sle_psoriasis_code = codelist_from_csv(
    "codelists/opensafely-ra-sle-psoriasis.csv",
    column="CTV3ID",
)

asplenia_code = codelist_from_csv(
    "codelists/opensafely-asplenia.csv",
    column="CTV3ID",
)

hiv_code = codelist_from_csv(
    "codelists/opensafely-hiv.csv",
    column="CTV3ID",
)

aplastic_anemia_code = codelist_from_csv(
    "codelists/opensafely-aplastic-anaemia.csv",
    column="CTV3ID",
)

permanent_immune_suppress_code = codelist_from_csv(
    "codelists/opensafely-permanent-immunosuppression.csv",
    column="CTV3ID",
)

temporary_immune_suppress_code = codelist_from_csv(
    "codelists/opensafely-temporary-immunosuppression.csv",
    column="CTV3ID",
)

# adminstered vaccine codes
vac_adm_1 = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-covadm1.csv",
    column="code"
)
vac_adm_2 = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-covadm2.csv",
    column="code"
)
vac_adm_3 = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-covadm3_cod.csv",
    column="code"
)
vac_adm_4 = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-covadm4_cod.csv",
    column="code"
)
vac_adm_5 = codelist_from_csv(
    "codelists/primis-covid19-vacc-uptake-covadm5_cod.csv",
    column="code"
)

vac_adm_combine_code = (
    vac_adm_1
    + vac_adm_2
    + vac_adm_3
    + vac_adm_4
    + vac_adm_5
)


drug_bnf_ch1_gi_dmd = codelist_from_csv(
    "codelists/user-kate-mansfield-bnf-1-gastro-intestinal-system-dmd.csv",
    column="code"
)

drug_bnf_ch2_cv_dmd = codelist_from_csv(
    "codelists/user-kate-mansfield-bnf-2-cardiovascular-system-dmd.csv",
    column="code"
)

drug_bnf_ch3_chest_dmd = codelist_from_csv(
    "codelists/user-kate-mansfield-bnf-3-respiratory-system-dmd.csv",
    column="code"
)

drug_bnf_ch4_cns_dmd = codelist_from_csv(
    "codelists/user-kate-mansfield-bnf-4-central-nervous-system-dmd.csv",
    column="code"
)

drug_bnf_ch5_inf_dmd = codelist_from_csv(
    "codelists/user-kate-mansfield-bnf-5-infections-dmd.csv",
    column="code"
)

drug_bnf_ch6_meta_dmd = codelist_from_csv(
    "codelists/user-kate-mansfield-bnf-6-endocrine-system-dmd.csv",
    column="code"
)

drug_bnf_ch7_gyn = codelist_from_csv(
    "codelists/user-kate-mansfield-bnf-7-obstetrics-gynaecology-and-urinary-tract-disorders-dmd.csv",
    column="code"
)

drug_bnf_ch8_cancer_dmd = codelist_from_csv(
    "codelists/user-kate-mansfield-bnf-8-malignant-disease-and-immunosuppression-dmd.csv",
    column="code"
)

drug_bnf_ch9_diet_blood_dmd = codelist_from_csv(
    "codelists/user-kate-mansfield-bnf-9-nutrition-and-blood-dmd.csv",
    column="code"
)

drug_bnf_ch10_muscle_dmd = codelist_from_csv(
    "codelists/user-kate-mansfield-bnf-10-musculoskeletal-and-joint-diseases-dmd.csv",
    column="code"
)

drug_bnf_ch11_eye_dmd = codelist_from_csv(
    "codelists/user-kate-mansfield-bnf-11-eye-dmd.csv",
    column="code"
)

drug_bnf_ch12_ent_dmd = codelist_from_csv(
    "codelists/user-kate-mansfield-bnf-12-ear-nose-and-oropharynx-dmd.csv",
    column="code"
)

drug_bnf_ch13_skin_dmd = codelist_from_csv(
    "codelists/user-kate-mansfield-bnf-13-skin-dmd.csv",
    column="code"
)

total_drugs_dmd = (
    drug_bnf_ch1_gi_dmd
    + drug_bnf_ch2_cv_dmd
    + drug_bnf_ch3_chest_dmd
    + drug_bnf_ch4_cns_dmd
    + drug_bnf_ch5_inf_dmd
    + drug_bnf_ch6_meta_dmd
    + drug_bnf_ch7_gyn
    + drug_bnf_ch8_cancer_dmd
    + drug_bnf_ch9_diet_blood_dmd
    + drug_bnf_ch10_muscle_dmd
    + drug_bnf_ch11_eye_dmd
    + drug_bnf_ch12_ent_dmd
    + drug_bnf_ch13_skin_dmd
)