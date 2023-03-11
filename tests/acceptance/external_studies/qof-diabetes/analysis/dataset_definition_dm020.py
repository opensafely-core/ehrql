from datetime import date

from dm_dataset import (
    make_dm_dataset,
    get_registration_status,
    get_dm_reg_r1,
    get_dm_reg_r2,
    get_dm020_r1,
    get_dm020_r2,
    get_dm020_r3,
    get_dm020_r4,
    get_dm020_r5,
    get_dm020_r6,
    get_dm020_r7,
    get_dm020_r8,
    get_dm020_r9,
    get_dm020_r10,
)

# Define index date and cutoff value for clinical rules
index_date = date(2022, 3, 31)
ifcchba_cutoff_val = 58.0

# Instantiate dataset and define clinical variables
dataset = make_dm_dataset(index_date=index_date)

# Define registration status
# NOTE: this is not identical to GMS registration status
has_registration = get_registration_status(index_date)

# Define diabetes register (DM_REG) rules:
dataset.dm_reg_r1 = get_dm_reg_r1(dataset)
dataset.dm_reg_r2 = get_dm_reg_r2(dataset)

# Define diabetes indicator DM020 rules:
dataset.dm020_r1 = get_dm020_r1(dataset)
dataset.dm020_r2 = get_dm020_r2(dataset, index_date, ifcchba_cutoff_val)
dataset.dm020_r3 = get_dm020_r3(dataset, index_date)
dataset.dm020_r4 = get_dm020_r4(dataset, index_date)
dataset.dm020_r5 = get_dm020_r5(dataset, index_date)
dataset.dm020_r6 = get_dm020_r6(dataset, index_date)
dataset.dm020_r7 = get_dm020_r7(dataset, index_date)
dataset.dm020_r8 = get_dm020_r8(dataset, index_date, ifcchba_cutoff_val)
dataset.dm020_r9 = get_dm020_r9(dataset, index_date)
dataset.dm020_r10 = get_dm020_r10(dataset, index_date)

# Define select action for DM_REG
has_dm_reg_select_r2 = dataset.dm_reg_r1 & ~dataset.dm_reg_r2

# Define first select action for DM020 (Rule 2)
has_dm020_select_r2 = ~dataset.dm020_r1 & dataset.dm020_r2

# Define second select action for DM020 (Rule 10)
has_dm020_select_r10 = (
    ~dataset.dm020_r1
    & ~dataset.dm020_r2
    & ~dataset.dm020_r3
    & ~dataset.dm020_r4
    & ~dataset.dm020_r5
    & ~dataset.dm020_r6
    & ~dataset.dm020_r7
    & ~dataset.dm020_r8
    & ~dataset.dm020_r9
    & ~dataset.dm020_r10
)

# Apply business rules to define population
dataset.define_population(
    # Registration status
    has_registration
    # Business rules for DM_REG
    & has_dm_reg_select_r2
    # Business rules for DM020
    & (has_dm020_select_r2 | has_dm020_select_r10)
)
