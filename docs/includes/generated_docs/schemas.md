## [beta.tpp](./beta.tpp/)
<small class="subtitle">
  <a href="./beta.tpp/"> view details → </a>
</small>

Available on backends: [**TPP**](../backends#tpp)

This schema defines the data (both primary care and externally linked) available in the
OpenSAFELY-TPP backend. For more information about this backend, see
"[SystmOne Primary Care](https://docs.opensafely.org/data-sources/systmone/)".

## [beta.core](./beta.core/)
<small class="subtitle">
  <a href="./beta.core/"> view details → </a>
</small>

Available on backends: [**TPP**](../backends#tpp), [**EMIS**](../backends#emis)

This schema defines the core tables and columns which should be available in any backend
providing primary care data, allowing dataset definitions written using this schema to
run across multiple backends.

## [beta.emis](./beta.emis/)
<small class="subtitle">
  <a href="./beta.emis/"> view details → </a>
</small>

Available on backends: [**EMIS**](../backends#emis)

This schema defines the data (both primary care and externally linked) available in the
OpenSAFELY-EMIS backend. For more information about this backend, see
"[EMIS Primary Care](https://docs.opensafely.org/data-sources/emis/)".

## [beta.raw.core](./beta.raw.core/)
<small class="subtitle">
  <a href="./beta.raw.core/"> view details → </a>
</small>

Available on backends: [**TPP**](../backends#tpp), [**EMIS**](../backends#emis)

This schema defines the core tables and columns which should be available in any backend
providing primary care data, allowing dataset definitions written using this schema to
run across multiple backends.

The data provided by this schema are minimally transformed. They are very close to the
data provided by the underlying database tables. They are provided for data development
and data curation purposes.

## [beta.raw.emis](./beta.raw.emis/)
<small class="subtitle">
  <a href="./beta.raw.emis/"> view details → </a>
</small>

Available on backends: [**EMIS**](../backends#emis)

This schema defines the data (both primary care and externally linked) available in the
OpenSAFELY-EMIS backend. For more information about this backend, see
"[EMIS Primary Care](https://docs.opensafely.org/data-sources/emis/)".

The data provided by this schema are minimally transformed. They are very close to the
data provided by the underlying database tables. They are provided for data development
and data curation purposes.

## [beta.raw.tpp](./beta.raw.tpp/)
<small class="subtitle">
  <a href="./beta.raw.tpp/"> view details → </a>
</small>

Available on backends: [**TPP**](../backends#tpp)

This schema defines the data (both primary care and externally linked) available in the
OpenSAFELY-TPP backend. For more information about this backend, see
"[SystmOne Primary Care](https://docs.opensafely.org/data-sources/systmone/)".

The data provided by this schema are minimally transformed. They are very close to the
data provided by the underlying database tables. They are provided for data development
and data curation purposes.

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
