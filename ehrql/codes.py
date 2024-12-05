"""
We make each coding system a distinct type. The query model's type checking will then
enforce that queries use the appropriate coding system for a given column.
"""

import csv
import dataclasses
import re
from pathlib import Path


class CodelistError(ValueError): ...


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


# A base class for fields that are concatenated lists of clinical codes. This occurs
# in the admitted patient care spell (apcs) table of hospital episode statistics for
# all_diagnoses (ICD10 codes), and all_procedures (OPCS4 codes).
#
# This inherits from str because that's what the underlying data is, but is in this
# file as it's sort of a code. In future a better implementation might be to parse the
# field value into a Set of clinical codes.
@dataclasses.dataclass(frozen=True)
class BaseMultiCodeString(str):
    @classmethod
    def _code_type(cls):
        raise NotImplementedError(
            "BaseMultiCodeString subclasses must implement the _code_type method"
        )

    @classmethod
    def _primitive_type(cls):
        return str


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
    "CTV3 (Read v3)"

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
    "SNOMED-CT"

    # 6-18 digit number with no leading zeros
    # https://confluence.ihtsdotools.org/display/DOCRELFMT/6.1+SCTID+Data+Type
    regex = re.compile(r"[1-9][0-9]{5,17}")


# Dictionary of Medicines and Devices
class DMDCode(BaseCode):
    "dm+d"

    # Syntactically equivalent to SNOMED-CT
    regex = SNOMEDCTCode.regex


#
# ICD10 codelist as concatenated string
#
# This is specifically for fields in the admitted patient care (APC) part
# of the hospital episode statistics (HES) data where there are fields
# that are a concatenation of all diagnosis codes for a patient's episode
# or spell.
class ICD10MultiCodeString(BaseMultiCodeString):
    "Multiple ICD-10 codes"

    @classmethod
    def _code_type(cls):
        return ICD10Code

    # We want to allow prefix searching, so when we check the regex we
    # want to account for that
    regex = re.compile(r"[A-Z][0-9]{0,3}")


def codelist_from_csv(filename, *, column, category_column=None):
    """
    Read a codelist from a CSV file as either a list or a dictionary (for categorised
    codelists).

    _filename_<br>
    Path to the file on disk, relative to the root of your repository. (Remember to use
    UNIX/style/forward-slashes not Windows\\style\\backslashes.)

    _column_<br>
    Name of the column in the CSV file which contains the codes.

    _category_column_<br>
    Optional name of a column in the CSV file which contains categories to which each
    code should be mapped. If this argument is passed then the resulting codelist will
    be a dictionary mapping each code to its corresponding category. This can be passed
    to the [`to_category()`](#CodePatientSeries.to_category) method to map a series of
    codes to a series of categories.
    """
    filename = Path(filename)
    if not filename.exists():
        # If the character which comes after the backslash in the string literal happens
        # to form a valid escape sequence then no backslash will appear in the compiled
        # string. Checking the repr for backslashes has false positives (e.g. a tab
        # character will trigger it) but that seems OK in this context.
        if "\\" in repr(filename):
            hint = (
                "\n\n"
                "HINT: Use forward slash (/) instead of backslash (\\) in file paths"
            )
        else:
            hint = ""
        raise CodelistError(f"No CSV file at {filename}{hint}")
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
