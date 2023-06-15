This page should link to concepts that relate to explaining ehrQL
from the perspective of users that already have experience with cohort-extractor.

:warning: If you are learning ehrQL without having any experience of using cohort-extractor,
the content here may be less relevant for you.

## How does ehrQL relate to cohort-extractor?

* In the long term, ehrQL is intended to eventually replace the existing OpenSAFELY cohort-extractor tool.
  * ehrQL uses dataset definitions in place of [cohort-extractor's study definitions](https://docs.opensafely.org/study-def/).
  * ehrQL's dataset definitions have the same goal as study definitions:
    extracting populations of interest for a research study.
  * In the short term, cohort-extractor will continue to be maintained,
    but new features and datasets will only likely be implemented in ehrQL.
* The rest of the OpenSAFELY platform remains unchanged.
   * In principle, provided that ehrQL supports all the features that you need,
     then you could replace any cohort-extractor steps in an existing OpenSAFELY project with ehrQL instead.

## Does ehrQL do everything that cohort-extractor already does?

* ehrQL is eventually intended to be a complete replacement for cohort-extractor.
* ehrQL can already be used to complete many of the kinds of data query extraction that cohort-extractor was used for.
* However, development is still ongoing.

## Why is ehrQL being developed?

* ehrQL has several goals; two of these are particularly relevant to researchers:
  * With ehrQL, we aim to simplify the learning curve for researchers querying electronic health records
    by providing a consistent and easy-to-understand interface.
    This has been designed based on our experience of developing cohort-extractor
    and seeing how researchers were using cohort-extractor to conduct research.
  * With ehrQL we aim to make it easier for our core software developers to extend ehrQL with new features and datasets.
    This is currently difficult with cohort-extractor's legacy code,
    where features have been "bolted on" over time.
    By doing so, we should be able to shorten the time to add features that researchers want.

## How do I replicate a certain data query pattern from cohort-extractor in ehrQL, or migrate my study definition to a dataset definition?

* :construction: We intend to add examples of certain cohort-extractor patterns
  and their ehrQL analogues.
* For now, consult the [ehrQL examples](examples.md) which may cover what you want to do.
* You can also [ask us for help](getting-help.md).
