## [tpp](schemas/tpp.md)
<small class="subtitle">
  <a href="./tpp/"> view details → </a>
</small>

Available on backends: [**TPP**](backends.md#tpp)

This schema defines the data (both primary care and externally linked) available in the
OpenSAFELY-TPP backend. For more information about this backend, see
"[SystmOne Primary Care](https://docs.opensafely.org/data-sources/systmone/)".

## [core](schemas/core.md)
<small class="subtitle">
  <a href="./core/"> view details → </a>
</small>

Available on backends: [**TPP**](backends.md#tpp), [**EMIS**](backends.md#emis)

This schema defines the core tables and columns which should be available in any backend
providing primary care data, allowing dataset definitions written using this schema to
run across multiple backends.

## [emis](schemas/emis.md)
<small class="subtitle">
  <a href="./emis/"> view details → </a>
</small>

Available on backends: [**EMIS**](backends.md#emis)

This schema defines the data (both primary care and externally linked) available in the
OpenSAFELY-EMIS backend. For more information about this backend, see
"[EMIS Primary Care](https://docs.opensafely.org/data-sources/emis/)".

## [raw.core](schemas/raw.core.md)
<small class="subtitle">
  <a href="./raw.core/"> view details → </a>
</small>

Available on backends: [**TPP**](backends.md#tpp), [**EMIS**](backends.md#emis)

This schema defines the core tables and columns which should be available in any backend
providing primary care data, allowing dataset definitions written using this schema to
run across multiple backends.

The data provided by this schema are minimally transformed. They are very close to the
data provided by the underlying database tables. They are provided for data development
and data curation purposes.

## [raw.emis](schemas/raw.emis.md)
<small class="subtitle">
  <a href="./raw.emis/"> view details → </a>
</small>

Available on backends: [**EMIS**](backends.md#emis)

This schema defines the data (both primary care and externally linked) available in the
OpenSAFELY-EMIS backend. For more information about this backend, see
"[EMIS Primary Care](https://docs.opensafely.org/data-sources/emis/)".

The data provided by this schema are minimally transformed. They are very close to the
data provided by the underlying database tables. They are provided for data development
and data curation purposes.

## [raw.tpp](schemas/raw.tpp.md)
<small class="subtitle">
  <a href="./raw.tpp/"> view details → </a>
</small>

Available on backends: [**TPP**](backends.md#tpp)

This schema defines the data (both primary care and externally linked) available in the
OpenSAFELY-TPP backend. For more information about this backend, see
"[SystmOne Primary Care](https://docs.opensafely.org/data-sources/systmone/)".

The data provided by this schema are minimally transformed. They are very close to the
data provided by the underlying database tables. They are provided for data development
and data curation purposes.

## [smoketest](schemas/smoketest.md)
<small class="subtitle">
  <a href="./smoketest/"> view details → </a>
</small>

Available on backends: [**TPP**](backends.md#tpp), [**EMIS**](backends.md#emis)

This tiny schema is used to write a [minimal dataset definition][smoketest_repo] that
can function as a basic end-to-end test (or "smoke test") of the OpenSAFELY platform
across all available backends.

[smoketest_repo]: https://github.com/opensafely/test-age-distribution
