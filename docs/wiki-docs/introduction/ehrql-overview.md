This page gives a very concise guide to ehrQL,
with links in each section to more detailed explanations.

## What is ehrQL?

* ehrQL is a Python-based query language for electronic health record (EHR) data.
* You run ehrQL in OpenSAFELY to query data and produce an output file with one row per patient and one column per feature of interest.
* Columns might be variables such as:
  * age
  * BMI
  * number of prescriptions of a particular drug
* :bulb: This [explanation gives an overview of what ehrQL is and how it works](../tutorial/ehrql-concepts-in-depth.md).

## What data can I access through ehrQL?

* Primary care EHR data such as:
  * [patient demographics](https://github.com/opensafely-core/ehrql/blob/c28b2e82defe43c2c1e8f379fb9308a952455d52/databuilder/tables/beta/tpp.py#L27-L58)
  * [medication events](https://github.com/opensafely-core/ehrql/blob/c28b2e82defe43c2c1e8f379fb9308a952455d52/databuilder/tables/beta/tpp.py#L167-L170)
  * [other clinical events](https://github.com/opensafely-core/ehrql/blob/c28b2e82defe43c2c1e8f379fb9308a952455d52/databuilder/tables/beta/tpp.py#L159-L163)
* Some data from [secondary care](https://github.com/opensafely-core/ehrql/blob/c28b2e82defe43c2c1e8f379fb9308a952455d52/databuilder/tables/beta/tpp.py#L230-L271)
* External data sets such as [death data from ONS](https://github.com/opensafely-core/ehrql/blob/c28b2e82defe43c2c1e8f379fb9308a952455d52/databuilder/tables/beta/tpp.py#L123-L155)
* A full [list of datasets available through OpenSAFELY is available](https://docs.opensafely.org/data-sources/).
  * :warning: We are working on making these available through ehrQL, but all may not yet be available.

## ehrQL builds datasets that detail features of populations

* ehrQL uses *dataset definitions* to query electronic health record data.
* The result of a *dataset definition* is a *dataset*.
* Datasets are a tabular collection of *features* describing *populations*.
* :bulb: There is a [full explanation of these concepts](../tutorial/ehrql-concepts-in-depth.md).

## How to run ehrQL

* In just one concise line: write a dataset definition,
  and then use `opensafely-cli` to run the ehrQL in that dataset definition.
* :bulb: There is a [tutorial that introduces how to run ehrQL](../tutorial/running-ehrql.md).

## How does ehrQL fit in with a full OpenSAFELY project?

* Typically, ehrQL is used when working on a full OpenSAFELY project.
  A project may involve data querying and extraction,
  analysis.
  and presentation steps.
* :bulb: There is an [explanation of how to use ehrQL in an OpenSAFELY project](../tutorial/ehrql-and-opensafely.md).
