## Supported output formats

The following output formats are supported:

### :heavy_check_mark: Recommended

* `.arrow` — Apache Arrow format
* `.csv.gz` — compressed CSV format

### :x: Not recommended

* `.csv` — uncompressed CSV format

:warning: The uncompressed CSV format is [not recommended](https://www.opensafely.org/changelog/2023-02-02/),
because this produces *much larger* files than the alternative formats.

## Unsupported output formats

These formats are not supported by ehrQL. They were previously
supported by cohort-extractor, but that has been discontinued.

* `.dta` and `.dta.gz` — Stata formats

## `arrowload` for Stata users

Stata itself does not directly support `.arrow`.
However, OpenSAFELY's Stata Docker image contains the `arrowload` library
that can load `.arrow` files in Stata.

Use `arrowload` as:

```
. arrowload /path/to/arrow/file
```

See the full documentation via running command-line Stata via OpenSAFELY:

```
opensafely exec stata-mp stata
```

and then running

```
. help arrowload
```

## Selecting an output format

You select an output format
when you use the `--output` option to specify an output filename for ehrQL.
The filename *extension* — for example, `.arrow` — that you provide determines the output format file.

If you specify a filename extension that is not supported,
you will get an error telling you so.

:notepad_spiral: If you omit the `--output` option,
the output is not saved to a file.
Instead, the output is displayed at the command line.

### Examples with `opensafely exec`

#### `.arrow`

```
opensafely exec ehrql:v1 generate-dataset "./dataset-definition.py" --dummy-tables "example-data/" --output "./outputs/data_extract.arrow"
```

#### `.csv.gz`

```
opensafely exec ehrql:v1 generate-dataset "./dataset-definition.py" --dummy-tables "example-data/" --output "./outputs/data_extract.csv.gz"
```

### Example `project.yaml`

```yaml
version: "4.0"

actions:
  extract_data:
    run: ehrql:v1 generate-dataset "./dataset_definition.py" --output "outputs/data_extract.arrow"
    outputs:
      highly_sensitive:
        population: outputs/data_extract.arrow
```

:warning: The `population` filename *must* be identical to the output filename specified by `--output`.
Otherwise you will see the following error when you use `opensafely run`
to run the project actions:

```
$ opensafely run run_all
=> ProjectValidationError
   Invalid project:
   1 validation error for Pipeline
   __root__
     --output in run command and outputs must match (type=value_error)
```
