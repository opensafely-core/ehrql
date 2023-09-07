# --8<-- [start:dataset_definition]
# --8<-- [start:dataset_import]
from ehrql import Dataset
# --8<-- [end:dataset_import]
# --8<-- [start:tables_import]
from ehrql.tables.beta.core import patients, medications
# --8<-- [end:tables_import]

# --8<-- [start:dataset_object]
dataset = Dataset()
# --8<-- [end:dataset_object]

# --8<-- [start:define_population]
dataset.define_population(patients.date_of_birth.is_on_or_before("1999-12-31"))
# --8<-- [end:define_population]

# --8<-- [start:asthma_medications]
asthma_codes = ["39113311000001107", "39113611000001102"]
latest_asthma_med = (
    medications.where(medications.dmd_code.is_in(asthma_codes))
    .sort_by(medications.date)
    .last_for_patient()
)
# --8<-- [end:asthma_medications]

# --8<-- [start:medication_date]
dataset.med_date = latest_asthma_med.date
# --8<-- [end:medication_date]
# --8<-- [start:medication_code]
dataset.med_code = latest_asthma_med.dmd_code
# --8<-- [end:medication_code]
# --8<-- [end:dataset_definition]
