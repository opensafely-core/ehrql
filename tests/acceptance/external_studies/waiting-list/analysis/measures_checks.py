###########################################################
# The purpose of this script is to check the distributions
# of records over time. 
# It counts the monthly number of records by RTT start date,
# RTT end date and week ending date.
# It also counts number of patients by RTT end date.
###########################################################

from ehrql import INTERVAL, Measures, months
from ehrql.tables.tpp import (
    patients, 
    wl_clockstops)


##########

# # Monthly counts - overall, admitted, and not admitted
# count_overall = wl_clockstops.where(
#         wl_clockstops.referral_to_treatment_period_end_date.is_during(INTERVAL)
#     ).pseudo_referral_identifier.count_distinct_for_patient()

# count_admitted = wl_clockstops.where(
#         wl_clockstops.referral_to_treatment_period_end_date.is_during(INTERVAL)
#         & wl_clockstops.waiting_list_type.is_in(["IRTT","PTLI","RTTI"])
#     ).pseudo_referral_identifier.count_distinct_for_patient()

# count_not_admitted = wl_clockstops.where(
#         wl_clockstops.referral_to_treatment_period_end_date.is_during(INTERVAL)
#         & wl_clockstops.waiting_list_type.is_in(["ORTT","PTLO","RTTO"])
#     ).pseudo_referral_identifier.count_distinct_for_patient()


# Monthly counts - orthopaedic only
count_ortho = wl_clockstops.where(
        wl_clockstops.referral_to_treatment_period_end_date.is_during(INTERVAL)
        & wl_clockstops.activity_treatment_function_code.is_in(["110","111","108","115"])
    ).pseudo_referral_identifier.count_distinct_for_patient()

count_admitted_ortho = wl_clockstops.where(
        wl_clockstops.referral_to_treatment_period_end_date.is_during(INTERVAL)
        & wl_clockstops.waiting_list_type.is_in(["IRTT","PTLI","RTTI"])
        & wl_clockstops.activity_treatment_function_code.is_in(["110","111","108","115"])
    ).pseudo_referral_identifier.count_distinct_for_patient()

count_not_admitted_ortho = wl_clockstops.where(
        wl_clockstops.referral_to_treatment_period_end_date.is_during(INTERVAL)
        & wl_clockstops.waiting_list_type.is_in(["ORTT","PTLO","RTTO"])
        & wl_clockstops.activity_treatment_function_code.is_in(["110","111","108","115"])
    ).pseudo_referral_identifier.count_distinct_for_patient()


# By treatment specialty (only include most common groups reported in public statistics)

# trt_func = ["100","120","130","140","150","160","170","300","301","320","330","340","400","410","430","502",]

# count_var = {}

# for code in trt_func:

#     count_var["count_" + code] =  wl_clockstops.where(
#         wl_clockstops.referral_to_treatment_period_end_date.is_during(INTERVAL)
#         & wl_clockstops.activity_treatment_function_code.is_in([code])
#     ).pseudo_referral_identifier.count_distinct_for_patient()
    
#     count_var["count_admitted_" + code] =  wl_clockstops.where(
#         wl_clockstops.referral_to_treatment_period_end_date.is_during(INTERVAL)
#         & wl_clockstops.waiting_list_type.is_in(["IRTT","PTLI","RTTI"])
#         & wl_clockstops.activity_treatment_function_code.is_in([code])
#     ).pseudo_referral_identifier.count_distinct_for_patient()
    
#     count_var["count_not_admitted_" + code] =  wl_clockstops.where(
#         wl_clockstops.referral_to_treatment_period_end_date.is_during(INTERVAL)
#         & wl_clockstops.waiting_list_type.is_in(["ORTT","PTLO","RTTO"])
#         & wl_clockstops.activity_treatment_function_code.is_in([code])
#     ).pseudo_referral_identifier.count_distinct_for_patient()

    

######

measures = Measures()
measures.configure_dummy_data(population_size=5000)

denominator = (        
        (patients.age_on(INTERVAL.start_date) >= 0) 
        & (patients.age_on(INTERVAL.start_date) < 110)
        & (patients.sex.is_in(["male","female"]))
        & wl_clockstops.exists_for_patient()
    )

measures.define_defaults(
    denominator = denominator,
    intervals=months(13).starting_on("2021-05-01")
    )

# measures.define_measure(
#     name="closed_total",
#     numerator=count_overall
#     )

measures.define_measure(
    name="closed_ortho",
    numerator=count_ortho
    )

# measures.define_measure(
#     name="closed_admit_total",
#     numerator=count_admitted
#     )

measures.define_measure(
    name="closed_admit_ortho",
    numerator=count_admitted_ortho
    )

# measures.define_measure(
#     name="closed_not_admit_total",
#     numerator=count_not_admitted
#     )

measures.define_measure(
    name="closed_not_admit_ortho",
    numerator=count_not_admitted_ortho
    )

# for code in trt_func:
#     measures.define_measure(
#         name=f"count_{code}",
#         numerator=count_var["count_" + code]
#     )
#     measures.define_measure(
#         name=f"count_admit_{code}",
#         numerator=count_var["count_admitted_" + code]
#     )
#     measures.define_measure(
#         name=f"count_not_admit_{code}",
#         numerator=count_var["count_not_admitted_" + code]
#     )
