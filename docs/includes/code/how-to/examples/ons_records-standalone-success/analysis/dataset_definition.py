from ehrql import Dataset
from ehrql.tables.beta.tpp import ons_deaths

dataset = Dataset()
last_ons_death = ons_deaths.sort_by(ons_deaths.date).last_for_patient()
dataset.date_of_death = last_ons_death.date
dataset.place_of_death = last_ons_death.place
dataset.cause_of_death = last_ons_death.cause_of_death_01
