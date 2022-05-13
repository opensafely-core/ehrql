"""
We make each coding system a distinct type. The query model's type checking will then
enforce that queries use the appropriate coding system for a given column.
"""
import dataclasses


@dataclasses.dataclass(frozen=True)
class BaseCode:
    value: str


class BNFCode(BaseCode):
    "Pseudo BNF"


class CTV3Code(BaseCode):
    "CTV3 (Read V3)"


class DMDCode(BaseCode):
    "Dictionary of Medicines and Devices"


class ICD10Code(BaseCode):
    "ICD-10"


class OPCS4Code(BaseCode):
    "OPCS-4"


class Read2Code(BaseCode):
    "Read V2"


class SNOMEDCTCode(BaseCode):
    "SNOMED CT"
