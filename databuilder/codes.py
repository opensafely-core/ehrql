"""
We make each coding system a distinct type. The query model's type checking will then
enforce that queries use the appropriate coding system for a given column.
"""
import csv
import dataclasses
import re
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

    def __post_init__(self):
        if not self.regex.fullmatch(self.value):
            raise ValueError(f"Invalid {self.__class__.__name__}: {self.value}")

    @classmethod
    def _primitive_type(cls):
        return str

    # The presence of this method allows query engines to work with values of this type,
    # despite not being explicitly told about them beforehand
    def _to_primitive_type(self):
        return self.value


class BNFCode(BaseCode, system_id="bnf"):
    "Pseudo BNF"

    regex = re.compile(
        r"""
        # Standard BNF code
          # Chapter, Section, Paragraph, Sub-paragraph
          [01][0-9]{6}
          # Chemical
          [0-9A-Z]{2}
          # Product, strength-formulation, generic equivalent
          ([A-Z][0-9A-Z]){3}
        | # OR
        # Appliances
        2[0-3][0-9]{9}
        """,
        re.VERBOSE,
    )


class CTV3Code(BaseCode, system_id="ctv3"):
    "CTV3 (Read V3)"

    # Some of the CTV3 codes in the OpenCodelists coding system database (though not any
    # actually used in codelists) violate the below format, either by having a leading
    # dot or by starting with a tilde. However I have confirmed that, aside from a tiny
    # handful of cases, these invalid codes are not used in the database so there should
    # never be a need to create codelists which use them.
    regex = re.compile(
        r"""
        [0-9A-Za-z]{5}
        | [0-9A-Za-z]{4}\.{1}
        | [0-9A-Za-z]{3}\.{2}
        | [0-9A-Za-z]{2}\.{3}
        """,
        re.VERBOSE,
    )


class ICD10Code(BaseCode, system_id="icd10"):
    "ICD-10"

    regex = re.compile(r"[A-Z][0-9]{2,3}")


class OPCS4Code(BaseCode, system_id="opcs4"):
    "OPCS-4"

    # The documented structure requires three digits, and a dot between the 2nd and 3rd
    # digit, but the codes we have in OpenCodelists omit the dot and sometimes have only
    # two digits.
    # https://en.wikipedia.org/wiki/OPCS-4#Code_structure
    regex = re.compile(
        r"""
        # Uppercase letter excluding I
        [ABCDEFGHJKLMNOPQRSTUVWXYZ]
        [0-9]{2,3}
        """,
        re.VERBOSE,
    )


class SNOMEDCTCode(BaseCode, system_id="snomedct"):
    "SNOMED CT"

    # 6-18 digit number with no leading zeros
    # https://confluence.ihtsdotools.org/display/DOCRELFMT/6.1+SCTID+Data+Type
    regex = re.compile(r"[1-9][0-9]{5,17}")


class DMDCode(BaseCode, system_id="dmd"):
    "Dictionary of Medicines and Devices"

    # Syntactically equivalent to SNOMED-CT
    regex = SNOMEDCTCode.regex


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
