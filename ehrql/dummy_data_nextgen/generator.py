import functools
import itertools
import logging
import random
import string
import time
from bisect import bisect_left
from contextlib import contextmanager
from datetime import date, timedelta

from ehrql.dummy_data_nextgen.query_info import QueryInfo, filter_values
from ehrql.exceptions import CannotGenerate
from ehrql.query_engines.in_memory import InMemoryQueryEngine
from ehrql.query_engines.in_memory_database import InMemoryDatabase
from ehrql.query_model.introspection import all_inline_patient_ids
from ehrql.tables import Constraint
from ehrql.utils.regex_utils import create_regex_generator


log = logging.getLogger()


CHARS = string.ascii_letters + string.digits + ".-+_"

# Use caching to avoid constantly re-creating the generators
get_regex_generator = functools.cache(create_regex_generator)


class DummyDataGenerator:
    def __init__(
        self,
        variable_definitions,
        population_size=10,
        batch_size=5000,
        random_seed="BwRV3spP",
        timeout=60,
        today=None,
    ):
        self.variable_definitions = variable_definitions
        self.population_size = population_size
        self.batch_size = batch_size
        self.random_seed = random_seed
        self.timeout = timeout
        # TODO: I dislike using today's date as part of the data generation because it
        # makes the results non-deterministic. However until we're able to infer a
        # suitable time range by inspecting the query, this will have to do.
        self.today = today if today is not None else date.today()
        self.patient_generator = DummyPatientGenerator(
            self.variable_definitions,
            self.random_seed,
            self.today,
            self.population_size,
        )
        log.info("Using next generation dummy data generation")

    def get_data(self):
        generator = self.patient_generator
        data = generator.get_empty_data()
        found = 0
        generated = 0

        # Create a version of the query with just the population definition, and an
        # in-memory engine to run it against
        population_query = {"population": self.variable_definitions["population"]}
        database = InMemoryDatabase()
        engine = InMemoryQueryEngine(database)

        log.info(
            f"Attempting to generate {self.population_size} matching patients "
            f"(random seed: {self.random_seed}, timeout: {self.timeout}s)"
        )
        log.info(
            "Use `dataset.configure_dummy_data(population_size=N)` "
            "to change number of patients generated"
        )
        start = time.time()

        for patient_id_batch in self.get_patient_id_batches():  # pragma: no branch
            # Generate batches of patient data (just enough to determine population
            # membership) and find those matching the population definition
            patient_batch = {
                patient_id: generator.get_patient_data_for_population_condition(
                    patient_id
                )
                for patient_id in patient_id_batch
            }
            generated += len(patient_batch)
            database.populate(merge_table_data(*patient_batch.values()))
            results = engine.get_results(population_query)
            # Accumulate all data from matching patients, returning once we have enough
            for row in results:
                # Because of the existence of InlinePatientTables it's possible to get
                # patients out of a population which we didn't put in. We want to ignore
                # these.
                if row.patient_id not in patient_batch:
                    continue

                extend_table_data(
                    data,
                    patient_batch[row.patient_id],
                    # Include additional data needed for the dataset but not required just
                    # to determine population membership
                    generator.get_remaining_patient_data(row.patient_id),
                )
                found += 1
                if found >= self.population_size:
                    break

            if found >= self.population_size:
                return data

            log.info(f"Generated {generated} patients, found {found} matching")

            if time.time() - start > self.timeout:
                log.warning(
                    f"Failed to find {self.population_size} matching patients within "
                    f"{self.timeout} seconds — giving up"
                )
                log.info(
                    f"Use e.g. `dataset.configure_dummy_data(timeout={self.timeout * 2})` "
                    f"to try for longer"
                )
                return data

    def get_patient_id_batches(self):
        id_stream = self.get_patient_id_stream()
        while True:
            yield itertools.islice(id_stream, self.batch_size)

    def get_patient_id_stream(self):
        # Where a query involves inline tables we want to extract all the patient IDs
        # and include them in the IDs for which we're going to generate dummy data
        inline_patient_ids = all_inline_patient_ids(*self.variable_definitions.values())
        yield from sorted(inline_patient_ids)
        for i in range(1, 2**63):  # pragma: no branch
            if i not in inline_patient_ids:
                yield i

    def get_results(self):
        database = InMemoryDatabase(self.get_data())
        engine = InMemoryQueryEngine(database)
        return engine.get_results(self.variable_definitions)


