from databuilder import table


class Cohort:
    population = table("patients").exists()
    dob = table("patients").first_by("patient_id").get("date_of_birth")
