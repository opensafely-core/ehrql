from ehrql.renderers import DISPLAY_RENDERERS
from ehrql.utils.itertools_utils import eager_iterator


def generate_table(results, column_specs, render_format):
    headers = list(column_specs.keys())
    results = eager_iterator(results)
    records = [
        {headers[i]: value for i, value in enumerate(result)} for result in results
    ]
    return DISPLAY_RENDERERS[render_format](records)
