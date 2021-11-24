"""
Shim module to avoid rename churn in studies

We package cohort-extractor-v2 in two ways:

 * docker image
 * pip installable artefact

This module is included in the docker package, but not the pipable artefact.
This allows study authors trying out v2 to avoid churn in the project.yamls by
keeping the same entrypoint for this project (`cohortextractor`).  However when
pip installing the project we will get the `cohortextractor2` directory in
site-packages but _not_ this shim module, avoiding any overlap with the
original cohortextractor.

"""
from cohortextractor2 import *  # noqa: F401, F403
