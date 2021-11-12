from cohortextractor import table


class Cohort:
    population = table("patients").exists()
