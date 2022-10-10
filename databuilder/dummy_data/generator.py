from databuilder.orm_utils import orm_classes_from_qm_tables
from databuilder.query_engines.in_memory import InMemoryQueryEngine
from databuilder.query_engines.in_memory_database import InMemoryDatabase
from databuilder.query_model import get_table_nodes


class DummyDataGenerator:
    def __init__(self, variable_definitions):
        self.variable_definitions = variable_definitions
        self.tables = get_table_nodes(*variable_definitions.values())
        self.orm_classes = orm_classes_from_qm_tables(self.tables)

    def get_data(self):
        return [orm_class(patient_id=1) for orm_class in self.orm_classes]

    def get_results(self):
        database = InMemoryDatabase()
        database.setup(self.get_data(), metadata=self.orm_classes[0].metadata)
        engine = InMemoryQueryEngine(database)
        return engine.get_results(self.variable_definitions)
