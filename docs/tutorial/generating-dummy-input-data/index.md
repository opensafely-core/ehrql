Before running queries against real data in an OpenSAFELY backend,
you should test your queries against dummy data on your own computer.

In the rest of this documentation,
we will use the same small set of dummy data.

:computer: Begin by creating a new directory on your computer and call it `learning-ehrql`.

:notepad_spiral: Any instructions in the documentation
that tell you to run a command from the command-line
will assume that you are in this `learning-ehrql` directory.
You will need to change directory to that directory before running commands.

:computer: At the command-line, navigate to your `learning-ehrql` directory, and run:

```
opensafely exec ehrql:v0 dump-example-data
```

### Check all the files are in the correct place

:warning: Before continuing to learn more about [running ehrQL](../running-ehrql.md),
check that you have the following structure for your files:

```
learning-ehrql
 └─ example-data
     ├─ addresses.csv
     ├─ clinical_events.csv
     ├─ medications.csv
     ├─ ons_deaths.csv
     ├─ patients.csv
     └─ practice_registrations.csv
```
