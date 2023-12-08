from ehrql import INTERVAL, Measures, months
from ehrql.tables.tpp import patients

from dm_dataset import (
    make_dm_dataset,
    get_registration_status,
    get_dm_reg_r1,
    get_dm_reg_r2,
)

index_date = INTERVAL.start_date

# Instantiate dataset and define clinical variables
dataset = make_dm_dataset(index_date=index_date)

# Define registration status
# NOTE: this is not identical to GMS registration status
has_registration = get_registration_status(index_date)

# Define diabetes register (DM_REG) rules:
dataset.dm_reg_r1 = get_dm_reg_r1(dataset)
dataset.dm_reg_r2 = get_dm_reg_r2(dataset)

# Define select rule 2
has_dm_reg_select_r2 = dataset.dm_reg_r1 & ~dataset.dm_reg_r2

# Define DM017 numerator and denominator
dm017_numerator = has_dm_reg_select_r2
dm017_denominator = has_registration

# Define measures
measures = Measures()

measures.define_measure(
    name="dm017",
    numerator=dm017_numerator,
    denominator=dm017_denominator,
    group_by={"sex": patients.sex},
    intervals=months(12).starting_on("2022-03-01"),
)
