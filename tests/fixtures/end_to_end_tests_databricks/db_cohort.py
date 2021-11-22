from cohortextractor2 import table


class Cohort:
    population = table("patients").exists()
