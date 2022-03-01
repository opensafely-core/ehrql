# OpenSAFELY Data Builder

This tool supports the authoring of OpenSAFELY-compliant research, by:

* Allowing developers to provide dummy data via a CSV file. They can then use this as
  input data when developing analytic models.
* Providing the mechanism by which datasets are extracted from live
  database backends within the OpenSAFELY framework.

:warning: Data Builder is still under development, but is
eventually intended to be a replacement for the [OpenSAFELY Cohort
Extractor](https://github.com/opensafely-core/cohort-extractor).

It is designed to be run within an OpenSAFELY-compliant research
repository, via Docker.  You can find a [template repository here](https://github.com/opensafely/research-template)
and a [Getting Started guide](https://docs.opensafely.org/getting-started/) in the
OpenSAFELY documentation to help you get your study repository set up.

Normally it will be invoked via the [OpenSAFELY command line tool](https://github.com/opensafely-core/opensafely-cli),
as described in the [documentation](https://docs.opensafely.org/getting-started/).

If running it directly, it should be run from within the research repository.
To run the latest version via Docker and access its full help:

    docker run --rm ghcr.io/opensafely-core/databuilder:v0 --help

# For developers

Please see [the additional information](DEVELOPERS.md).

There is also [a glossary](GLOSSARY.md) of terms used in the codebase.

# About the OpenSAFELY framework

The OpenSAFELY framework is a Trusted Research Environment (TRE) for electronic
health records research in the NHS, with a focus on public accountability and
research quality.

Read more at [OpenSAFELY.org](https://opensafely.org).
