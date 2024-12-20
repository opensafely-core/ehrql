You can run ehrQL in two places:

* on your own computer,
  where you can try out ehrQL against _dummy tables_,
  and test that your analysis code runs correctly
* on an OpenSAFELY backend database,
  to use ehrQL with _real tables_

## Running ehrQL on your own computer against dummy tables

There are three ways to run ehrQL on your own computer against dummy tables:

1. using the OpenSAFELY VS Code extension, to explore the contents of ehrQL elements and datasets
1. as a standalone action, to test your dataset definition, via `opensafely exec`
1. as the first step in an OpenSAFELY pipeline, to test the whole pipeline, via `opensafely run`

### 1. Exploring ehrQL using the OpenSAFELY VS Code extension

The [OpenSAFELY VS Code extension](../explanation/vscode-extension.md) uses dummy tables to allow you to inspect the contents of ehrQL tables, columns, datasets and queries as you are writing
ehrQL in VS Code.


### 2. Running ehrQL as a standalone action via `opensafely exec`

To actually run your ehrQL queries against real tables,
you need to write a dataset definition and save it in a file.

But first, while you are developing an ehrQL query,
you can run your dataset definition against dummy tables
to produce an output file that you can inspect.

:computer: Copy and paste the following dataset definition
into a new file called `dataset_definition.py`:

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

dataset.med_date = latest_asthma_med.date
dataset.med_code = latest_asthma_med.dmd_code
```

:grey_question: Can you work out what the dataset definition will generate?

Make sure you save the file!

:computer: Use the command below to run your dataset definition with ehrQL.

```
opensafely exec ehrql:v1 generate-dataset dataset_definition.py --dummy-tables example-data --output output/dataset.csv
```

:notepad_spiral: ehrQL dataset definitions are written in Python.
But, unlike typical Python code,
we instead run the dataset definition via the OpenSAFELY CLI.
The OpenSAFELY CLI internally uses a correctly configured version of Python
to run the dataset definition.

#### What each part of this command does

* `opensafely exec ehrql:v1` uses the OpenSAFELY CLI to run ehrQL.
  The `v1` after the `:` refers to the version of ehrQL being used.
* `generate-dataset` instructs ehrQL to generate a dataset from the dataset definition.
* `dataset_definition.py` specifies the filename of the dataset definition to use.
    * The dataset definition file is in the directory that we are running `opensafely exec`
      so we do not need to specify the full path to the file in this case.
* `--dummy-tables example-data` specifies that the dummy CSV input data is in the `example-data` directory.
    * :notepad_spiral: If the `--dummy-tables` option is omitted,
      randomly generated data will be used instead.
* `--output output/dataset.csv` specifies the path to the output CSV file.
    * :notepad_spiral: If the `--output` option is omitted,
      the output will be not be saved to a file,
      but displayed on screen.

#### What you should see when you run the command

You should see output displayed similar to this:

```
2023-04-19 08:53:41 [info     ] Compiling dataset definition from dataset_definition.py [ehrql.main]
2023-04-19 08:53:41 [info     ] Generating dummy dataset       [ehrql.main]
2023-04-19 08:53:41 [info     ] Reading CSV data from example-data [ehrql.main]
2023-04-19 08:53:41 [info     ] Building dataset and writing results [ehrql.main]
```

:notepad_spiral: The date and time you see will differ from that here.

#### The output file

The output will be stored in a file called `dataset.csv` in the `output` directory.

The file will contain the following CSV data:

```
patient_id,med_date,med_code
0,2014-01-11,39113611000001102
1,2018-09-21,39113311000001107
4,2017-05-11,39113611000001102
5,2019-07-06,39113611000001102
6,,
7,,
8,,
9,,
```

:notepad_spiral: The bottom 4 rows in the generated dataset show that there are 4 patients in the defined population that do not have any record for the medications specified in the dataset definition.

:computer: Try running the ehrQL dataset definition again,
without the `--dummy-tables` and `--output` options:

```
opensafely exec ehrql:v1 generate-dataset dataset_definition.py
```

By not specifying the dummy tables to use,
random data is used as the data source to generate the dataset,
instead of using the sample dummy tables that you downloaded previously.

By not specifying the output file,
the output is displayed on screen.
This can be useful for quickly seeing output
while working on a dataset definition,
instead of saving to a file,
and then opening the file.


#### When things go wrong

If your dataset definition contains some invalid ehrQL,
an error message will be displayed on the screen.

This is one example:

```
$ opensafely exec ehrql:v1 generate-dataset dataset_definition.py --dummy-tables example-data --output output/dataset.csv
2023-04-21 17:53:42 [info     ] Compiling dataset definition from dataset_definition.py [ehrql.main]
Error loading file 'dataset_definition.py':
```
```pycon
Traceback (most recent call last):
  File "/workspace/dataset_definition.py", line 10, in <module>
    dataset.med_date = latest_asthma_med.dat
                       ^^^^^^^^^^^^^^^^^^^
