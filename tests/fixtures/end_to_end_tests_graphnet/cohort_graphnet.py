from databuilder import table


class Cohort:
    population = table("patient_demographics").exists()
    dob = table("patient_demographics").first_by("patient_id").get("date_of_birth")
