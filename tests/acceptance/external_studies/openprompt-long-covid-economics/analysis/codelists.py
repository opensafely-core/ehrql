from databuilder.ehrql import codelist_from_csv

# 1. Long COVID
# # import different long COVID codelists:
long_covid_assessment_codes = codelist_from_csv(
    "codelists/opensafely-assessment-instruments-and-outcome-measures-for-long-covid.csv",
    column = "code"
)     
    
long_covid_dx_codes =  codelist_from_csv(
    "codelists/opensafely-nice-managing-the-long-term-effects-of-covid-19.csv",
    column = "code"
) 

long_covid_referral_codes = codelist_from_csv(
    "codelists/opensafely-referral-and-signposting-for-long-covid.csv",
    column = "code"
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
    column = "CTV3ID",
)

copd = codelist_from_csv(
    "codelists/opensafely-chronic-respiratory-disease.csv",
    column = "CTV3ID",
)
