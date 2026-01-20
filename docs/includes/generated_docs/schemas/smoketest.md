
# <strong>smoketest</strong> schema

Available on backends: [**TPP**](../backends.md#tpp), [**EMIS**](../backends.md#emis)

This tiny schema is used to write a [minimal dataset definition][smoketest_repo] that
can function as a basic end-to-end test (or "smoke test") of the OpenSAFELY platform
across all available backends.

[smoketest_repo]: https://github.com/opensafely/test-age-distribution

``` {.python .copy title='To use this schema in an ehrQL file:'}
from ehrql.tables.smoketest import (
    patients,
)
```

<p class="dimension-indicator"><code>one row per patient</code></p>
## patients


<div markdown="block" class="definition-list-wrapper">
  <div class="title">Columns</div>
  <dl markdown="block">
<div markdown="block">
  <dt id="patients.date_of_birth">
    <strong>date_of_birth</strong>
    <a class="headerlink" href="#patients.date_of_birth" title="Permanent link">🔗</a>
    <code><a href="../../language/#DatePatientSeries">date</a></code>
  </dt>
  <dd markdown="block">
Patient's year and month of birth, provided in format YYYY-MM-01. The day will always be the first of the month.

 * Always the first day of a month
 * Never `NULL`
  </dd>
</div>

  </dl>
</div>
