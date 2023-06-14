# Supported output formats

The following output formats are supported:

## :heavy_check_mark: Recommended

* `.arrow` — Apache Arrow format
* `.csv.gz` — compressed CSV format

## :x: Not recommended

* `.csv` — uncompressed CSV format

:warning: The uncompressed CSV format is [not recommended](https://www.opensafely.org/changelog/2023-02-02/),
because this produces *much larger* files than the alternative formats.

# :construction: Unsupported output formats

* `.dta` and `.dta.gz` — Stata formats
  * Stata output support is still in development.
  * There is an [open ehrQL issue](https://github.com/opensafely-core/ehrql/issues/794) that discusses the work
    of supporting a suitable format for Stata.

# Selecting an output format

You select an output format
when you use the `--output` option to specify an output filename for ehrQL.
The filename *extension* — for example, `.arrow` — that you provide determines the output format file.

If you specify a filename extension that is not supported,
you will get an error telling you so.

## Examples with `opensafely exec`

### `.arrow`

```
opensafely exec databuilder:v0 generate-dataset "./dataset-definition.py" --dummy-tables "example-data/" --output "./outputs/data_extract.arrow"
```

### `.csv.gz`

```
opensafely exec databuilder:v0 generate-dataset "./dataset-definition.py" --dummy-tables "example-data/" --output "./outputs/data_extract.csv.gz"
```

## Example `project.yaml`

```yaml
version: "3.0"

expectations:
  population_size: 1000

actions:
  extract_data:
    run: databuilder:v0 generate-dataset "./dataset_definition.py" --output "outputs/data_extract.arrow"
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
