from ehrql import INTERVAL, create_measures, months
from ehrql.tables.core import practice_registrations


# study_period = ("2020-04-01", "2021-03-31")

# dataset = create_dataset()
# dataset.configure_dummy_data(population_size=10)

# concordant_dates = (
#     repeat_medications.where(repeat_medications.date.is_during(study_period))
#     .where(repeat_medications.date == repeat_medications.start_date)
#     .date.count_distinct_for_patient()
# )

# dataset.concordant_date_count = concordant_dates

# dataset.define_population(patients.exists_for_patient())

# show(dataset)

measures = create_measures()

denominator = practice_registrations.for_patient_on(
    INTERVAL.start_date
).exists_for_patient()
registration = practice_registrations.for_patient_on("2022-01-01")

practice = registration.practice_pseudo_id

measures.configure_dummy_data(
    population_size=10,
    additional_population_constraint=registration.practice_pseudo_id.is_in([1, 2, 3]),
)

measures.define_measure(
    "list_size",
    numerator=denominator,
    denominator=denominator,
    intervals=months(2).starting_on("2022-01-01"),
    group_by={
        "practice": practice_registrations.for_patient_on(
            INTERVAL.start_date
        ).practice_pseudo_id,
    },
)
