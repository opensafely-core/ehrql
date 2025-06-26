This page describes how ehrQL fits in with a full OpenSAFELY project.

In one sentence:

> Researchers develop an ehrQL query and analysis code on their own computers
> using dummy tables,
> then submit it to the [OpenSAFELY jobs site](https://jobs.opensafely.org)
> to run against real tables in an OpenSAFELY backend.

## Project workflow summary

The workflow for a single study using ehrQL is documented in the
[OpenSAFELY Analysis workflow documentation](https://docs.opensafely.org/workflow/).

In summary:

1. Create a Git repository from the template repository provided and clone it on your local machine.
1. Write a dataset definition in ehrQL that specifies what data you want to extract from the database.
   **Only this step is specific to ehrQL.**
1. Develop analysis scripts using [dummy datasets](#dummy-datasets) in R, Stata, or Python to process and analyse the dummy datasets created by ehrQL.
1. Test the code by running the analysis steps specified in the [project pipeline](https://docs.opensafely.org/actions-pipelines/).
1. Execute the analysis on the [real tables via OpenSAFELY's jobs site](#real-tables). This will generate outputs on the secure server.
1. Check the [output for disclosivity within the server, and redact if necessary](https://docs.opensafely.org/releasing-files/).
1. Release the [outputs on the jobs site](https://docs.opensafely.org/releasing-files/#2-requesting-release-of-outputs-from-the-server).

## Dummy datasets

Because OpenSAFELY doesn't allow researchers direct access to patient data,
researchers must use dummy datasets for developing their analysis code on their own computer.

When an ehrQL action is executed on a researcher's computer (see [Running ehrQL](../explanation/running-ehrql.md)),
ehrQL can generate dummy datasets based on the properties of the tables used in the dataset definition.
Alternatively, users can also provide their own dummy tables.

This allows the dataset definition to be checked for errors,
and produces dummy datasets that can be used to test downstream actions that depend on the output of the ehrQL action.

## Real tables

Executing a dataset definition against real tables in an OpenSAFELY backend involves running the study on the
[OpenSAFELY jobs site](https://jobs.opensafely.org).
More information about the jobs site and how to run a study can be found in the
[OpenSAFELY documentation](https://docs.opensafely.org/jobs-site/).
