* ehrQL is a query language for electronic health record (EHR) data.
* You run ehrQL in OpenSAFELY to query data.
* The result of an ehrQL query is an output file with one row per patient
  and one column per feature of interest.
* Columns might be features such as:
    * age
    * BMI
    * number of prescriptions of a particular drug

!!! info

    ehrQL is a replacement for OpenSAFELY's cohort-extractor.

    cohort-extractor will continue to work
    and be supported for OpenSAFELY projects
    created before June 2023.

    However, *new* projects should use ehrQL to query data available in OpenSAFELY.
    Please [get in touch with us before you start using ehrQL](introduction/getting-help.md)
    and we can help you get started.

    For more details,
    read our [explanation on what this change means](introduction/guidance-for-existing-cohort-extractor-users.md)
    for existing cohort-extractor users.

## ehrQL provides access to several data sources

Data sources that you can query include:

* Primary care EHR data such as:
    * patient demographics
    * medication events
    * other clinical events
* Some data from secondary care
* External data sets such as death data from ONS

:bulb: Refer to the [list of datasets available through OpenSAFELY](https://docs.opensafely.org/data-sources/).

## How to start learning ehrQL

We suggest that you first read through the introduction section in order,
starting with ["Using this documentation"](introduction/using-this-documentation.md)

The introduction will give you more information about ehrQL
and this documentation.

Next, work through the tutorial section in order,
starting with ["Installation and setup"](tutorial/installation-and-setup.md).

The tutorial will guide you through:

* setting up and running ehrQL on your own computer
* writing ehrQL queries (known as *dataset definitions*)
