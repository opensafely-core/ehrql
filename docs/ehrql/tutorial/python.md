# Installing ehrQL with Python

---8<-- 'includes/data-builder-danger-header.md'

!!! warning
    We recommend that you use ehrQL with the [OpenSAFELY CLI](../../../opensafely-cli.md)
    as instructed in the [ehrQL tutorial](index.md).

## Limitations

This option is a fall back if:

* you are a competent Python user,
* and you understand how to install Python packages yourself with `pip`

This installation option will allow you to run ehrQL dataset definitions only.
You will not be able to run a full OpenSAFELY project via a [`project.yaml` pipeline](../../../actions-pipelines.md).

If you are unable to run ehrQL via Docker,
you can try installing ehrQL directly using Python.

As Python configurations vary between operating systems,
and how users have Python configured,
we will not give detailed instructions.

!!! warning
    This option may not work on Windows currently:
    <https://github.com/opensafely-core/ehrql/issues/790>

!!! todo
    Can we fix that issue?

## Requirements

You will need to:

* have a suitable Python version installed (currently Python 3.11)
* configure a suitable virtual environment to run ehrQL
  for example with `conda` or `venv`
* install the ehrQL package into that virtual environment;

## Installation

Install the latest version of ehrQL into your new virtual environment with `pip`

```
pip install git+https://github.com/opensafely-core/ehrql@main#egg=opensafely-ehrql`
```

!!! todo
    It's probably better to advocate installing the same version we're using to build the definitions.
    This will be a tagged version in `ehrql/requirements.prod.in`.

!!! todo

    Are we going to ever publish ehrQL to PyPI?

### Checking the installation

Make sure that you can run ehrQL's "help" command:

```
ehrql --help
```

If that command succeeds,
you should see some help text
and ehrQL should be correctly installed.

## Using ehrQL's command-line interface

This section explains how to load dataset definitions into ehrQL.

Each dataset definition used in this tutorial has a filename of the form:

```
IDENTIFIER_DATASOURCENAME_dataset_definition.py
```

For example, for

```
1a_minimal_dataset_definition.py
```

the identifier is `1a` and the data source name is `minimal`.
The identifier associates the dataset definition with a specific tutorial page.

!!! todo

    Check how compatible this is cross-platform.

To run this dataset definition with ehrQL,

1. In a terminal, enter the `ehrql-tutorial-examples` directory that you extracted
   from the sample data.
2. Run this command:

   ```
   ehrql generate-dataset "1a_minimal_dataset_definition.py" --dummy-tables "example-data/minimal/" --output "outputs.csv"
   ```
3. You should see ehrQL run without error
   and find the `outputs.csv` file in the `ehrql-tutorial-examples` directory
   that you were working in.

!!! tip

    In general, the command to run a dataset defintion looks like:

    ```
    ehrql generate-dataset "IDENTIFIER_DATASOURCENAME_dataset_definition.py --dummy-tables "example-data/DATASOURCENAME/" --output "outputs.csv"
    ```

    You need to substitute `DATASOURCENAME` with the appropriate dataset name,
    and `IDENTIFIER_DATASOURCENAME_dataset_definition.py` to match the specific dataset definition
    that you want to run.

!!! tip

    The output in this example is called `outputs.csv`,
    but you can choose any valid filename.
