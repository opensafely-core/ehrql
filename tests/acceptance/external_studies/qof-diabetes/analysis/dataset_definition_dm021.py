from argparse import ArgumentParser

from ehrql import INTERVAL, Measures, months
from ehrql.tables.tpp import patients

from dm_dataset import (
    make_dm_dataset,
    get_registration_status,
    get_dm_reg_r1,
    get_dm_reg_r2,
    get_dm021_r1,
    get_dm021_r2,
    get_dm021_r3,
    get_dm021_r4,
    get_dm021_r5,
    get_dm021_r6,
    get_dm021_r7,
    get_dm021_r8,
    get_dm021_r9,
    get_dm021_r10,
)

# Define index date and cutoff value for clinical rules
parser = ArgumentParser()
parser.add_argument("--ifcchba-cutoff-val", type=int)
args = parser.parse_args()
ifcchba_cutoff_val = args.ifcchba_cutoff_val

index_date = INTERVAL.start_date

# Instantiate dataset and define clinical variables
dataset = make_dm_dataset(index_date=index_date)

# Define registration status
# NOTE: this is not identical to GMS registration status
has_registration = get_registration_status(index_date)

# Define diabetes register (DM_REG) rules:
dataset.dm_reg_r1 = get_dm_reg_r1(dataset)
dataset.dm_reg_r2 = get_dm_reg_r2(dataset)

# Define diabetes indicator DM021 rules:
dataset.dm021_r1 = get_dm021_r1(dataset)
dataset.dm021_r2 = get_dm021_r2(dataset, index_date, ifcchba_cutoff_val)
dataset.dm021_r3 = get_dm021_r3(dataset, index_date)
dataset.dm021_r4 = get_dm021_r4(dataset, index_date)
dataset.dm021_r5 = get_dm021_r5(dataset, index_date)
dataset.dm021_r6 = get_dm021_r6(dataset, index_date)
dataset.dm021_r7 = get_dm021_r7(dataset, index_date)
dataset.dm021_r8 = get_dm021_r8(dataset, index_date, ifcchba_cutoff_val)
dataset.dm021_r9 = get_dm021_r9(dataset, index_date)
dataset.dm021_r10 = get_dm021_r10(dataset, index_date)

# Define select action for DM_REG
has_dm_reg_select_r2 = dataset.dm_reg_r1 & ~dataset.dm_reg_r2

# Define first select action for DM021 (Rule 2)
has_dm021_select_r2 = ~dataset.dm021_r1 & dataset.dm021_r2

# Define second select action for DM021 (Rule 10)
has_dm021_select_r10 = (
    ~dataset.dm021_r1
    & ~dataset.dm021_r2
    & ~dataset.dm021_r3
    & ~dataset.dm021_r4
    & ~dataset.dm021_r5
    & ~dataset.dm021_r6
    & ~dataset.dm021_r7
    & ~dataset.dm021_r8
    & ~dataset.dm021_r9
    & ~dataset.dm021_r10
)

# Define DM021 numerator and denominator
# DM021 gets applied to DM_REG (has_dm_reg_select_r2)
# The numerator is applied to the patients selected into the denominator
dm021_numerator = has_dm021_select_r2
dm021_denominator = has_dm_reg_select_r2 & (has_dm021_select_r2 | has_dm021_select_r10)

# Define measures
measures = Measures()

measures.define_measure(
    name="dm021",
    numerator=dm021_numerator,
    denominator=dm021_denominator,
    group_by={"sex": patients.sex},
    intervals=months(12).starting_on("2022-03-01"),
)
