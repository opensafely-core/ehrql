import csv
from pathlib import Path

from cohortextractor.query_language import Codelist


def codelist(codes, system):
    first_code = codes[0]
    has_categories = isinstance(first_code, tuple)
    codes = Codelist(codes, system, has_categories=has_categories)
    return codes


def filter_codes_by_category(codelist_obj, include):
    assert (
        codelist_obj.has_categories
    ), "Can only filter codes by category on a categorised codelist"
    new_codes = [
        (code, category)
        for (code, category) in codelist_obj.codes
        if category in include
    ]
    if not len(new_codes):
        raise ValueError(f"codelist has no codes matching categories: {include}")
    return Codelist(new_codes, codelist_obj.system, has_categories=True)


def codelist_from_csv(filename, system, column="code", category_column=None):
    codes = []
    csv_path = Path(filename)
    if not csv_path.exists():
        raise ValueError(f"Codelist csv file at {filename} could not be found")

    with csv_path.open("r") as f:
        for row in csv.DictReader(f):
            # We strip whitespace below. Longer term we expect this to be done
            # automatically by OpenCodelists but for now we want to avoid the
            # problems it creates
            if category_column is not None and category_column not in row:
                raise ValueError(
                    f"Codelist csv file at {filename} does not contain category column '{category_column}'"
                )
            if column not in row:
                raise ValueError(
                    f"Codelist csv file at {filename} does not contain column '{column}'"
                )
            if category_column:
                codes.append((row[column].strip(), row[category_column].strip()))
            else:
                codes.append(row[column].strip())
    codes = Codelist(codes, system=system, has_categories=bool(category_column))
    return codes


def combine_codelists(first_codelist, *other_codelists):
    for other in other_codelists:
        # First check that all codelists can be combines
        if first_codelist.system != other.system:
            raise ValueError(
                f"Cannot combine codelists from different systems: "
                f"'{first_codelist.system}' and '{other.system}'"
            )
        if first_codelist.has_categories != other.has_categories:
            raise ValueError("Cannot combine categorised and uncategorised codelists")

    combined_dict = {}
    for codelist_to_combine in [first_codelist, *other_codelists]:
        for item in codelist_to_combine.codes:
            code = item[0] if codelist_to_combine.has_categories else item
            if code in combined_dict and combined_dict[code] != item:
                raise ValueError(
                    f"Inconsistent categorisation: {item} and {combined_dict.get(code)}"
                )
            else:
                combined_dict[code] = item
    return Codelist(combined_dict.values(), first_codelist.system)
