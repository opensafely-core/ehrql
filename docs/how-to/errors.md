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
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
dataset.age = patients.age_on("2023-01-01")
 dataset.define_population(dataset.age > 16) # This line has incorrect indentation.
```

Run the dataset definition with:
```
opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition.py
```

#### Error

```pytb
Error loading file 'analysis/dataset_definition.py':

  File "/workspace/analysis/dataset_definition.py", line 6
    dataset.define_population(dataset.age > 16)
IndentationError: unexpected indent
```

The error message tells us that there is an indentation error, and also the line that
the error occurred on.

#### Fixed dataset definition :heavy_check_mark:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
dataset.age = patients.age_on("2023-01-01")
dataset.define_population(dataset.age > 16) # This line now has correct indentation.
```

### Forbidden feature names

Python has constraints on allowed variable names, which also apply to the names of dataset features.
For example, a name — `age!` — with a non-alphanumeric character is invalid:

#### Failing dataset definition :x:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
dataset.age! = patients.age_on("2023-01-01") # age! is an invalid feature name.
```

Run the dataset definition with:
```
opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition.py
```

#### Error

```pytb
Error loading file 'analysis/dataset_definition.py':

  File "/workspace/analysis/dataset_definition.py", line 5
    dataset.age! = patients.age_on("2023-01-01") # age! is an invalid feature name.
               ^
SyntaxError: invalid syntax
```

#### Fixed dataset definition :heavy_check_mark:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
dataset.age = patients.age_on("2023-01-01") # We have changed the invalid feature name, "age!", to a valid one, "age".
```

## Common ehrQL errors

These errors are specific to ehrQL,
rather than Python.

### Forgetting to set a population

#### Failing dataset definition :x:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
dataset.age = patients.age_on("2023-01-01")
```

Run the dataset definition with:
```
opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition.py
```

#### Error

```
A population has not been defined; define one with define_population()
```

#### Fixed dataset definition :heavy_check_mark:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
dataset.age = patients.age_on("2023-01-01")
dataset.define_population(dataset.age > 16) # Here we have now defined a population for the dataset.
```

### Invalid feature name: `population` is a reserved name

There are a few constraints on feature names in ehrQL.

#### Failing dataset definition :x:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
dataset.population = patients.age_on("2023-01-01") > 16
```

Run the dataset definition with:
```
opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition.py
```

#### Error

```pytb
Traceback (most recent call last):
  File "/workspace/analysis/dataset_definition.py", line 6, in <module>
    dataset.population = patients.age_on("2023-01-01") > 16
    ^^^^^^^^^^^^^^^^^^
AttributeError: Cannot set variable 'population'; use define_population() instead
```

#### Fixed dataset definition :heavy_check_mark:

Define population with the `define_population` syntax:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
dataset.define_population(patients.age_on("2023-01-01") > 16)
```

Or rename the feature, if it is required as a separate output:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
dataset.over_16 = patients.age_on("2023-01-01") > 16
```

### Invalid feature name: `variables` is a reserved name

#### Failing dataset definition :x:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
dataset.variables = patients.age_on("2023-01-01") > 16
...
```

Run the dataset definition with:
```
opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition.py
```

#### Error

```pytb
Traceback (most recent call last):
  File "/workspace/analysis/dataset_definition.py", line 5, in <module>
    dataset.variables = patients.age_on("2023-01-01") > 16
    ^^^^^^^^^^^^^^^^^
AttributeError: 'variables' is not an allowed variable name
```
#### Fixed dataset definition :heavy_check_mark:

Rename the feature to something other than `variables`.

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
dataset.age_greater_than_16 = patients.age_on("2023-01-01") > 16
...
```

### Invalid feature name: feature names must not start with underscores

#### Failing dataset definition :x:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
age = patients.age_on("2023-01-01")
dataset.define_population(age > 16)
dataset._age = age
```

Run the dataset definition with:
```
opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition.py
```

#### Error

```pytb
Traceback (most recent call last):
  File "/workspace/analysis/dataset_definition.py", line 7, in <module>
    dataset._age = age
    ^^^^^^^^^^^^^
AttributeError: Variable names must start with a letter, and contain only alphanumeric characters and underscores (you defined a variable '_age')

```

