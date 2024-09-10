*ehrQL* (rhymes with *circle*), the **Electronic Health Records Query Language**,
is a query language and software tool designed for working with health data.
Researchers write **dataset definitions** with the query language
and execute them with the tool to generate **datasets with one row per patient**.

ehrQL allows researchers to access data sources from primary and secondary care,
as well as from organisations such as the Office for National Statistics (ONS).

ehrQL standardises data management tasks to promote efficiency,
reproducibility and transparency while maintaining patient privacy.
You can find out more about ehrQL's [philosophy and design goals](https://www.bennett.ox.ac.uk/blog/2023/09/why-ehrql/) on the Bennett Institute blog,
or see some [examples of ehrQL](how-to/examples.md) in action in the documentation.

If you have cumbersome data management tasks which are not currently supported by ehrQL
then please email us at <bennett@phc.ox.ac.uk> so we can consider how we might extend ehrQL to meet your needs.

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
[#opensafely-users](https://bennettoxford.slack.com/archives/C01D7H9LYKB)
Slack channel.
(If you're unsure how to join, then please ask your co-pilot.)

## A dataset definition

The following dataset definition selects the date and the code of each patient's most recent asthma medication,
for all patients born on or before 31 December 1999.

```ehrql
from ehrql import create_dataset
from ehrql.tables.core import patients, medications

dataset = create_dataset()

dataset.define_population(patients.date_of_birth.is_on_or_before("1999-12-31"))

asthma_codes = ["39113311000001107", "39113611000001102"]
latest_asthma_med = (
    medications.where(medications.dmd_code.is_in(asthma_codes))
    .sort_by(medications.date)
    .last_for_patient()
)

dataset.asthma_med_date = latest_asthma_med.date
dataset.asthma_med_code = latest_asthma_med.dmd_code
```

When the dataset definition is executed with the command line interface,
the command line interface generates a dataset with one row per patient.
For example, it may generate the following dummy dataset:

| patient_id | asthma_med_date |        asthma_med_code |
| ---------- | --------------- | ---------------------- |
|          1 |      2023-05-14 | 39113611000001102      |
|          2 |      2023-05-26 | 39113611000001102      |
|          3 |      2018-07-23 | 39113311000001107      |
|          5 |      2004-09-25 | 39113611000001102      |
|          6 |      2007-04-25 | 39113611000001102      |
|          7 |      1949-10-18 | 39113311000001107      |
|          9 |      1966-05-15 | 39113311000001107      |
|         10 |      1966-03-14 | 39113611000001102      |
