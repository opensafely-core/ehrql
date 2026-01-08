import datetime

from ehrql import Dataset
from ehrql.dummy_data_nextgen.generator import DummyDataGenerator
from ehrql.tables import EventFrame, Series, table


@table
class annotated_events(EventFrame):
    date_start = Series(datetime.date)
    date_end = Series(datetime.date)
    code = Series(str)


def test_dummy_data_generator_with_relational_column_constraints():
    dataset = Dataset()
    dataset.define_population(annotated_events.exists_for_patient())

    last_event = annotated_events.sort_by(
        annotated_events.date_start
    ).last_for_patient()

    dataset.is_valid = last_event.date_start <= last_event.date_end

    variable_definitions = dataset._compile()
    generator = DummyDataGenerator(variable_definitions)
    generator.population_size = 10
    generator.batch_size = 5
    results = list(generator.get_results())

    # We might want to mix in some invalid results in the future?
    assert set(r.is_valid for r in results).issubset({True, None})
