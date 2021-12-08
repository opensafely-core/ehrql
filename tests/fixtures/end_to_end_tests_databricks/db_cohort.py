from databuilder import table


class Cohort:
    population = table("patients").exists()