#### Fixed data definition :heavy_check_mark:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
age = patients.age_on("2023-01-01")
dataset.define_population(age > 16)
dataset.age = age # _age feature renamed to remove the leading underscores.
```

### Re-defining a feature

In the following dataset definition, `dataset.age` is first defined as `age` and then defined again as `age1`.

#### Failing dataset definition :x:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
age = patients.age_on("2000-01-01")
age1 = patients.age_on("2023-01-01")
dataset.define_population(age > 16)
dataset.age = age
dataset.age = age1
```

Run the dataset definition with:
```
opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition.py
```

#### Error

```pytb
Traceback (most recent call last):
  File "/workspace/analysis/dataset_definition.py", line 9, in <module>
    dataset.age = age1
    ^^^^^^^^^^^
AttributeError: 'age' is already set and cannot be reassigned
```

#### Fixed dataset definition :heavy_check_mark:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
age = patients.age_on("2000-01-01")
age1 = patients.age_on("2023-01-01")
dataset.define_population(age > 16)
dataset.age = age
dataset.age1 = age1 # The second age feature now has a unique name on the dataset
```

### Undefined features

All features set on a dataset must be defined; in the following dataset, `age` has been
defined on its own, but has not been defined when set on the dataset:

#### Failing dataset definition :x:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
age = patients.age_on("2000-01-01")
dataset.define_population(age > 16)
dataset.age
```

Run the dataset definition with:
```
opensafely exec ehrql:v1 generate-dataset analysis/dataset_definition.py
```

#### Error

```pytb
Traceback (most recent call last):
  File "/workspace/analysis/dataset_definition.py", line 8, in <module>
    dataset.age
AttributeError: Variable 'age' has not been defined
```

#### Fixed dataset definition :heavy_check_mark:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
age = patients.age_on("2000-01-01")
dataset.define_population(age > 16)
dataset.age = age # dataset.age is now defined
```

### Trying to set a feature that has more than one row per patient

#### Failing dataset definition :x:

```python
from ehrql import create_dataset
from ehrql.tables.tpp import practice_registrations

dataset = create_dataset()
dataset.registered_on = practice_registrations.start_date
```

The `practice_registrations` table contains multiple rows per patient.

#### Error

```pytb
Traceback (most recent call last):
  File "/workspace/analysis/dataset_definition.py", line 5, in <module>
    dataset.registered_on = practice_registrations.start_date
    ^^^^^^^^^^^^^^^^^^^^^
TypeError: Invalid variable 'registered_on'. Dataset variables must return one row per patient
```

#### Fixed dataset definition :heavy_check_mark:

To return the latest `registered_on` date, first sort the practice registrations table, find the
last registration for each patient, and *then* get the start date.

```python
from ehrql import create_dataset
from ehrql.tables.tpp import practice_registrations

dataset = create_dataset()
latest_registration_per_patient = practice_registrations.sort_by(practice_registrations.start_date).last_for_patient()
dataset.registered_on = latest_registration_per_patient.start_date
```

### Trying to set a feature to a row rather than a value

In the following dataset definition, we have reduce the practice registrations to one row per patient, but
we have not selected a value as the feature:

#### Failing dataset definition :x:

```python
from ehrql import create_dataset
from ehrql.tables.tpp import practice_registrations

dataset = create_dataset()
dataset.registered_on = practice_registrations.sort_by(practice_registrations.start_date).last_for_patient()
```

#### Error

```pytb
Traceback (most recent call last):
  File "/workspace/analysis/dataset_definition.py", line 5, in <module>
    dataset.registered_on = practice_registrations.sort_by(practice_registrations.start_date).last_for_patient()
    ^^^^^^^^^^^^^^^^^^^^^
TypeError: Invalid variable 'registered_on'. Dataset variables must be values not whole rows
```

Fix the dataset definition by setting the feature to a single value, in this case, `start_date`.

#### Fixed dataset definition :heavy_check_mark:

```python
from ehrql import create_dataset
from ehrql.tables.tpp import practice_registrations

dataset = create_dataset()
latest_registration_per_patient = practice_registrations.sort_by(practice_registrations.start_date).last_for_patient()
dataset.registered_on = latest_registration_per_patient.start_date
```

### Type errors in ehrQL expressions

Many ehrQL comparisons require the elements being compared to be of the same type.

In the following dataset definition, `age` is an integer, but in the last line we
try to define the population by comparing age to the string `"10"`

#### Failing dataset definition :x:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
age = patients.age_on("2023-01-01")
dataset.define_population(age >= "10")
```

