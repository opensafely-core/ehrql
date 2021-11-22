from cohortextractor2 import cohort_date_range, table

index_date_range = cohort_date_range(
    start="2021-01-01", end="2021-03-01", increment="month"
)


def cohort():
    class Cohort:
        population = table("practice_registrations").date_in_range().exists()
        date = table("clinical_events").first_by("patient_id").get("date")
        event = table("clinical_events").first_by("patient_id").get("code")

    return Cohort
