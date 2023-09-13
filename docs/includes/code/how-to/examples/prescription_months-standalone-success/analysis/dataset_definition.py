from ehrql import Dataset
from ehrql.tables.beta.tpp import medications

amoxicillin_codelist = codelist_from_csv(XXX)

winter_months = [10,11,12,1,2,3]

dataset = Dataset()
dataset.winter_amoxicillin_count = medications.where(
        medications.dmd_code.is_in(amoxicillin_codelist)
).where(
        medications.date.month.is_in(winter_months)
)
