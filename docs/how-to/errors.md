## ehrQL error messages

If an error is found in your dataset definition.
ehrQL will stop running and give you an error message.
ehrQL error messages are shown as a [Python error report, known as a "traceback"](https://realpython.com/python-traceback/).

:notepad_spiral: The error messages are from Python because ehrQL runs in Python.

These error messages can be confusing to read,
but they also give you lots of information to use to debug
and fix your dataset definition.

### Example error message

Let's look at an example of an error report:

```pytb
Traceback (most recent call last):
  File "/workspace/analysis/dataset_definition.py", line 7, in <module>
    dataset._age = age
    ^^^^^^^^^^^^^
AttributeError: Variable names must start with a letter, and contain only alphanumeric characters and underscores (you defined a variable '_age')
```

* The *traceback* tells you what code actually caused the error.
  The traceback shows both the filename
  and where the error occurred in the file.
* There is an error message at the end.
  The error message shows what kind of error occurred —
  here, this is an `AttributeError` —
  followed by details of what the problem is.

## How to use this page

### Structure of this page

For each error, there is:

1. a simple code example that causes the error
1. the error details
1. the simple code example modified to fix the error

### Finding an error on this page

If you are working with ehrQL,
and encounter an error,
this page may help you.

Because of the included code examples and errors,
this is a long page.

Here are some tips on narrowing down the search

#### Using the table of contents

Skimming the table of contents navigation bar on the right-hand side of this page,
to see if any of the general descriptions of errors apply
to what you are trying to do.

#### Using your browser's "Find text in page" feature

Using the "Find text in page" feature of your browser,
searching for parts of the error report.
Let's look at the example given above again:

```pytb
Traceback (most recent call last):
  File "/workspace/analysis/dataset_definition.py", line 7, in <module>
    dataset._age = age
    ^^^^^^^^^^^^^
AttributeError: Variable names must start with a letter, and contain only alphanumeric characters and underscores (you defined a variable '_age')
```

The first part of this traceback depends on the specific code that has been written here.
It shows:

* the name of the file —
  `dataset_definition.py` stored in the `analysis` directory
* the line number in the file causing the error —
  line 7
* the line of code causing the error

All of these will vary depending on the code being run.
These are useful to point you to where your error is.

However, they are possibly less useful to search for in the list provided here,
because this part of the error report will vary.
What *will* stay more constant is the final error message.
Searching in this page for parts of that line,
for example `AttributeError` or `Variable names must start with a letter`
may show you the relevant error.

:warning: This page covers many of the common ehrQL errors you may see,
but is not an exhaustive list.

:warning: Notice that even the error message may contain references to the precise code.
In this example: `you defined a variable '_age'`.

:question: Can you find the part of this page that does explain this error?

### Examples currently use the TPP backend

## Python syntax errors

These can occur because Python has its own syntactic rules
that ehrQL code must also adhere to.

### Code indentation error

Python has particular rules about indentation.
If a dataset definition contains indentation errors,
the error message will tell you about them.
For example, there is an indentation error in the following dataset definition.

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/code_indentation-standalone-failure/analysis/dataset_definition.py'
```

Run the dataset definition with:
```
opensafely exec ehrql:v0 generate-dataset analysis/dataset_definition.py
```

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/code_indentation-standalone-failure/output/traceback.txt'
```

The error message tells us that there is an indentation error, and also the line that
the error occurred on.

#### Fixed dataset definition :heavy_check_mark:

```python
--8<-- 'includes/code/how-to/errors/code_indentation-standalone-failure/analysis/dataset_definition.py'
```

### Forbidden feature names

Python has constraints on allowed variable names, which also apply to the names of dataset features.
For example, a name — `age!` — with a non-alphanumeric character is invalid:

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/feature_name-standalone-failure/analysis/dataset_definition.py'
```

Run the dataset definition with:
```
opensafely exec ehrql:v0 generate-dataset analysis/dataset_definition.py
```

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/feature_name-standalone-failure/output/traceback.txt'
```

#### Fixed dataset definition :heavy_check_mark:

```python
--8<-- 'includes/code/how-to/errors/feature_name-standalone-success/analysis/dataset_definition.py'
```

## Common ehrQL errors

These errors are specific to ehrQL,
rather than Python.

### Forgetting to set a population

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/set_population-standalone-failure/analysis/dataset_definition.py'
```

Run the dataset definition with:
```
opensafely exec ehrql:v0 generate-dataset analysis/dataset_definition.py
```

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/set_population-standalone-failure/output/traceback.txt'
```

#### Fixed dataset definition :heavy_check_mark:

```python
--8<-- 'includes/code/how-to/errors/set_population-standalone-success/analysis/dataset_definition.py'
```

### Invalid feature name: `population` is a reserved name

There are a few constraints on feature names in ehrQL.

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/population_reserved-standalone-failure/analysis/dataset_definition.py'
```

Run the dataset definition with:
```
opensafely exec ehrql:v0 generate-dataset analysis/dataset_definition.py
```

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/population_reserved-standalone-failure/output/traceback.txt'
```

#### Fixed dataset definition :heavy_check_mark:

Define population with the `define_population` syntax:

```python
--8<-- 'includes/code/how-to/errors/population_reserved-standalone-success/analysis/dataset_definition.py'
```

Or rename the feature, if it is required as a separate output:

```python
--8<-- 'includes/code/how-to/errors/population_reserved2-standalone-success/analysis/dataset_definition.py'
```

### Invalid feature name: `variables` is a reserved name

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/variables_reserved-standalone-failure/analysis/dataset_definition.py'
```

Run the dataset definition with:
```
opensafely exec ehrql:v0 generate-dataset analysis/dataset_definition.py
```

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/variables_reserved-standalone-failure/output/traceback.txt'
```

#### Fixed dataset definition :heavy_check_mark:

Rename the feature to something other than `variables`.

```python
--8<-- 'includes/code/how-to/errors/variables_reserved-standalone-success/analysis/dataset_definition.py'
```

### Invalid feature name: feature names must not start with underscores

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/underscore_name-standalone-failure/analysis/dataset_definition.py'
```

Run the dataset definition with:
```
opensafely exec ehrql:v0 generate-dataset analysis/dataset_definition.py
```

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/underscore_name-standalone-failure/output/traceback.txt'
```

#### Fixed data definition :heavy_check_mark:

```python
--8<-- 'includes/code/how-to/errors/underscore_name-standalone-success/analysis/dataset_definition.py'
```

### Re-defining a feature

In the following dataset definition, `dataset.age` is first defined as `age` and then defined again as `age1`.

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/feature_redefinition-standalone-failure/analysis/dataset_definition.py'
```

Run the dataset definition with:
```
opensafely exec ehrql:v0 generate-dataset analysis/dataset_definition.py
```

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/feature_redefinition-standalone-failure/output/traceback.txt'
```

#### Fixed dataset definition :heavy_check_mark:

```python
--8<-- 'includes/code/how-to/errors/feature_redefinition-standalone-success/analysis/dataset_definition.py'
```

### Undefined features

All features set on a dataset must be defined; in the following dataset, `age` has been
defined on its own, but has not been defined when set on the dataset:

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/undefined_feature-standalone-failure/analysis/dataset_definition.py'
```

Run the dataset definition with:
```
opensafely exec ehrql:v0 generate-dataset analysis/dataset_definition.py
```

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/undefined_feature-standalone-failure/output/traceback.txt'
```

#### Fixed dataset definition :heavy_check_mark:

```python
--8<-- 'includes/code/how-to/errors/undefined_feature-standalone-success/analysis/dataset_definition.py'
```

### Trying to set a feature that has more than one row per patient

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/multiple_rows-standalone-failure/analysis/dataset_definition.py'
```

The `practice_registrations` table contains multiple rows per patient.

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/multiple_rows-standalone-failure/output/traceback.txt'
```

#### Fixed dataset definition :heavy_check_mark:

To return the latest `registered_on` date, first sort the practice registrations table, find the
last registration for each patient, and *then* get the start date.

```python
--8<-- 'includes/code/how-to/errors/multiple_rows-standalone-success/analysis/dataset_definition.py'
```

### Trying to set a feature to a row rather than a value

In the following dataset definition, we have reduce the practice registrations to one row per patient, but
we have not selected a value as the feature:

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/feature_value-standalone-failure/analysis/dataset_definition.py'
```

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/feature_value-standalone-failure/output/traceback.txt'
```

Fix the dataset definition by setting the feature to a single value, in this case, `start_date`.

#### Fixed dataset definition :heavy_check_mark:

```python
--8<-- 'includes/code/how-to/errors/feature_value-standalone-success/analysis/dataset_definition.py'
```

### Type errors in ehrQL expressions

Many ehrQL comparisons require the elements being compared to be of the same type.

In the following dataset definition, `age` is an integer, but in the last line we
try to define the population by comparing age to the string `"10"`

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/element_type-standalone-failure/analysis/dataset_definition.py'
```

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/element_type-standalone-failure/output/traceback.txt'
```

#### Fixed dataset definition :heavy_check_mark:

```python
--8<-- 'includes/code/how-to/errors/element_type-standalone-success/analysis/dataset_definition.py'
```

### Invalid keywords "and", "or", "not"

In normal Python, logical operations can be performed using the keywords `and`, `or` and `not`. In ehrQL
these are prohibited and will raise an error.

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/invalid_keywords-standalone-failure/analysis/dataset_definition.py'
```

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/invalid_keywords-standalone-failure/output/traceback.txt'
```

#### Fixed dataset definition :heavy_check_mark:

As described in the error message, use the operator `&` instead:

```python
--8<-- 'includes/code/how-to/errors/invalid_keywords-standalone-success/analysis/dataset_definition.py'
```

### Chaining comparisons

Chained comparisons are not allowed in ehrQL.

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/chained_comparison-standalone-failure/analysis/dataset_definition.py'
```

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/chained_comparison-standalone-failure/output/traceback.txt'
```

#### Fixed dataset definition :heavy_check_mark:

```python
--8<-- 'includes/code/how-to/errors/chained_comparison-standalone-success/analysis/dataset_definition.py'
```

### Trying to perform arithmetic operations with an integer column and a float constant

In the following dataset, `age` is an integer. We cannot subtract a float from it.

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/arithmetic_type-standalone-failure/analysis/dataset_definition.py'
```

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/arithmetic_type-standalone-failure/output/traceback.txt'
```

#### Fixed dataset definition :heavy_check_mark:

```python
--8<-- 'includes/code/how-to/errors/arithmetic_type-standalone-success/analysis/dataset_definition.py'
```

### Calculate a date difference without specifying return units

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/date_difference-standalone-failure/analysis/dataset_definition.py'
```

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/date_difference-standalone-failure/output/traceback.txt'
```

To fix this error, specify the units of the date difference that you want in the feature:

#### Fixed dataset definition :heavy_check_mark:

```python
--8<-- 'includes/code/how-to/errors/date_difference-standalone-success/analysis/dataset_definition.py'
```

### Trying to subtract/add constants to dates

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/date_addition-standalone-failure/analysis/dataset_definition.py'
```

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/date_addition-standalone-failure/output/traceback.txt'
```

ehrQL cannot add an integer to a date - it needs to know what sort of time unit
we are adding (days, months, years).

#### Fixed dataset definition :heavy_check_mark:

```python
--8<-- 'includes/code/how-to/errors/date_addition-standalone-success/analysis/dataset_definition.py'
```

### Incorrectly referencing a table column

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/column_reference-standalone-failure/analysis/dataset_definition.py'
```

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/column_reference-standalone-failure/output/traceback.txt'
```

#### Fixed dataset definition :heavy_check_mark:

Columns can be specified as the table attribute:

```python
--8<-- 'includes/code/how-to/errors/column_reference-standalone-success/analysis/dataset_definition.py'
```

They can also be specified as a name string:

```python
--8<-- 'includes/code/how-to/errors/column_reference2-standalone-success/analysis/dataset_definition.py'
```

### Specifying a default for `case` which is a different type to the values

In the following dataset definition, two age groups are defined as integers (1 and 2). A default
value (for patients who don't fall into one of the categories) is defined as "unknown".  This is
an error - any default value given for a case statement must be of the same type (or None).

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/case_default-standalone-failure/analysis/dataset_definition.py'
```

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/case_default-standalone-failure/output/traceback.txt'
```

#### Fixed dataset definition :heavy_check_mark:

```python
--8<-- 'includes/code/how-to/errors/case_default-standalone-success/analysis/dataset_definition.py'
```

### Using `is_in` without a container

#### Failing dataset definition :x:

```python
--8<-- 'includes/code/how-to/errors/in_container-standalone-failure/analysis/dataset_definition.py:initial_error'
```

#### Error

```pytb
--8<-- 'includes/code/how-to/errors/in_container-standalone-failure/output/traceback.txt'
```

:notepad_spiral: This is also an error:

```python
--8<-- 'includes/code/how-to/errors/in_container-standalone-failure/analysis/dataset_definition.py:age_range'
```

#### Fixed dataset definition :heavy_check_mark:

Arguments passed to `is_in` must be wrapped in a python container - a set, list or tuple.
All of the following features defined with `is_in` are valid.

```python
--8<-- 'includes/code/how-to/errors/in_container-standalone-success/analysis/dataset_definition.py'
```
