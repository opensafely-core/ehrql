from cohortextractor import table


class Cohort:
    date = table("clinical_events").get("date")
    event = table("clinical_events").get("code")
