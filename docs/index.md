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

## A dataset definition

The following dataset definition selects the date and the code of each patient's most recent asthma medication,
for all patients born on or before 31 December 1999.

```python
--8<-- 'includes/code/tutorial/writing-a-dataset-definition/asthma_medications-standalone-success/analysis/dataset_definition.py:dataset_definition'
```

When the dataset definition is executed with the command line interface,
the command line interface generates a dataset with one row per patient.
For example, it may generate the following dummy dataset:

{{ read_csv('includes/code/tutorial/writing-a-dataset-definition/asthma_medications-standalone-success/output/data_extract.csv', keep_default_na=False) }}
