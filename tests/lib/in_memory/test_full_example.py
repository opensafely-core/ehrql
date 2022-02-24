# from databuilder.query_language import (
#     Dataset,
#     DateSeries,
#     IdSeries,
#     build_event_table,
#     build_patient_table,
# )

# patients = build_patient_table(
#     "patients",
#     {
#         "patient_id": IdSeries,
#         "date_of_birth": DateSeries,
#     },
# )

# imms = build_event_table(
#     "imms",
#     {},
# )

# # Create a dataset.
# dataset = Dataset()

# # Create two PatientSeries for age and sex and assign to the dataset.
# dataset.age = patients.age
# dataset.sex = patients.sex

# # Create a new EventFrame representing just the events with covid vaccination codes.
# covid_imms = imms.filter(imms.code.is_in(covid_vacc_codes))

# # Create an PatientFrame representing just, for each patient, the first record
# # in covid_imms.
# first = covid_imms.sort_by(imms.date).first_for_patient()

# # Create two PatientSeries for the first date / code and assign to the dataset.
# dataset.first_date = first.date
# dataset.first_code = first.code

# # Create an PatientFrame representing, for each patient, just the record that
# # occurs first 28 days after the first record of a covid vaccination.
# second = (
#     covid_imms.filter(imms.date > (dataset.first_date + 28))
#     .sort_by(imms.date)
#     .first_for_patient()
# )

# # Create two PatientSeries for the second date / code and assign to the dataset.
# dataset.second_date = second.date
# dataset.second_code = second.code

# # Create a PatientSeries based on the values in two other PatientSeries.
# dataset.codes_match = categorise(
#     {
#         "yes": dataset.first_code == dataset.second_code,
#         "no": True,
#     }
# )

# # Include only patients who have been at same practice for duration of study.
# dataset.set_population(
#     registrations.filter(registrations.start_date <= "2021-01-01")
#     .filter(registrations.end_date >= "2021-06-30")
#     .exists_for_patient()
# )
