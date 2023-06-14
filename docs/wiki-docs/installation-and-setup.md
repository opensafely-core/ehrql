# Installation and setup

This page guides you to

* install the necessary prerequisites for running ehrQL on your own computer;
* check that ehrQL is working correctly;
* download a directory of dummy data that we will use
  for demonstrations in the rest of the documentation

It assumes that you have already read the short [Introduction to ehrQL concepts](introduction-to-ehrql-concepts.md).

## Working with ehrQL

### ehrQL is run via a command-line interface

ehrQL is run via the command-line interface —
sometimes referred to as a terminal or shell —
on your computer:

* for Linux or macOS, this is often a program called Terminal
* for Windows, this might be the Command Prompt, PowerShell, Git Bash, or Anaconda Prompt,
depending on what you have installed and prefer to use

:spiral_notepad: It is possible that you have more than one command-line interface installed.

It is not essential,
but it will help if you are already somewhat comfortable with the command-line interface
that you will use to work with ehrQL.

### Writing and editing ehrQL dataset definitions

As well as running ehrQL,
you will need some way of editing your ehrQL dataset definitions
that specify queries you want to run against electronic health record data.

If you do not already have a preferred text editor or integrated development environment for writing code,
we suggest that you try [Visual Studio Code](https://code.visualstudio.com/).
Visual Studio Code is available for Windows, macOS and Linux.

Visual Studio Code also provides an [integrated command-line interface or "terminal"](https://code.visualstudio.com/docs/terminal/basics).
Visual Studio Code's integrated terminal indicates which command-line interface is running.
If you have multiple command-line interfaces installed,
Visual Studio Code also provides an option [to select a different command-line interface](https://code.visualstudio.com/docs/terminal/basics#_terminal-shells).

:spiral_notepad: You should be able to complete all the tutorial steps from within Visual Studio Code.
You can:
* create and edit files, and folders (directories)
* run commands, such as `opensafely`, in the terminal
* run Python and use the Python interactive console from the terminal

## Install the ehrQL prerequisites

:computer: To run ehrQL,
you also need to have additional software installed:

* Docker
* opensafely-cli

If you are already working on OpenSAFELY projects using cohort-extractor,
then you should have these installed.
If that is the case,
you can move on to [Check that you have the latest version of opensafely-cli](#check-that-you-have-the-latest-version-of-opensafely-cli).

### Install Docker

Follow the [Docker installation guidance in the OpenSAFELY documentation](https://docs.opensafely.org/install-docker/).

### Install the opensafely-cli

Follow the [opensafely-cli installation guidance in the OpenSAFELY documentation](https://docs.opensafely.org/opensafely-cli/).

## Check that you have the latest version of opensafely-cli

:computer: At the command-line, run:

```
opensafely upgrade
```

This should either upgrade the version of opensafely-cli that you have,
or tell you that you have the latest version.

## Get the latest ehrQL Docker image

The Docker image contains the ehrQL code packaged up for you to use
via the opensafely-cli.

:computer: At the command-line, run:

```
opensafely pull ehrql
```

## Check that you can run ehrQL

:computer: At the command-line, run:

```
opensafely exec ehrql:v0
```

When the command completes,
you should see a text help message that starts something like:

```
usage: ehrql [-h] [--version]
                   {generate-dataset,dump-dataset-sql,create-dummy-tables,generate-measures,sandbox,test-connection} ...


:spiral_notepad: This command does not specify anything for ehrQL to do as yet.

Generate datasets in OpenSAFELY
...
```

:grey_question: Check the output that you got from running the command.
Did you see something similar?

:heavy_check_mark: If you see the help text as above,
then everything is set up correctly.
You can continue with the rest of this tutorial.\
:x: If you do not see similar help text to above or you get an error,
please [contact us](getting-help.md)
and we can help you get started.

## Downloading some dummy data

Before running queries against real data in an OpenSAFELY backend,
you can test your queries against dummy data on your own computer.

In the rest of this documentation,
we will use the same small set of dummy data.

:computer: Begin by creating a new directory on your computer and call it `learning-ehrql`.

:spiral_notepad: Any instructions in the documentation
that tell you to run a command from the command-line
will assume that you are in this `learning-ehrql` directory.
You will need to change directory to that directory before running commands.

:computer: Retrieve the sample dummy data files for use in this tutorial:
1. Download [this zip file](https://github.com/opensafely-core/ehrql-example-data/archive/refs/heads/main.zip).
2. Create a new directory inside `learning-ehrql` called `example-data`.
3. Inside the zip file are several CSV files. Extract the CSV files to the `example-data` directory.

:warning: Some zip extraction software may nest extracted files inside an additional directory.

### Check all the files are in the correct place

:warning: Before continuing to learn more about [running ehrQL](running-ehrql.md),
check that you have the following structure for your files:

        learning-ehrql
         └─ example-data
             ├─ addresses.csv
             ├─ clinical_events.csv
             ├─ medications.csv
             ├─ ons_deaths.csv
             ├─ patients.csv
             └─ practice_registrations.csv

# What to read next

:fast_forward: [Running ehrQL](running-ehrql.md)