class DummyPatientGenerator:
    def __init__(self, variable_definitions, random_seed, today, population_size):
        self.__rnd = None
        self.random_seed = random_seed
        self.today = today
        self.query_info = QueryInfo.from_variable_definitions(variable_definitions)
        self.population_size = population_size

        self.__column_values = {}
        self.__reset_event_range()

    @property
    def rnd(self):
        if self.__rnd is None:
            raise AssertionError(
                "Attempting to use random generation outside of a seed block."
            )
        return self.__rnd

    @contextmanager
    def seed(self, seed):
        old_rnd = self.__rnd
        try:
            self.__rnd = random.Random(f"{self.random_seed}:{seed}")
            yield
        finally:
            self.__rnd = old_rnd

    def get_patient_data_for_population_condition(self, patient_id):
        # Generate data for just those tables needed for determining whether the patient
        # is included in the population
        return self.get_patient_data(patient_id, self.query_info.population_table_names)

    def get_remaining_patient_data(self, patient_id):
        # Generate data for any tables not included above
        return self.get_patient_data(patient_id, self.query_info.other_table_names)

    def get_patient_data(self, patient_id, table_names):
        # Generate some basic demographic facts about the patient which subsequent table
        # generators can use to ensure a consistent patient history
        self.generate_patient_facts(patient_id)
        data = {}
        for name in table_names:
            # Seed the random generator per-table, so that we get the same data no
            # matter what order the tables are generated in
            with self.seed(f"{patient_id}:{name}"):
                table_info = self.query_info.tables[name]
                # Support specialised generators for individual tables, otherwise just make
                # some empty rows
                get_rows = getattr(self, f"rows_for_{table_info.name}", self.empty_rows)
                rows = get_rows(table_info)
                for row in rows:
                    # Fill in any values that haven't already been set by a specialised
                    # generator
                    self.populate_row(table_info, row)
                table_node = table_info.table_node
                column_names = table_node.schema.column_names
                data[table_node] = [
                    (patient_id, *[row[c] for c in column_names]) for row in rows
                ]
        return data

    def get_patient_column(self, column_name):
        for table_name in self.query_info.population_table_names:
            try:
                return self.query_info.tables[table_name].columns[column_name]
            except KeyError:
                pass

    def __reset_event_range(self):
        self.events_start = date(1900, 1, 1)
        self.events_end = self.today

    def generate_patient_facts(self, patient_id):
        # Seed the random generator using the patient_id so we always generate the same
        # data for the same patient
        with self.seed(patient_id):
            self.__reset_event_range()
            iters = 0
            while True:
                iters += 1
                assert iters <= 1000
                # Retry until we have a date of birth and date of death that are
                # within reasonable ranges
                dob_column = self.get_patient_column("date_of_birth")
                if dob_column is not None:
                    date_of_birth = self.get_random_value(dob_column)
                else:
                    date_of_birth = self.today - timedelta(
                        days=self.rnd.randrange(0, 120 * 365)
                    )

                dod_column = self.get_patient_column("date_of_death")
                if dod_column is not None:
                    date_of_death = self.get_random_value(dod_column)
                else:
                    age_days = self.rnd.randrange(105 * 365)
                    date_of_death = date_of_birth + timedelta(days=age_days)

                if (
                    date_of_birth is None
                    or date_of_death is None
                    or (
                        date_of_death >= date_of_birth
                        and (date_of_death - date_of_birth < timedelta(105 * 365))
                    )
                ):
                    break

            self.date_of_birth = date_of_birth
            self.events_start = self.date_of_birth

            if date_of_death is None:
                self.date_of_death = None
                self.events_end = self.today
            else:
                self.date_of_death = (
                    date_of_death if date_of_death < self.today else None
                )
                self.events_end = min(self.today, date_of_death)

    def rows_for_patients(self, table_info):
        row = {
            "date_of_birth": self.date_of_birth,
            "date_of_death": self.date_of_death,
        }
        # Apply any FirstOfMonth constraints
        for key, value in row.items():
            if key in table_info.columns and value is not None:
                if table_info.columns[key].get_constraint(Constraint.FirstOfMonth):
                    row[key] = value.replace(day=1)
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
        max_rows = 1 if table_info.has_one_row_per_patient else 16
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

    def __check_values(self, column_info, result):
        if not result:
            raise CannotGenerate(
                f"Unable to find any values for {column_info.name} that satisfy the population definition."
                + (
                    ""
                    if self.__is_exhaustive(column_info)
                    else " If you believe this should be possible, please report this as a bug."
                )
            )

        for v in result:
            assert v is None or isinstance(v, column_info.type)
        return result

    def __is_exhaustive(self, column_info):
        if column_info.get_constraint(
            Constraint.Categorical
        ) or column_info.get_constraint(Constraint.ClosedRange):
            return True
        return column_info.type not in (int, float, str)

    def get_possible_values(self, column_info):
        try:
            return self.__column_values[column_info]
        except KeyError:
            pass

        with self.seed(f"columns:{column_info.name}"):
            exhaustive = True

            # Arbitrary small number of retries for when we don't manage
            # to generate enough of some unbounded range the first time.
            for _ in range(3):
                if cat_constraint := column_info.get_constraint(Constraint.Categorical):
                    base_values = list(cat_constraint.values)
                elif range_constraint := column_info.get_constraint(
                    Constraint.ClosedRange
                ):
                    base_values = range(
                        range_constraint.minimum,
                        range_constraint.maximum + 1,
                        range_constraint.step,
                    )
                elif column_info.type is date:
                    earliest_possible = date(1900, 1, 1)
                    base_values = [
                        earliest_possible + timedelta(days=i)
                        for i in range((self.today - earliest_possible).days + 1)
                    ]
                elif column_info.type is bool:
                    base_values = [False, True]
                elif column_info.type is int:
                    base_values = list(
                        range(
                            -max(100, self.population_size * 2),
                            max(100, self.population_size * 2),
                        )
                    )
                    exhaustive = False
                elif column_info.type is float:
                    base_values = [
                        0.01 * i for i in range(max(101, self.population_size * 2 + 1))
                    ]
                    exhaustive = False
                elif column_info.type is str:
                    exhaustive = False
                    if column_info._values_used:
                        # If we know some good strings already there's no point in generating
                        # additional strings that almost certainly won't work.'
                        base_values = []
                    elif regex_constraint := column_info.get_constraint(
                        Constraint.Regex
                    ):
                        generator = get_regex_generator(regex_constraint.regex)
                        base_values = [
                            generator(self.rnd)
                            for _ in range(self.population_size * 10)
                        ]
                    else:
                        # A random ASCII string is unlikely to be very useful here, but it at least
                        # makes it a bit clearer what the issue is (that we don't know enough about
                        # the column to generate anything more helpful) rather than the blank string
                        # we always used to return
                        base_values = [
                            "".join(
                                self.rnd.choice(CHARS)
                                for _ in range(self.rnd.randrange(16))
                            )
                            for _ in range(self.population_size * 10)
                        ]
                else:
                    assert False

                base_values = list(base_values)
                base_values.extend(column_info._values_used)
                base_values.append(None)
                if column_info.name == "date_of_death":
                    base_values = [
                        v for v in base_values if v is None or v < self.today
                    ]

                base_values = [
                    v
                    for v in base_values
                    if all(c.validate(v) for c in column_info.constraints)
                ]

                if column_info.query is None:
                    values = base_values
                else:
                    values = filter_values(column_info.query, base_values)

                if exhaustive or values:
                    break

            values.sort(key=lambda x: (x is not None, x))

            values = self.__check_values(column_info, values)
            assert values[0] is None or None not in values

            self.__column_values[column_info] = values
            return values

    def get_random_value(self, column_info):
        values = self.get_possible_values(column_info)
        assert values
        if column_info.type is date:
            result = self.rnd.choice(values)
            if result is None:
                return result
            if self.events_start <= result <= self.events_end:
                return result

            lo = bisect_left(
                values, self.events_start, lo=1 if values[0] is None else 0
            )
            hi = bisect_left(values, self.events_end, lo=lo)
            if hi < len(values) and values[hi] == self.events_end:
                hi += 1
            if lo >= len(values) or hi == 0 or lo == hi:
                # TODO: This is something of a bad hack.
                # We've found ourselves in a situation where we've generated
                # a patient that can't actually have a valid value for this,
                # but we are required to have one. The solution here is to just
                # return some random nonsense and let the population definition
                # exclude this patient.
                #
                # We pick values[0] in particular because that's where None will
                # be, so it's the only possible valid value, but if this column
                # is not nullable then it'll just be an arbitrary date that can't
                # work.
                return values[0]

            i = self.rnd.randrange(lo, hi)
            return values[i]
        else:
            return self.rnd.choice(values)

    def get_empty_data(self):
        return {
            table_info.table_node: [] for table_info in self.query_info.tables.values()
        }


def extend_table_data(target, *others):
    for other in others:
        for key, value in other.items():
            target.setdefault(key, []).extend(value)


def merge_table_data(*dicts):
    target = {}
    extend_table_data(target, *dicts)
    return target
