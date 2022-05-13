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


def codelist_from_csv(filename, column, system):
    try:
        code_class = REGISTRY[system]
    except KeyError:
        raise CodelistError(
            f"No system matching '{system}', allowed are: "
            f"{', '.join(REGISTRY.keys())}"
        )
    filename = Path(filename)
    if not filename.exists():
        raise CodelistError(f"No CSV file at {filename}")
    codes = []
    with filename.open("r") as f:
        for row in csv.DictReader(f):
            try:
                value = row[column].strip()
            except KeyError:
                raise CodelistError(f"No column '{column}' in {filename}")
            if value:
                codes.append(code_class(value))
    return frozenset(codes)
