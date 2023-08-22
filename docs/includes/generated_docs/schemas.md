## [beta.tpp](./beta.tpp/)
<small class="subtitle">
  <a href="./beta.tpp/"> view details → </a>
</small>

Available on backends: [**TPP**](../backends#tpp)

This defines all the data (both primary care and externally linked) available in the
OpenSAFELY-TPP backend.

## [beta.core](./beta.core/)
<small class="subtitle">
  <a href="./beta.core/"> view details → </a>
</small>

Available on backends: [**TPP**](../backends#tpp), [**EMIS**](../backends#emis)

This schema defines the core tables and columns which should be available in any backend
providing primary care data, allowing dataset definitions written using this schema to
run across multiple backends.

!!! warning
    This schema is still a work-in-progress while the EMIS backend remains under
    development. Projects requiring EMIS data should continue to use the [Cohort
    Extractor](https://docs.opensafely.org/study-def/) tool.

## [beta.smoketest](./beta.smoketest/)
<small class="subtitle">
  <a href="./beta.smoketest/"> view details → </a>
</small>

Available on backends: [**TPP**](../backends#tpp), [**EMIS**](../backends#emis)

This tiny schema is used to write a [minimal dataset definition][smoketest_repo] that
can function as a basic end-to-end test (or "smoke test") of the OpenSAFELY platform
across all available backends.

[smoketest_repo]: https://github.com/opensafely/test-age-distribution

## [examples.tutorial](./examples.tutorial/)
<small class="subtitle">
  <a href="./examples.tutorial/"> view details → </a>
</small>

_This schema is for development or testing purposes and is not available on any backend._

This example schema is for use in the ehrQL tutorial.
