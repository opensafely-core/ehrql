Dataset definitions written in ehrQL can be run inside different secure
environments, managed by different providers of EHR data.

For each such secure environment, there is a corresponding "backend"
defined in ehrQL. Each ehrQL backend:

* specifies the datasets available inside each secure environment
* does the necessary translation work to allow the same
  dataset definition to run against data modelled in different ways and
  stored in different systems

When writing a dataset definition you don't need to explicitly reference
any particular backend. But, as not every dataset is available in every
backend, the [table schema](schemas.md) you use to write your dataset
definition will determine which backends it can be run against.

Below are the backends currently supported in ehrQL, together with the
list of [table schemas](schemas.md) each one supports.


---8<-- 'includes/generated_docs/backends.md'
