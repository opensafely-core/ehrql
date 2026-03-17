import dataclasses

from ehrql.measures.measures import DisclosureControlConfig, MeasureCollection
from ehrql.query_language import DummyDataConfig
from ehrql.query_model.nodes import Dataset


class DefinitionError(Exception):
    "Error in or with the user-supplied definition file"


@dataclasses.dataclass
class ModuleDetails:
    """
    Captures all the values (including possible errors) which we might be interested in
    from a user-supplied definition module
    """

    dataset: Dataset | DefinitionError | None = None
    dataset_dummy_data_config: DummyDataConfig | None = None
    test_data: dict | None = None
    measures: MeasureCollection | DefinitionError | None = None
    measures_dummy_data_config: DummyDataConfig | None = None
    measures_disclosure_control_config: DisclosureControlConfig | None = None
    claimed_permissions: tuple = ()
