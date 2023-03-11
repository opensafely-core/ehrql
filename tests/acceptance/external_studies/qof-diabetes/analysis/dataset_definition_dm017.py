from datetime import date

from dm_dataset import (
    make_dm_dataset,
    get_registration_status,
    get_dm_reg_r1,
    get_dm_reg_r2,
)

# Define index date
index_date = date(2022, 3, 31)

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


# Apply business rules to define population
dataset.define_population(has_registration & has_dm_reg_select_r2)