#### Error

```pytb
Traceback (most recent call last):
  File "/workspace/analysis/dataset_definition.py", line 6, in <module>
    dataset.define_population(age >= "10")
                              ^^^^^^^^^^^
ehrql.query_model.nodes.TypeValidationError: GE.rhs requires 'ehrql.query_model.nodes.Series[int]' but got 'ehrql.query_model.nodes.Series[str]'
```

#### Fixed dataset definition :heavy_check_mark:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
age = patients.age_on("2023-01-01")
dataset.define_population(age >= 10)  # age is now being compared to the integer 10
```

### Invalid keywords "and", "or", "not"

In normal Python, logical operations can be performed using the keywords `and`, `or` and `not`. In ehrQL
these are prohibited and will raise an error.

#### Failing dataset definition :x:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
age = patients.age_on("2023-01-01")
dataset.define_population((age >= 16) and (age <= 80))
```

#### Error

```pytb
Traceback (most recent call last):
  File "/workspace/analysis/dataset_definition.py", line 6, in <module>
    dataset.define_population((age >= 16) and (age <= 80))
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: The keywords 'and', 'or', and 'not' cannot be used with ehrQL, please use the operators '&', '|' and '~' instead.
(You will also see this error if you try use a chained comparison, such as 'a < b < c'.)
```

#### Fixed dataset definition :heavy_check_mark:

As described in the error message, use the operator `&` instead:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
age = patients.age_on("2023-01-01")
dataset.define_population((age >= 16) & (age <= 80))
```

### Chaining comparisons

Chained comparisons are not allowed in ehrQL.

#### Failing dataset definition :x:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
age = patients.age_on("2023-01-01")
dataset.define_population(16 < age <= 80)
```

#### Error

```pytb
Traceback (most recent call last):
  File "/workspace/analysis/dataset_definition.py", line 6, in <module>
    dataset.define_population(16 < age <= 80)
                              ^^^^^^^^^^^^^^
TypeError: The keywords 'and', 'or', and 'not' cannot be used with ehrQL, please use the operators '&', '|' and '~' instead.
(You will also see this error if you try use a chained comparison, such as 'a < b < c'.)
```

#### Fixed dataset definition :heavy_check_mark:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
age = patients.age_on("2023-01-01")
dataset.define_population((age >= 16) & (age <= 80))
```

### Trying to perform arithmetic operations with an integer column and a float constant

In the following dataset, `age` is an integer. We cannot subtract a float from it.

#### Failing dataset definition :x:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
age = patients.age_on("2023-01-01")
dataset.age_minus_5 = age - 5.5
```

#### Error

```pytb
Traceback (most recent call last):
  File "/workspace/analysis/dataset_definition.py", line 6, in <module>
    dataset.age_minus_5 = age - 5.5
                          ~~~~^~~~~
ehrql.query_model.nodes.TypeValidationError: Subtract.rhs requires 'ehrql.query_model.nodes.Series[int]' but got 'ehrql.query_model.nodes.Series[float]'
```

#### Fixed dataset definition :heavy_check_mark:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
age = patients.age_on("2023-01-01")
dataset.age_minus_5 = age - 5
```

### Calculate a date difference without specifying return units

#### Failing dataset definition :x:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
dataset.age_in_may = "2023-05-01" - patients.date_of_birth
```

#### Error

```pytb
Traceback (most recent call last):
  File "/workspace/analysis/dataset_definition.py", line 5, in <module>
    dataset.age_in_may = "2023-05-01" - patients.date_of_birth
    ^^^^^^^^^^^^^^^^^^
TypeError: Invalid variable 'age_in_may'. Dataset variables must be values not whole rows
```

To fix this error, specify the units of the date difference that you want in the feature:

#### Fixed dataset definition :heavy_check_mark:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
dataset.age_in_may = ("2023-05-01" - patients.date_of_birth).years
```

### Trying to subtract/add constants to dates

#### Failing dataset definition :x:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()
dataset.date_at_age_16 = patients.date_of_birth + 16
```

#### Error

