from cohortextractor import table


# Define tables of interest, filtered to relevant values
abc = table("clinical_events").filter(code="abc")
# Get a single row per patient by selecting the latest event
abc_values = abc.latest()


class Cohort:
    # define columns in output
    abc_value = abc_values.get("test_value")
    date = abc_values.get("date")
