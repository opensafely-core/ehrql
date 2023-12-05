# How to work with codelists

A *codelist* is a collection of clinical codes that can be used to classify patients as having certain clinical events or demographic properties.
For example, in a clinical system (e.g., [SNOMED CT](https://digital.nhs.uk/services/terminology-and-classifications/snomed-ct)),
an asthma diagnosis may be indicated by [more than 100 codes](https://www.opencodelists.org/codelist/primis-covid19-vacc-uptake/ast/v1/#full-list).

To help you create, edit, and manage codelists, OpenSAFELY provides a web-based tool called [OpenCodelists](https://www.opencodelists.org).
For more information about how to create and edit codelists, see "[Building a codelist](https://docs.opensafely.org/codelist-creation/)".

## Adding codelists to your dataset definition

Codelists need to be stored as data within your study repository, from where they can be used in your dataset definition.
They live as CSV files in the `codelists/` directory (for more details see "[Adding codelists to a project](https://docs.opensafely.org/codelist-project/)").
Codelists are loaded into variables as follows:

```py
from ehrql import codelist_from_csv

ethnicity_codelist = codelist_from_csv(
    "codelists/ethnicity_codelist_with_categories.csv",
    column="snomedcode",
    category_column="Grouping_6"
)
```

You can add codelists to your `analysis/dataset_definition.py`, but we recommend that you add all your codelists to a file called `analysis/codelists.py` and import them at the top of your dataset definition.
We recommend that you name each codelists you want add in your import statement.
This makes it easier to read and understand your code.

```py
from codelists import my_codelist1, my_codelist2
```

## Combining codelists

To combine different codelists you can use the `+` operator.
This maintains separate codelists for some variable definitions while also allowing to combine them if needed.
For example, the two codelists `chronic_cardiac_codes` and `acute_cardiac_codes` can be combined as follows:

```py
all_cardiac_codes = chronic_cardiac_codes + acute_cardiac_codes
```

## Using a small number of codes

In some cases you may want to use only one or two clinical codes.
You can define a collection of codes as follows:

```py
weight_codes = ["27113001", "162763007"]
```

When you use your user defined codelists, ehrQL will check whether the codes you specified are valid clinical codes in the clinical system you're querying.
For ease of discoverability and reproducibility we recommend [building codelists using OpenCodelists](https://docs.opensafely.org/codelist-creation/), or re-using existing ones.