```pytb
Traceback (most recent call last):
  File "/workspace/analysis/dataset_definition.py", line 5, in <module>
    dataset.date_at_age_16 = patients.date_of_birth + 16
                             ~~~~~~~~~~~~~~~~~~~~~~~^~~~
TypeError: unsupported operand type(s) for +: 'DatePatientSeries' and 'int'
```

ehrQL cannot add an integer to a date - it needs to know what sort of time unit
we are adding (days, months, years).

#### Fixed dataset definition :heavy_check_mark:

```python
from ehrql import create_dataset, years
from ehrql.tables.core import patients

dataset = create_dataset()
dataset.date_at_age_16 = patients.date_of_birth + years(16)
```

### Incorrectly referencing a table column

#### Failing dataset definition :x:

```python
from ehrql import create_dataset
from ehrql.tables.core import clinical_events

dataset = create_dataset()
first_event = clinical_events.sort_by(date).first_for_patient()
dataset.event_date = first_event.date
```

#### Error

```pytb
Traceback (most recent call last):
  File "/workspace/analysis/dataset_definition.py", line 5, in <module>
    first_event = clinical_events.sort_by(date).first_for_patient()
                                          ^^^^
NameError: name 'date' is not defined
```

#### Fixed dataset definition :heavy_check_mark:

Columns can be specified as the table attribute:

```python
from ehrql import create_dataset
from ehrql.tables.core import clinical_events

dataset = create_dataset()
first_event = clinical_events.sort_by(clinical_events.date).first_for_patient()
dataset.event_date = first_event.date
```

They can also be specified as a name string:

```python
from ehrql import create_dataset
from ehrql.tables.core import clinical_events

dataset = create_dataset()
first_event = clinical_events.sort_by("date").first_for_patient()
dataset.event_date = first_event.date
```

### Specifying a default for `case` which is a different type to the values

In the following dataset definition, two age groups are defined as integers (1 and 2). A default
value (for patients who don't fall into one of the categories) is defined as "unknown".  This is
an error - any default value given for a case statement must be of the same type (or None).

#### Failing dataset definition :x:

```python
from ehrql import create_dataset, case, when
from ehrql.tables.core import patients

dataset = create_dataset()

age = patients.age_on("2023-01-01")
dataset.age_group = case(
   when(age < 10).then(1),
   when(age > 80).then(2),
   otherwise="unknown",
)
```

#### Error

```pytb
Traceback (most recent call last):
  File "/workspace/analysis/dataset_definition.py", line 7, in <module>
    dataset.age_group5 = case(
                         ^^^^^
ehrql.query_model.nodes.TypeValidationError: Case.default requires 'ehrql.query_model.nodes.Series[int] | None' but got 'ehrql.query_model.nodes.Series[str]'
```

#### Fixed dataset definition :heavy_check_mark:

```python
from ehrql import create_dataset, case, when
from ehrql.tables.core import patients

dataset = create_dataset()

age = patients.age_on("2023-01-01")
dataset.age_group = case(
   when(age < 10).then(1),
   when(age > 80).then(2),
   otherwise=0,
)
```

### Using `is_in` without a container

#### Failing dataset definition :x:

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()

age = patients.age_on("2023-01-01")
dataset.age_30 = age.is_in(30)
```

#### Error

```pytb
Traceback (most recent call last):
  File "/workspace/analysis/dataset_definition.py", line 7, in <module>
    dataset.age_30 = age.is_in(30)
                     ^^^^^^^^^^^^^
ehrql.query_model.nodes.TypeValidationError: In.rhs requires 'ehrql.query_model.nodes.Series[collections.abc.Set[int]]' but got 'ehrql.query_model.nodes.Series[int]'
```

:notepad_spiral: This is also an error:

```python
dataset.age_30_or_40 = age.is_in(30, 40)
```

#### Fixed dataset definition :heavy_check_mark:

Arguments passed to `is_in` must be wrapped in a python container - a set, list or tuple.
All of the following features defined with `is_in` are valid.

```python
from ehrql import create_dataset
from ehrql.tables.core import patients

dataset = create_dataset()

age = patients.age_on("2023-01-01")
dataset.age_30_list = age.is_in([30])
dataset.age_30_or_40_set = age.is_in({30, 40})
dataset.age_30_or_40_tuple = age.is_in((30, 40))
```
