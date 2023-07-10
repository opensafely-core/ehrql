# ehrQL language reference


## Frames

Frames are the starting point for building any query in ehrQL. You can
think of a Frame as being like a table in a database, in that it
contains multiple rows and multiple columns. But a Frame can have
operations applied to it like filtering or sorting to produce a new
Frame.

You don't need to define any Frames yourself. Instead you import them
from the various [schemas](../schemas/) available in `ehrql.tables` e.g.
```py
from ehrql.tables.beta.core import patients
```

Frames have columns which you can access as attributes on the Frame e.g.
```py
dob = patients.date_of_birth
```

The [schema](../schemas/) documentation contains the full list of
available columns for each Frame. For example, see
[`ehrql.tables.beta.core.patients`](../schemas/beta.core/#patients).

Accessing a column attribute on a Frame produces a [Series](#series),
which are documented elsewhere below.

Some Frames contain at most one row per patient, we call these
PatientFrames; others can contain multiple rows per patient, we call
these EventFrames.

---8<-- 'includes/generated_docs/language__frames.md'

---


## Series

A Series represents a column of values of a certain type. Some Series
contain at most one value per patient, we call these PatientSeries;
others can contain multiple values per patient, we call these
EventSeries. Values can be NULL (i.e. missing) but a Series can never
mix values of different types.

---8<-- 'includes/generated_docs/language__series.md'

---


## Date Arithmetic

---8<-- 'includes/generated_docs/language__date_arithmetic.md'

---


## General

---8<-- 'includes/generated_docs/language__general.md'

---


## Measures

Measures are used for calculating the ratio of one quantity to another
as it varies over time, and broken down by different demographic (or
other) groupings.

---8<-- 'includes/generated_docs/language__measures.md'
