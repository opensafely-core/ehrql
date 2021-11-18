from cohortextractor import table


def clinical_events():
    return table("clinical_events")


def registrations():
    return table("practice_registrations")
