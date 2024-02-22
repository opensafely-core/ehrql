from ehrql import Dataset, years, days, months, minimum_of, maximum_of, case, when
from ehrql.tables.core import patients, clinical_events
from ehrql.tables.tpp import practice_registrations, ons_deaths

import codelists

def make_dataset_lowerGI(index_date, end_date):
    
    dataset = Dataset()

    reg_date = practice_registrations.where(practice_registrations.start_date.is_on_or_between(index_date, end_date)
                                                    ).sort_by(
                                                        practice_registrations.start_date
                                                    ).first_for_patient().start_date
    
    age_16_date = patients.date_of_birth + years(16)

    dataset.entry_date = maximum_of(reg_date, age_16_date, "2018-03-23")

    death_date = ons_deaths.date

    age_110_date = patients.date_of_birth + years(110)

    dereg_date = practice_registrations.sort_by(practice_registrations.end_date
                                              ).first_for_patient().end_date

    colorectal_ca_diag_date = clinical_events.where(clinical_events.snomedct_code.is_in(codelists.colorectal_diagnosis_codes_snomed)
                                                        ).sort_by(
                                                            clinical_events.date
                                                        ).first_for_patient().date
    
    dataset.exit_date = minimum_of(death_date, age_110_date, dereg_date, colorectal_ca_diag_date, "2023-10-22")

    dataset.death_date = death_date

    def first_event(codelist):
        return clinical_events.where(clinical_events.snomedct_code.is_in(codelist)
            ).where(
                clinical_events.date.is_on_or_between(index_date, end_date)
            ).where(
                clinical_events.date.is_on_or_between(dataset.entry_date, dataset.exit_date)
            ).sort_by(
                clinical_events.date
            ).first_for_patient()
    
    def prev_event(codelist, symp_date):
        return clinical_events.where(clinical_events.snomedct_code.is_in(codelist)
            ).where(
                clinical_events.date.is_on_or_between(symp_date - days (42), symp_date - days(1))
            ).exists_for_patient()

    dataset.ida_date = first_event(codelists.ida_codes).date
    dataset.cibh_date = first_event(codelists.cibh_codes).date
    dataset.prbleed_date = first_event(codelists.prbleeding_codes).date
    dataset.wl_date = first_event(codelists.wl_codes).date
    dataset.abdomass_date = first_event(codelists.abdomass_codes).date
    dataset.abdopain_date = first_event(codelists.abdopain_codes).date
    dataset.anaemia_date = first_event(codelists.anaemia_codes).date

    dataset.fit_test_any_date = first_event(codelists.fit_codes).date

    def has_event(codelist):
        return first_event(codelist).exists_for_patient()

    dataset.ida_symp = has_event(codelists.ida_codes) & ~prev_event(codelists.ida_codes, dataset.ida_date)
    dataset.cibh_symp = has_event(codelists.cibh_codes) & ~prev_event(codelists.cibh_codes, dataset.cibh_date)
    dataset.abdomass_symp = has_event(codelists.abdomass_codes) & ~prev_event(codelists.abdomass_codes, dataset.abdomass_date)
    dataset.prbleed_symp_50 = has_event(codelists.prbleeding_codes) & (patients.age_on(dataset.prbleed_date) >= 50) & ~prev_event(codelists.prbleeding_codes, dataset.prbleed_date)
    dataset.wl_symp_50 = has_event(codelists.wl_codes) & (patients.age_on(dataset.wl_date) >= 50) & ~prev_event(codelists.wl_codes, dataset.wl_date)
    dataset.abdopain_symp_50 = has_event(codelists.abdopain_codes) & (patients.age_on(dataset.abdopain_date) >= 50) & ~prev_event(codelists.abdopain_codes, dataset.abdopain_date)
    dataset.anaemia_symp_60 = has_event(codelists.anaemia_codes) & (patients.age_on(dataset.anaemia_date) >= 60) & ~prev_event(codelists.anaemia_codes, dataset.anaemia_date)
    dataset.wl_abdopain_symp_40 = has_event(codelists.wl_codes) & has_event(codelists.abdopain_codes) & ((patients.age_on(dataset.wl_date) >= 40) | (patients.age_on(dataset.abdopain_date) >= 40)) & ~prev_event(codelists.wl_codes, dataset.wl_date) & ~prev_event(codelists.abdopain_codes, dataset.abdopain_date)
    dataset.prbleed_abdopain_symp = has_event(codelists.prbleeding_codes) & has_event(codelists.abdopain_codes) & (patients.age_on(dataset.prbleed_date) < 50) & ~prev_event(codelists.prbleeding_codes, dataset.prbleed_date) & ~prev_event(codelists.abdopain_codes, dataset.abdopain_date)
    dataset.prbleed_wl_symp = has_event(codelists.prbleeding_codes) & has_event(codelists.wl_codes) & (patients.age_on(dataset.prbleed_date) < 50) & ~prev_event(codelists.prbleeding_codes, dataset.prbleed_date) & ~prev_event(codelists.wl_codes, dataset.wl_date)
    dataset.lowerGI_any_symp = (dataset.ida_symp | dataset.cibh_symp | dataset.abdomass_symp | dataset.prbleed_symp_50 | dataset.wl_symp_50 | dataset.abdopain_symp_50 | dataset.anaemia_symp_60 | dataset.wl_abdopain_symp_40 | dataset.prbleed_abdopain_symp | dataset.prbleed_wl_symp)

    dataset.fit_test_any = has_event(codelists.fit_codes) & ~prev_event(codelists.fit_codes, dataset.fit_test_any_date)

    def fit_6_weeks(symp_date):
        return clinical_events.where(clinical_events.snomedct_code.is_in(codelists.fit_codes)
        ).where(
            clinical_events.date.is_on_or_between(symp_date, symp_date + days(42))
        ).sort_by(
            clinical_events.date
        ).first_for_patient()
        
    dataset.fit_6_ida = dataset.ida_symp & fit_6_weeks(dataset.ida_date).exists_for_patient()
    dataset.fit_6_cibh = dataset.cibh_symp & fit_6_weeks(dataset.cibh_date).exists_for_patient()
    dataset.fit_6_abdomass = dataset.abdomass_symp & fit_6_weeks(dataset.abdomass_date).exists_for_patient()
    dataset.fit_6_prbleed = dataset.prbleed_symp_50 & fit_6_weeks(dataset.prbleed_date).exists_for_patient()
    dataset.fit_6_wl = dataset.wl_symp_50 & fit_6_weeks(dataset.wl_date).exists_for_patient()
    dataset.fit_6_abdopain = dataset.abdopain_symp_50 & fit_6_weeks(dataset.abdopain_date).exists_for_patient()
    dataset.fit_6_anaemia = dataset.anaemia_symp_60 & fit_6_weeks(dataset.anaemia_date).exists_for_patient()
    dataset.fit_6_wl_abdopain = dataset.wl_abdopain_symp_40 & (fit_6_weeks(dataset.wl_date).exists_for_patient() | fit_6_weeks(dataset.abdopain_date).exists_for_patient())
    dataset.fit_6_prbleed_abdopain = dataset.prbleed_abdopain_symp & fit_6_weeks(dataset.prbleed_date).exists_for_patient()
    dataset.fit_6_prbleed_wl = dataset.prbleed_wl_symp & fit_6_weeks(dataset.prbleed_date).exists_for_patient()
    dataset.fit_6_all_lowerGI = (dataset.fit_6_ida | dataset.fit_6_cibh | dataset.fit_6_abdomass | dataset.fit_6_prbleed | dataset.fit_6_wl | dataset.fit_6_abdopain | dataset.fit_6_anaemia | dataset.fit_6_wl_abdopain | dataset.fit_6_prbleed_abdopain | dataset.fit_6_prbleed_wl)

    def colorectal_ca_symp_6_months(symp_date):
        return clinical_events.where(clinical_events.snomedct_code.is_in(codelists.colorectal_diagnosis_codes_snomed)
        ).where(
            clinical_events.date.is_on_or_between(symp_date, symp_date + months(6))
        ).sort_by(
            clinical_events.date
        ).first_for_patient()

    dataset.ca_6_ida = dataset.ida_symp & colorectal_ca_symp_6_months(dataset.ida_date).exists_for_patient()
    dataset.ca_6_cibh = dataset.cibh_symp & colorectal_ca_symp_6_months(dataset.cibh_date).exists_for_patient()
    dataset.ca_6_abdomass = dataset.abdomass_symp & colorectal_ca_symp_6_months(dataset.abdomass_date).exists_for_patient()
    dataset.ca_6_prbleed = dataset.prbleed_symp_50 & colorectal_ca_symp_6_months(dataset.prbleed_date).exists_for_patient()
    dataset.ca_6_wl = dataset.wl_symp_50 & colorectal_ca_symp_6_months(dataset.wl_date).exists_for_patient()
    dataset.ca_6_abdopain = dataset.abdopain_symp_50 & colorectal_ca_symp_6_months(dataset.abdopain_date).exists_for_patient()
    dataset.ca_6_anaemia = dataset.anaemia_symp_60 & colorectal_ca_symp_6_months(dataset.anaemia_date).exists_for_patient()
    dataset.ca_6_wl_abdopain = dataset.wl_abdopain_symp_40 & (colorectal_ca_symp_6_months(dataset.wl_date).exists_for_patient() | colorectal_ca_symp_6_months(dataset.abdopain_date).exists_for_patient())
    dataset.ca_6_prbleed_abdopain = dataset.prbleed_abdopain_symp & colorectal_ca_symp_6_months(dataset.prbleed_date).exists_for_patient()
    dataset.ca_6_prbleed_wl = dataset.prbleed_wl_symp & colorectal_ca_symp_6_months(dataset.prbleed_date).exists_for_patient()
    dataset.ca_6_all_lowerGI = (dataset.ca_6_ida | dataset.ca_6_cibh | dataset.ca_6_abdomass | dataset.ca_6_prbleed | dataset.ca_6_wl | dataset.ca_6_abdopain | dataset.ca_6_anaemia | dataset.ca_6_wl_abdopain | dataset.ca_6_prbleed_abdopain | dataset.ca_6_prbleed_wl)

    return dataset