AttributeError: 'medications' object has no attribute 'dat'
```

Refer to [the catalogue of errors](../how-to/errors.md) for help with interpreting error messages.

### 3. Running ehrQL in an OpenSAFELY pipeline via `opensafely run`

To run your ehrQL queries as part of an OpenSAFELY pipeline with `opensafely run`,
you need to have a file called `project.yaml`.

:notepad_spiral: There is considerably more technical detail on [the project pipeline in the OpenSAFELY documentation](https://docs.opensafely.org/actions-pipelines/).

:computer: Copy the following into a file called
`project.yaml`:

```yaml
version: '4.0'

actions:
  generate_dataset:
    run: ehrql:v1 generate-dataset dataset_definition.py --dummy-tables example-data --output output/dataset.csv.gz
    outputs:
      highly_sensitive:
        dataset: output/dataset.csv.gz

  summarise_dataset:
    run: python:latest summarise_dataset.py
    needs: [generate_dataset]
    outputs:
     moderately_sensitive:
        dataset: output/summary.txt
```

:notepad_spiral: Users already familiar with the [OpenSAFELY research template](https://github.com/opensafely/research-template) may notice that the research template already includes a basic `project.yaml` file that can be edited.
Here, for the purposes of this tutorial,
to skip setting up the template,
we create this file entirely by hand.

The `project.yaml` file defines two actions: `generate_dataset` and `summarise_dataset`.
Each of these actions specifies one or more `outputs`.

:notepad_spiral: The definitions of "highly sensitive" and "moderately sensitive" are explained in the [`project.yaml` documentation](https://docs.opensafely.org/actions-pipelines/#projectyaml-format).

The `generate_dataset` action's `run:` command should look familiar from the previous section.
However, note that the `--output` path is now to a compressed CSV file (`dataset.csv.gz`).

:notepad_spiral: We recommend the use of compressed CSV files when generating a dataset definition as part of an OpenSAFELY pipeline.

`summarise_dataset` uses a Python script called `summarise_dataset.py`.
Copy the following into a file called `summarise_dataset.py`.

```python
import pandas as pd

dataframe = pd.read_csv("output/dataset.csv.gz")
num_rows = len(dataframe)

with open("output/summary.txt", "w") as f:
    f.write(f"There are {num_rows} patients in the population\n")
```

:grey_question: Even if you don't know how to use [pandas](https://pandas.pydata.org/),
can you guess at what this code might do before you run the OpenSAFELY project?

:computer: Use the command below to run all of the actions
in `project.yaml`:

    opensafely run run_all

:notepad_spiral: If is this is the first time you have used `opensafely exec`,
the OpenSAFELY CLI may fetch some other Docker images (`python` and `busybox`) needed to run the action.

#### What you should see when you run the command

You should see in the logs output displayed similar to this:

```
$ opensafely run run_all

Running actions: generate_dataset, summarise_dataset

jobrunner.run loop started
generate_dataset: Preparing your code and workspace files
...
summarise_dataset: Extracting output file: output/summary.txt
summarise_dataset: Finished recording results
summarise_dataset: Completed successfully
summarise_dataset: Cleaning up container and volume

=> generate_dataset
   Completed successfully

   log file: metadata/generate_dataset.log
   outputs:
     output/dataset.csv.gz  - highly_sensitive

=> summarise_dataset
   Completed successfully

   log file: metadata/summarise_dataset.log
   outputs:
     output/summary.txt  - moderately_sensitive
```

:notepad_spiral: Some of the middle lines of this log have been omitted.

#### The output files

The `generate_dataset` action will generate a compressed CSV file called `dataset.csv.gz` in the `output` directory.
If you unzip this, you should see the same output as the previous example.

The `summarise_dataset` action will generate a small text file called `summary.txt` in the `output` directory.
This will tell you how many patients are in your population.

## Running ehrQL on an OpenSAFELY backend database

Once you are happy with your ehrQL queries and any analysis code,
you can submit your project to run against real data in an OpenSAFELY backend database.

To submit your project to run against real data, refer to the
[existing documentation on using the OpenSAFELY jobs site](https://docs.opensafely.org/jobs-site).

:notepad_spiral: You will require approval for an OpenSAFELY project,
before you can submit your project to the jobs site.

## Questions

* :grey_question: Why would you use the ehrQL `show()` function?
* :grey_question: Which `opensafely` command would you use to run just a dataset definition as a single action?
* :grey_question: Which `opensafely` command would you use to run an entire OpenSAFELY project consisting of multiple actions?
