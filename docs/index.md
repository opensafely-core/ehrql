*ehrQL* (rhymes with *circle*), the **Electronic Health Records Query Language**,
is a query language and command line interface designed for the specific application domain of EHR data.
Researchers write **dataset definitions** with the query language
and execute them with the command line interface to generate **datasets with one row per patient**.

ehrQL allows researchers to access data sources from primary and secondary care,
as well as from organisations such as the Office for National Statistics (ONS).

## ehrQL's documentation

ehrQL's documentation has four main sections:

1. The [tutorial](tutorial/index.md) provides practical steps for studying ehrQL.

1. The [how-to guides](how-to/index.md) provide practical steps for working with ehrQL in your project.

1. The [reference](reference/index.md) provides background knowledge for working with ehrQL in your project.

1. The [explanation](explanation/index.md) provides background knowledge for studying ehrQL.

### Conventions

* :computer: steps you should follow on the computer you are using for studying or working with ehrQL
* :notepad_spiral: explanatory information
* :warning: important information
* :grey_question: questions for you to think about

### Navigation

The four main sections are written to be read in order.
You can navigate between them by:

* pressing the ++n++ or ++period++ keys to go to the next page, and the ++p++ or ++comma++ keys to go to the previous page;
* using the *Previous* and *Next* links in the page footer;
* referring to the navigation pane to the left of the page and clicking a link.

## Asking for help

If you need help with ehrQL or ehrQL's documentation,
then please ask for help on the
[#ehrql-support](https://bennettoxford.slack.com/archives/C04DVD1UQC9)
Slack channel.
(If you're unsure how to join, then please ask your co-pilot.)

## Example

The following dataset definition is written in ehrQL:

```python
from ehrql import Dataset
from ehrql.tables.beta.core import patients, medications

dataset = Dataset()

dataset.define_population(patients.date_of_birth.is_on_or_before("1999-12-31"))

asthma_codes = ["39113311000001107", "39113611000001102"]
latest_asthma_med = (
    medications.where(medications.dmd_code.is_in(asthma_codes))
    .sort_by(medications.date)
    .last_for_patient()
)

dataset.med_date = latest_asthma_med.date
dataset.med_code = latest_asthma_med.dmd_code
```

Notice that the dataset will be restricted to the population of patients born on or before 31st December 1999.
It will contain two columns: `med_date` and `med_code`.
`med_date` is the date, and `med_code` is the code, of the latest (most recent) asthma medication.
Asthma medications will be restricted to those with the dm+d codes `39113311000001107` and `39113611000001102`.

When the dataset definition is executed with the command line interface,
the command line interface generates a dataset with one row per patient.
For example, it may generate the following dummy dataset:

| `patient_id` | `med_date` | `med_code`        |
|--------------|------------|-------------------|
| 1            | 2018-09-21 | 39113311000001107 |
| 2            | 2014-01-11 | 39113611000001102 |
| 4            | 2017-05-11 | 39113611000001102 |
| 5            |            |                   |

## ehrQL replaces cohort-extractor

Whilst cohort-extractor will be supported for projects created before June 2023,
new projects should use ehrQL.
For more information,
please read the [guidance for existing cohort-extractor users](explanation/guidance-for-existing-cohort-extractor-users.md).
