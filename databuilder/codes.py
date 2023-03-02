"""
We make each coding system a distinct type. The query model's type checking will then
enforce that queries use the appropriate coding system for a given column.
"""
import csv
import dataclasses
import re
from pathlib import Path


class CodelistError(ValueError):
    ...


@dataclasses.dataclass(frozen=True)
class BaseCode:
    value: str

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


class BNFCode(BaseCode):
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


class CTV3Code(BaseCode):
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


class ICD10Code(BaseCode):
    "ICD-10"

    regex = re.compile(r"[A-Z][0-9]{2,3}")


class OPCS4Code(BaseCode):
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


class SNOMEDCTCode(BaseCode):
    "SNOMED CT"

    # 6-18 digit number with no leading zeros
    # https://confluence.ihtsdotools.org/display/DOCRELFMT/6.1+SCTID+Data+Type
    regex = re.compile(r"[1-9][0-9]{5,17}")


class DMDCode(BaseCode):
    "Dictionary of Medicines and Devices"

    # Syntactically equivalent to SNOMED-CT
    regex = SNOMEDCTCode.regex


def codelist_from_csv(filename, *, column, category_column=None):
    filename = Path(filename)
    if not filename.exists():
        raise CodelistError(f"No CSV file at {filename}")
    with filename.open("r") as f:
        return codelist_from_csv_lines(
            f, column=column, category_column=category_column
        )


def codelist_from_csv_lines(lines, *, column, category_column=None):
    if category_column is None:
        category_column = column
        return_list = True
    else:
        return_list = False
    # Using `restval=""` ensures we never get None instead of string, so we can always
    # call `.strip()` without blowing up
    reader = csv.DictReader(iter(lines), restval="")
    if column not in reader.fieldnames:
        raise CodelistError(f"No column '{column}' in CSV")
    if category_column not in reader.fieldnames:
        raise CodelistError(f"No column '{category_column}' in CSV")
    code_map = {row[column].strip(): row[category_column].strip() for row in reader}
    # Discard any empty codes
    code_map.pop("", None)
    if return_list:
        return list(code_map)
    else:
        return code_map
