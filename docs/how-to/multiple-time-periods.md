# How to run your ehrQL over multiple time periods

Sometimes you may need to run the same ehrQL separately over multiple months or years.
This may be needed for instance to capture discrete periods of patient activity
through time, or where there are multiple study index dates.

Other than making a separate ehrQL file for each period required, there are two
supported options:

## 1. Pass parameters via the project.yaml
- Pass in a custom parameter to each ehrQL action (in the `project.yaml`) that allows us
  to use the same code with a different date each time. Each period is a separate
  action. 
- This creates a full patient-level dataset for each period, allowing concatenation and
  further analysis. 
- If you are running for many periods (e.g. every month for several years) you may need
  to write a script to generate all the actions required. It may be computationally
  expensive and require more storage space.
- Find more details in the how-to guide on [re-using ehrQL with custom
  parameters](./parameterise-ehrql.md). 

## 2. The measures framework
- The measures framework is used to calculate quotients (i.e. a numerator divided by a
  denominator) for each period, which can be broken down by other variables (e.g. age
  bands). 
- The periods ("intervals"), numerators, denominators and groups are all defined using
  ehrQL in a modified dataset definition. 
- This approach does **not** generate a full patient-level dataset for each period -
  only a single measures output, showing the numerators and denominators for each
  measure for each period. 
- This is ideal if you are only planning simple calculations on your results (e.g.
  trends/rates over time) or as an initial step to check that your overall results look
  sensible. 
- This approach creates smaller files and should generally run faster than the
  Parameters approach. 
- Find more details in the guide to the [measures framework](../explanation/measures.md).
