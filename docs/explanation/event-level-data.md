# Event Level Data

---8<-- 'includes/eld-warning.md'

Datasets in ehrQL are restricted to one row per patient (or "patient-level") outputs.
The Event Level Data system allows you to add supplementary output files alongside the
main dataset which can contain more than one row per patient.


## Adding events to a dataset

Events are added using the
[`add_event_table()`](../reference/language.md#Dataset.add_event_table) method on
datasets. As an example, suppose you wanted to retrieve all relevant vaccination and
hospitalisation events for a set of patients:

```python
# ... imports etc ...

dataset = create_dataset()

dataset.define_population(
  (patients.age_on(study_start) >= 18)
  & (patients.age_on(study_start) <= 65)
)

# Get some vaccination events 
vaxx = vaccinations.where(
    vaccinations.date.is_on_or_between(study_start, study_end)
    & (vaccinations.target_disease == "SARS-2 CORONAVIRUS")
)

# Get some hospital admissions with a certain diagnosis
admissions = apcs.where(
    apcs.primary_diagnosis.is_in(respiratory_codes)
)

# Add these events to the dataset as ancillary files

dataset.add_event_table(
    "covid_vaccinations",
    date=vaxx.date,
    product=vaxx.product_name,
)

dataset.add_event_table(
    "respiratory_admissions",
    admitted=admissions.admission_date,
    discharged=admissions.discharge_date,
)
```

As the example shows, the `add_event_table()` method takes a name string and then some
number of column keywords. The table name can be whatever you want: it just affects what
the output file is called. Likewise with the column names.

You can add as many event tables to a dataset as you need.

Note that events are only returned for patients who **match the population definition**
of the dataset.


## Configuring outputs

Because event level output consists of multiple files rather than a single dataset file,
the way you specify the `--output` argument to `generate-dataset` is slightly different.
Instead of writing:
```
--output outputs/cohort.arrow
```

You write:
```
--output outputs/cohort/:arrow
```

Instead of a single file called `cohort` this will create a _directory_ called
`cohort` which will contain multiple files: a `dataset.arrow` file with the normal
one-row-per-patient output, and then one file for each of the event tables you've
defined.

Note that this works with any supported file format, not just Arrow.

You will also need to change the `outputs:` specification in your `project.yaml` file to
match, changing `output/cohort.arrow` to `output/cohort/*.arrow`.

A complete example might look like:
```yaml
generate_dataset:
  run: ehrql:v1 generate-dataset analysis/dataset_definition.py
    --output output/cohort/:arrow
  outputs:
    highly_sensitive:
      cohort: output/cohort/*.arrow
```
