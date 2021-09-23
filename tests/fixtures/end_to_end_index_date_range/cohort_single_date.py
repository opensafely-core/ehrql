from cohortextractor import cohort_date_range, table


index_date_range = cohort_date_range("2021-01-31")


def cohort(index_date):
    class Cohort:
        population = table("practice_registrations").date_in_range(index_date).exists()
        date = table("clinical_events").first_by("patient_id").get("date")
        event = table("clinical_events").first_by("patient_id").get("code")

    return Cohort
