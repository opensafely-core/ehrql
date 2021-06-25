from cohortextractor import table


class Cohort:
    everything = table("clinical_events").get("code")
