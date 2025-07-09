
<h4 class="attr-heading" id="get_parameter" data-toc-label="get_parameter" markdown>
  <tt><strong>get_parameter</strong>(<em>name</em>, <em>type=<class 'str'></em>, <em>default=None</em>)</tt>
</h4>
<div markdown="block" class="indent">
Define and retrieve user-specified parameters that have been passed on the command line.

User-definied parameters are passed after a `--`, in the format `--key value`

For example, to pass values for two parameters, `max_age` and `region`:

```
generate-dataset /path/to/dataset_definiton/.py -- --max_age 70 --sex female
```

Multiple values can be passed per parameter, and will be parsed
as a list, e.g.
```
generate-dataset /path/to/dataset_definiton/.py -- --sex male female
```
or
```
generate-dataset /path/to/dataset_definiton/.py -- --sex male --sex female
```

For each parameter, in the dataset definition, call `get_parameter()`, e.g.:
```
    sex = get_parameter(name="sex")
```

Parameters are parsed as strings, unless a `type` is explicitly specified.
Usually this will be one of the standard python types, such as integers or floats.
e.g. to convert the `max_age` value to an integer:
```
    max_age = get_parameter(name="max_age", type=int)
```

A value must be provided for each parameter defined by `get_parameter()` *unless*
a default value is specified.
e.g. to default to 100 as the `max_age` value if no value is provided:
```
    max_age = get_parameter(name="max_age", default=100)
```

To use in ehrQL:

```ehrql
from ehrql import create_dataset, get_parameter
from ehrql.tables.core import patients


max_age = get_parameter(name="max_age", type=int, default=20)
sex = get_parameter(name="sex", default="male")

dataset = create_dataset()
age = patients.age_on("2025-01-01")

dataset.define_population((age < max_age) & (patients.sex==sex))
```
</div>
