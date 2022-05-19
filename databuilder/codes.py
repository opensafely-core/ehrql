"""
We make each coding system a distinct type. The query model's type checking will then
enforce that queries use the appropriate coding system for a given column.
"""
import csv
import dataclasses
from pathlib import Path

# Populated by `BaseCode.__init_subclass__` below
REGISTRY = {}


class CodelistError(ValueError):
    ...


@dataclasses.dataclass(frozen=True)
class BaseCode:
    value: str

    def __init_subclass__(cls, system_id, **kwargs):
        REGISTRY[system_id] = cls

    # The presence of this method allows query engines to work with values of this type,
    # despite not being explicitly told about them beforehand
    def _to_primitive_type(self):
        return self.value


class BNFCode(BaseCode, system_id="bnf"):
    "Pseudo BNF"


class CTV3Code(BaseCode, system_id="ctv3"):
    "CTV3 (Read V3)"


class DMDCode(BaseCode, system_id="dmd"):
    "Dictionary of Medicines and Devices"


class ICD10Code(BaseCode, system_id="icd10"):
    "ICD-10"


class OPCS4Code(BaseCode, system_id="opcs4"):
    "OPCS-4"


class Read2Code(BaseCode, system_id="readv2"):
    "Read V2"


class SNOMEDCTCode(BaseCode, system_id="snomedct"):
    "SNOMED CT"


@dataclasses.dataclass()
class Codelist:
    codes: set[BaseCode]
    category_maps: dict[str, dict[BaseCode, str]]

    def __post_init__(self):
        # Check that the same codes are used everywhere
        for category_map in self.category_maps.values():
            assert self.codes == category_map.keys()
        # In general, we want categorisations to be accessed as attributes on the
        # codelist e.g.
        #
        #   codelist.group_6_ethnicity
        #
        # But in case there are names which aren't valid Python identifiers (or which
        # clash with other instance attributes) it's always possible to use the
        # dictionary directly e.g.
        #
        #  codelist.category_maps["Group 6 Ethnicity"]
        #
        for name, category_map in self.category_maps.items():
            # Avoid names which could be magic attributes or blat an already existing
            # attribute
            if not name.startswith("_") and not hasattr(self, name):
                setattr(self, name, category_map)


def codelist_from_csv(filename, column, system):
    filename = Path(filename)
    if not filename.exists():
        raise CodelistError(f"No CSV file at {filename}")
    with filename.open("r") as f:
        return codelist_from_csv_lines(f, column, system)


def codelist_from_csv_lines(lines, column, system):
    try:
        code_class = REGISTRY[system]
    except KeyError:
        raise CodelistError(
            f"No system matching '{system}', allowed are: "
            f"{', '.join(REGISTRY.keys())}"
        )
    # `restval` ensures we never get None instead of string, so `.strip()` will
    # never blow up
    reader = csv.DictReader(iter(lines), restval="")
    if column not in reader.fieldnames:
        raise CodelistError(f"No column '{column}' in CSV")
    codes = set()
    # We treat every other column in the CSV as being a mapping from codes to categories
    category_maps = {name: {} for name in reader.fieldnames if name != column}
    for row in reader:
        code_str = row[column].strip()
        if code_str:
            code = code_class(code_str)
            codes.add(code)
            for name, category_map in category_maps.items():
                category_map[code] = row[name].strip()
    return Codelist(codes, category_maps)
