from ehrql import Dataset, case, when
from ehrql.tables.beta.tpp import addresses

dataset = Dataset()
imd = addresses.for_patient_on("2023-01-01").imd_rounded
dataset.imd_quintile = case(
    when((imd >=0) & (imd < int(32844 * 1 / 5))).then("1 (most deprived)"),
    when(imd < int(32844 * 2 / 5)).then("2"),
    when(imd < int(32844 * 3 / 5)).then("3"),
    when(imd < int(32844 * 4 / 5)).then("4"),
    when(imd < int(32844 * 5 / 5)).then("5 (least deprived)"),
    default="unknown"
)
