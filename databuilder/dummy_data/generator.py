import random
from datetime import date, timedelta

from sqlalchemy.orm import declarative_base

from databuilder.dummy_data.query_info import QueryInfo
from databuilder.orm_utils import orm_class_from_schema
from databuilder.query_engines.in_memory import InMemoryQueryEngine
from databuilder.query_engines.in_memory_database import InMemoryDatabase


class DummyDataGenerator:
    # TODO: Make these user configurable. We're deliberately not doing this right now
    # because we want to keep the API surface to zero in the early stages while we
    # iterate on things.
    population_size = 500
    batch_size = 5000
    random_seed = "BwRV3spP"

    def __init__(self, variable_definitions):
        self.variable_definitions = variable_definitions

        # TODO: I dislike using today's date as part of the data generation because it
        # makes the results non-deterministic. However until we're able to infer a
        # suitable time range by inspecting the query, this will have to do.
        self.today = date.today()
        self.rnd = random.Random()

        # Create ORM classes for each of the tables used in the dataset definition
        self.query_info = QueryInfo.from_variable_definitions(self.variable_definitions)
        Base = declarative_base()
        self.orm_classes = {
            table_info.name: orm_class_from_schema(
                Base,
                table_info.name,
                table_info,
                table_info.has_one_row_per_patient,
            )
            for table_info in self.query_info.tables.values()
        }

    def get_data(self):
        data = []
        found = 0

        # Create a version of the query with just the population definition, and an
        # in-memory engine to run it against
        population_query = {"population": self.variable_definitions["population"]}
        database = InMemoryDatabase()
        engine = InMemoryQueryEngine(database)

        # TODO: This needs some sort of timeout as it's possible we won't generate
        # matching patients fast enough
        for batch_start in range(1, 2**63, self.batch_size):
            # Generate batches of patient data and find those matching the population
            # definition
            patient_batch = {
                patient_id: list(self.get_patient_data(patient_id))
                for patient_id in range(batch_start, batch_start + self.batch_size)
            }
            database.setup(*patient_batch.values())
            results = engine.get_results(population_query)
            # Accumulate all data from matching patients, returning once we have enough
            for row in results:
                data.extend(patient_batch[row.patient_id])
                found += 1
                if found >= self.population_size:
                    return data

        # Keep coverage happy: the loop should never complete
        assert False

    def get_results(self):
        database = InMemoryDatabase()
        database.setup(self.get_data())
        engine = InMemoryQueryEngine(database)
        return engine.get_results(self.variable_definitions)

    def get_patient_data(self, patient_id):
        # Seed the random generator using the patient_id so we always generate the same
        # data for the same patient
        self.rnd.seed(f"{self.random_seed}:{patient_id}")
        # Generate some basic demographic facts about the patient which subsequent table
        # generators can use to ensure a consistent patient history
        self.generate_patient_facts()
        # Generate data for each of the tables used in the query
        for table_info in self.query_info.tables.values():
            # Support specialised generators for individual tables, otherwise just make
            # some empty rows
            get_rows = getattr(self, f"rows_for_{table_info.name}", self.empty_rows)
            rows = get_rows(table_info)
            for row in rows:
                # Fill in any values that haven't already been set by a specialised
                # generator
                self.populate_row(table_info, row)
                row["patient_id"] = patient_id
            orm_class = self.orm_classes[table_info.name]
            yield from (orm_class(**row) for row in rows)

    def generate_patient_facts(self):
        # TODO: We could obviously generate more realistic age distributions than this
        date_of_birth = self.today - timedelta(days=self.rnd.randrange(0, 120 * 365))
        age_days = self.rnd.randrange(105 * 365)
        date_of_death = date_of_birth + timedelta(days=age_days)

        self.date_of_birth = date_of_birth
        self.date_of_death = date_of_death if date_of_death < self.today else None
        self.events_start = self.date_of_birth
        self.events_end = min(self.today, date_of_death)

    def rows_for_patients(self, table_info):
        row = {
            "date_of_birth": self.date_of_birth.replace(day=1),
            "date_of_death": self.date_of_death,
        }
        return [row]

    def rows_for_practice_registrations(self, table_info):
        # TODO: Generate more interesting registration histories; for now, we just
        # assume that every patient is permanently registered with a single practice
        # from birth
        row = {
            "start_date": self.events_start,
            "end_date": None,
        }
        return [row]

    def empty_rows(self, table_info):
        # Generate a small handful of events for event-level tables
        max_rows = 1 if table_info.has_one_row_per_patient else 8
        row_count = self.rnd.randrange(max_rows + 1)
        return [{} for _ in range(row_count)]

    def populate_row(self, table_info, row):
        # Remove any columns created by table generators that aren't used in the query
        for extra_column in row.keys() - table_info.columns:
            del row[extra_column]
        # Populate any columns used in the query which haven't already been set
        for name, column_info in table_info.columns.items():
            if name not in row:
                row[name] = self.get_random_value(column_info)

    def get_random_value(self, column_info):
        # TODO: This never returns None although for realism it sometimes should
        if column_info.choices:
            # TODO: It's obviously not true in general that categories are equiprobable
            return self.rnd.choice(column_info.choices)
        elif column_info.type is bool:
            return self.rnd.choice((True, False))
        elif column_info.type is int:
            # TODO: This distributon is obviously ridiculous but will do for now
            return self.rnd.randrange(100)
        elif column_info.type is float:
            # TODO: As is this
            return self.rnd.random() * 100
        elif column_info.type is str:
            # There's not much we can do about non-categorical strings with no
            # comparison values used in the query (generating a random string is
            # unlikely to be useful), but I don't expect we'll get many of these
            return ""
        elif column_info.type is date:
            # Use an exponential distribution to preferentially generate recent events
            # (mean of one year ago). This works OK for the our immediate purposes but
            # we'll no doubt have to iterate on this.
            days_ago = int(self.rnd.expovariate(1 / 365))
            event_date = self.events_end - timedelta(days=days_ago)
            # Clip to the available time range
            return max(event_date, self.events_start)
        else:
            assert False, f"Unhandled type: {column_info.type}"
