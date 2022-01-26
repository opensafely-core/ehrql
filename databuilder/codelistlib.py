import csv
from pathlib import Path

from .query_model_old import Codelist


def codelist(codes, system):
    first_code = codes[0]
    has_categories = isinstance(first_code, tuple)
    codes = Codelist(tuple(codes), system, has_categories=has_categories)
    return codes


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
            if category_column:
                raise NotImplementedError(
                    "Categorised codelists are currently unsupported"
                )
            if column not in row:
                raise ValueError(
                    f"Codelist csv file at {filename} does not contain column '{column}'"
                )
            codes.append(row[column].strip())
    codes = Codelist(tuple(codes), system=system, has_categories=bool(category_column))
    return codes


def combine_codelists(first_codelist, *other_codelists):

    for other in other_codelists:
        # First check that all codelists can be combines
        if first_codelist.system != other.system:
            raise ValueError(
                f"Cannot combine codelists from different systems: "
                f"'{first_codelist.system}' and '{other.system}'"
            )
        # TODO codelist categories
        # if first_codelist.has_categories != other.has_categories:
        #     raise ValueError("Cannot combine categorised and uncategorised codelists")

    combined_dict = {}
    for codelist_to_combine in [first_codelist, *other_codelists]:
        for item in codelist_to_combine.codes:
            combined_dict[item] = item
            # TODO codelist categories
            # code = item[0] if codelist_to_combine.has_categories else item
            # if combined_dict.get(code, code) != code:
            #     raise ValueError(
            #         f"Inconsistent categorisation: {item} and {combined_dict[code]}"
            #     )
            # else:
            #     combined_dict[code] = item
    return Codelist(tuple(combined_dict.values()), first_codelist.system)
