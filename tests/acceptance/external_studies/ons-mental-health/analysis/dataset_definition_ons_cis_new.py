from databuilder.ehrql import Dataset
from databuilder.tables.beta import tpp as schema


#######################################################################################
# Define study dates 
#######################################################################################

start_date = '2020-01-24'
end_date = '2022-10-19'
n_visits = 26

dataset = Dataset()

#######################################################################################
# Define population
# Filter ONS CIS table to visit dates between the study start and end dates (inclusive) 
# and set the population to only patients who have at least one visit date in study date
# range
#######################################################################################

ons_cis = schema.ons_cis.where(schema.ons_cis.visit_date.is_on_or_between(start_date, end_date))
dataset.define_population(ons_cis.exists_for_patient())

#######################################################################################
# Define variables
# Create n_visits sequential variables for the ONS CIS columns of interest
#######################################################################################

def get_sequential_events(events, num_events, column_name):
    """
    This function takes a table of events (multiple per patient), a number of events to be
    extracted, and a column name to sort by.

    In this case, events is all of the ons_cis table visits that are within the study start
    and end date.
    """
    sort_column = getattr(events, column_name)
    previous_date = None
    for _ in range(num_events):
        # One each iteration through this loop, we first filter the events to only those
        # LATER than the previous_date found
        if previous_date is not None:
            later_events = events.where(sort_column > previous_date)
        else:
            later_events = events
        # Now we sort the events and get the first one
        next_event = later_events.sort_by(sort_column).first_for_patient()
        yield next_event
        # And update previous_date so the next iteration through the loop will filter to
        # events after this one we've just retrieved 
        previous_date = getattr(next_event, column_name)


# retrieve sequential visits by visit date
visits = get_sequential_events(ons_cis, n_visits, "visit_date")
# loop over the visits and for each one, set the variables on the dataset for the columns
# we're interested in
# Note that n is zero-indexed, so for n_visits=26, variables will be named
# e.g. `visit_date_0`, `visit_date_1`, ..., `visit_date_25`
for n, visit in enumerate(visits):
    setattr(dataset, f"visit_date_{n}", visit.visit_date)
    setattr(dataset, f"visit_num_{n}", visit.visit_num)
    setattr(dataset, f"last_linkage_dt_{n}", visit.last_linkage_dt)
    setattr(dataset, f"is_opted_out_of_nhs_data_share_{n}", visit.is_opted_out_of_nhs_data_share)
    setattr(dataset, f"imd_decile_e_{n}", visit.imd_decile_e)
    setattr(dataset, f"imd_quartile_e_{n}", visit.imd_quartile_e)
    setattr(dataset, f"rural_urban_{n}", visit.rural_urban)
