from ehrql import Dataset
from ehrql.tables.beta.core import clinical_events
from ehrql.codes import codelist_from_csv

dataset = Dataset()

ethnicity_codelist = codelist_from_csv(
    "ethnicity_codelist_with_categories",
    column="snomedcode",
    category_column="Grouping_6",
)

dataset.latest_ethnicity_code = (
    clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity_codelist))
    .where(clinical_events.date.is_on_or_before("2023-01-01"))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .snomedct_code
)
latest_ethnicity_group = latest_ethnicity_code.to_category(
    ethnicity_codelist
)
