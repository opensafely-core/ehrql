## TPP
<small class="subtitle">
  <a href="https://github.com/opensafely-core/ehrql/blob/main/ehrql/backends/tpp.py">
    <code>ehrql.backends.tpp.TPPBackend</code>
  </a>
</small>

[TPP](https://tpp-uk.com/) are the developers and operators of the
[SystmOne](https://tpp-uk.com/products/) EHR platform. The ehrQL TPP backend
provides access to primary care data from SystmOne, plus data linked from other
sources.

This backend implements the following table schemas:

 * [beta.core](../schemas/beta.core/)
 * [beta.tpp](../schemas/beta.tpp/)
 * [beta.smoketest](../schemas/beta.smoketest/)

## EMIS
<small class="subtitle">
  <a href="https://github.com/opensafely-core/ehrql/blob/main/ehrql/backends/emis.py">
    <code>ehrql.backends.emis.EMISBackend</code>
  </a>
</small>

!!! warning
    This backend is still under development and is not ready for production use.
    Projects requiring EMIS data should continue to use the [Cohort
    Extractor](https://docs.opensafely.org/study-def/) tool.

[EMIS Health](https://www.emishealth.com/) are the developers and operators of the
[EMIS Web](https://www.emishealth.com/products/emis-web) EHR platform. The ehrQL
EMIS backend provides access to primary care data from EMIS Web, plus data linked
from other sources.

This backend implements the following table schemas:

 * [beta.core](../schemas/beta.core/)
 * [beta.smoketest](../schemas/beta.smoketest/)
