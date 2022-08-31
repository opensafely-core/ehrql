"""An implementation of a simple and fast in-memory database that can be driven by the
the in-memory engine.

See tests in test_database.py for comprehensive examples of how this all works.
"""

from collections import UserDict, defaultdict
from dataclasses import dataclass

from databuilder.orm_factory import table_has_one_row_per_patient
from tests.lib.util import iter_flatten


class InMemoryDatabase:
    def setup(self, *input_data, metadata=None):
        self.all_patients = set()

        input_data = list(iter_flatten(input_data))

        if metadata:
            pass
        elif input_data:
            metadata = input_data[0].metadata
        else:
            assert False, "No source of metadata"
        assert all(item.metadata is metadata for item in input_data)

        sqla_table_to_items = {table: [] for table in metadata.sorted_tables}
        for item in input_data:
            sqla_table_to_items[item.__table__].append(item)

        self.tables = {}
        for sqla_table, items in sqla_table_to_items.items():
            self.tables[sqla_table.name] = self.build_table(sqla_table, items)

    def build_table(self, sqla_table, items):
        col_names = [col.name for col in sqla_table.columns]
        if table_has_one_row_per_patient(sqla_table):
            table_cls = PatientTable
        else:
            table_cls = EventTable
            for ix, item in enumerate(items):
                item.row_id = ix
        row_records = [
            [getattr(item, col_name) for col_name in col_names] for item in items
        ]
        table = table_cls.from_records(col_names, row_records)
        self.all_patients |= table.patients()
        return table

    def host_url(self):
        # Hack!  Other test database classes deriving from tests.lib.databases.DbDetails
        # return a URL that can be used to connect to the database.  See
        # InMemoryQueryEngine.database.
        return self


@dataclass
class PatientTable:
    """A wrapper around a mapping from column names to PatientColumn instances."""

    name_to_col: dict

    @classmethod
    def from_records(cls, col_names, row_records):
        assert col_names[0] == "patient_id"
        if row_records:
            col_records = list(zip(*row_records))
        else:
            col_records = [[]] * len(col_names)
        patients = col_records[0]
        name_to_col = {
            col_name: PatientColumn(dict(zip(patients, col_record)))
            for col_name, col_record in zip(col_names, col_records)
        }
        return cls(name_to_col)

    @classmethod
    def parse(cls, s):
        """Create instance by parsing string.
        >>> tbl = PatientTable.parse(
        ...     '''
        ...       |  i1 |  i2
        ...     --+-----+-----
        ...     1 | 101 | 111
        ...     2 | 201 |
        ...     '''
        ... )
        >>> tbl.name_to_col.keys()
        dict_keys(['patient_id', 'i1', 'i2'])
        >>> tbl['patient_id'].patient_to_value
        {1: 1, 2: 2}
        >>> tbl['i1'].patient_to_value
        {1: 101, 2: 201}
        >>> tbl['i2'].patient_to_value
        {1: 111, 2: None}
        """

        header, _, *lines = s.strip().splitlines()
        col_names = [token.strip() for token in header.split("|")]
        col_names[0] = "patient_id"
        row_records = [
            [parse_value(token.strip()) for token in line.split("|")] for line in lines
        ]
        return cls.from_records(col_names, row_records)

    def __repr__(self):
        width = 17
        lines = []
        lines.append(" | ".join(name.ljust(width) for name in self.name_to_col))
        lines.append("-+-".join("-" * width for _ in self.name_to_col))
        for p in sorted(self["patient_id"].patients()):
            lines.append(
                " | ".join(
                    str(col[p]).ljust(width) for col in self.name_to_col.values()
                )
            )
        return "\n".join(lines)

    def __getitem__(self, name):
        return self.name_to_col[name]

    def to_records(self):
        for p in self.patients():
            yield {name: col[p] for name, col in self.name_to_col.items()}

    def patients(self):
        return self["patient_id"].patients()

    def exists(self):
        return PatientColumn({p: True for p in self.patients()}, False)

    def count(self):
        return PatientColumn({p: 1 for p in self.patients()}, 0)

    def filter(self, predicate):  # noqa A003
        return PatientTable(
            {name: col.filter(predicate) for name, col in self.name_to_col.items()}
        )


@dataclass
class EventTable:
    """A wrapper around a mapping from column names to EventColumn instances."""

    name_to_col: dict

    @classmethod
    def from_records(cls, col_names, row_records):
        if row_records:
            col_records = list(zip(*row_records))
        else:
            col_records = [[]] * len(col_names)
        assert col_names[0] == "patient_id"
        assert col_names[1] == "row_id"
        patients = col_records[0]
        rows = col_records[1]
        name_to_col = {}
        for col_name, col_record in zip(col_names, col_records):
            patient_to_values = defaultdict(dict)
            for p, k, v in zip(patients, rows, col_record):
                patient_to_values[p][k] = v
            name_to_col[col_name] = EventColumn(
                {p: Rows(vv) for p, vv in patient_to_values.items()}
            )
        return cls(name_to_col)

    @classmethod
    def parse(cls, s):
        """Create instance by parsing string.
        >>> tbl = EventTable.parse(
        ...     '''
        ...       |   |  i1 |  i2
        ...     --+---+-----+-----
        ...     1 | 0 | 100 | 110
        ...     1 | 1 | 101 |
        ...     2 | 2 | 200 | 210
        ...     '''
        ... )
        >>> tbl.name_to_col.keys()
        dict_keys(['patient_id', 'row_id', 'i1', 'i2'])
        >>> tbl['patient_id'].patient_to_rows
        {1: Rows({0: 1, 1: 1}), 2: Rows({2: 2})}
        >>> tbl['i1'].patient_to_rows
        {1: Rows({0: 100, 1: 101}), 2: Rows({2: 200})}
        """

        header, _, *lines = s.strip().splitlines()
        col_names = [token.strip() for token in header.split("|")]
        col_names[0] = "patient_id"
        col_names[1] = "row_id"
        row_records = [
            [parse_value(token) for token in line.split("|")] for line in lines
        ]
        return cls.from_records(col_names, row_records)

    def __repr__(self):
        width = 17
        lines = []
        lines.append(" | ".join(name.ljust(width) for name in self.name_to_col))
        lines.append("-+-".join("-" * width for _ in self.name_to_col))
        for p, rows in sorted(self["patient_id"].patient_to_rows.items()):
            for k in rows:
                lines.append(
                    " | ".join(
                        str(col[p][k]).ljust(width) for col in self.name_to_col.values()
                    )
                )
        return "\n".join(lines)

    def __getitem__(self, name):
        return self.name_to_col[name]

    def patients(self):
        return self["patient_id"].patients()

    def exists(self):
        return self["patient_id"].aggregate_values(bool, False)

    def count(self):
        return self["patient_id"].aggregate_values(len, 0)

    def filter(self, predicate):  # noqa A003
        return EventTable(
            {name: col.filter(predicate) for name, col in self.name_to_col.items()}
        )

    def sort(self, sort_index):
        return EventTable(
            {name: col.sort(sort_index) for name, col in self.name_to_col.items()}
        )

    def pick_at_index(self, ix):
        return PatientTable(
            {
                name: col.pick_at_index(ix)
                for name, col in self.name_to_col.items()
                if name != "row_id"
            }
        )


@dataclass
class PatientColumn:
    """A wrapper around a mapping from a patient ID to a Python value, with a default
    value for missing patients.
    """

    patient_to_value: dict
    default: object = None

    @classmethod
    def parse(cls, s, default=None):
        """Create instance by parsing string.
        >>> col = PatientColumn.parse(
        ...     '''
        ...     1 | 101
        ...     2 |
        ...     '''
        ... )
        >>> col.patient_to_value
        {1: 101, 2: None}
        """

        patient_to_value = {}
        for line in s.strip().splitlines():
            p, v = line.split("|")
            patient_to_value[int(p)] = parse_value(v)
        return cls(patient_to_value, default)

    def __repr__(self):
        return "\n".join(f"{p} | {v}" for p, v in sorted(self.patient_to_value.items()))

    def __getitem__(self, patient):
        return self.patient_to_value.get(patient, self.default)

    def patients(self):
        return set(self.patient_to_value)

    def filter(self, predicate):  # noqa A003
        return PatientColumn(
            {p: self[p] for p in self.patients() if predicate[p]},
            self.default,
        )


@dataclass
class EventColumn:
    """A wrapper around a mapping from a patient ID to a Rows instance."""

    patient_to_rows: dict

    @classmethod
    def parse(cls, s):
        """Create instance by parsing string.
        >>> col = EventColumn.parse(
        ...     '''
        ...     1 | 0 | 101
        ...     1 | 1 | 102
        ...     2 | 2 | 201
        ...     2 | 3 | 202
        ...     3 | 4 | ---
        ...     '''
        ... )
        >>> col.patient_to_rows
        {1: Rows({0: 101, 1: 102}), 2: Rows({2: 201, 3: 202}), 3: Rows({})}
        """

        patient_to_values = defaultdict(dict)
        for line in s.strip().splitlines():
            p, k, v = line.split("|")
            if v.strip() == "---":
                patient_to_values[int(p)] = {}
                continue
            patient_to_values[int(p)][int(k)] = parse_value(v)
        patient_to_rows = {p: Rows(vv) for p, vv in patient_to_values.items()}
        return cls(patient_to_rows)

    def __repr__(self):
        return "\n".join(
            f"{p} | {k} | {v}"
            for p, rows in sorted(self.patient_to_rows.items())
            for k, v in rows.items()
        )

    def __getitem__(self, patient):
        return self.patient_to_rows.get(patient, Rows({}))

    def patients(self):
        return set(self.patient_to_rows)

    def aggregate_values(self, fn, default):
        return PatientColumn(
            {
                p: rows.aggregate_values(fn, default)
                for p, rows in self.patient_to_rows.items()
            },
            default,
        )

    def filter(self, predicate):  # noqa A003
        patient_to_rows = {
            p: rows.filter(predicate[p]) for p, rows in self.patient_to_rows.items()
        }
        return EventColumn({p: rows for p, rows in patient_to_rows.items() if rows})

    def sort_index(self):
        return EventColumn(
            {p: rows.sort_index() for p, rows in self.patient_to_rows.items()}
        )

    def sort(self, sort_index):
        return EventColumn(
            {p: rows.sort(sort_index[p]) for p, rows in self.patient_to_rows.items()}
        )

    def pick_at_index(self, ix):
        return PatientColumn(
            {p: rows.pick_at_index(ix) for p, rows in self.patient_to_rows.items()}
        )


class Rows(UserDict):
    """Instances are an ordered mapping from opaque row IDs to values, representing the
    values belonging to a single patient in an EventColumn.
    """

    def __repr__(self):
        return f"Rows({super().__repr__()})"

    def __eq__(self, other):
        """Compare for equality with other.

        Two instances are equal if and only if their items are the same, and their
        keys are in the same order.
        """

        return list(self.items()) == list(other.items())

    def aggregate_values(self, fn, default):
        """Apply aggregation function to all non-null values.

        See https://github.com/opensafely-core/databuilder/issues/465.
        """

        filtered = [v for v in self.values() if v is not None]
        if filtered:
            return fn(filtered)
        else:
            return default

    def filter(self, predicate):  # noqa A003
        """Filter rows, keeping only those whose value in predicate is True."""

        if not isinstance(predicate, Rows):
            # This branch is hit when an EventSeries is filtered by a literal boolean.
            predicate = Rows({k: predicate for k in self})
        return Rows({k: v for k, v in self.items() if predicate[k]})

    def sort_index(self):
        """Map each value to its ordinal position in set of unique values.

        It's important that equal values are given the same position or else the
        resulting sort_index will overspecify the order and we lose the stability of the
        sort operation.
        """

        sorted_values = sorted(set(self.values()), key=nulls_first_order)
        return Rows({k: sorted_values.index(v) for k, v in self.items()})

    def sort(self, sort_index):
        """Sort rows by position in sort_index.

        If two values have the same position, their current position is used as a
        tiebreaker.  This ensures that sorting is stable.
        """

        return Rows(
            {
                k: v
                for (_, _, k, v) in sorted(
                    (sort_index[k], tiebreaker, k, v)
                    for tiebreaker, (k, v) in enumerate(self.items())
                )
            }
        )

    def pick_at_index(self, ix):
        """Return element at given position."""

        k = list(self)[ix]
        return self[k]


def apply_function(fn, *columns):
    """Apply function to list containing EventColumn and/or PatientColumn instances."""

    patients = set().union(*[col.patients() for col in columns])
    if any(col for col in columns if isinstance(col, EventColumn)):
        return EventColumn(
            {
                p: apply_function_to_rows_and_values(fn, [col[p] for col in columns])
                for p in patients
            }
        )
    else:
        return PatientColumn(
            {p: fn(*[col[p] for col in columns]) for p in patients},
            default=fn(*[col.default for col in columns]),
        )


def apply_function_to_rows_and_values(fn, args):
    """Apply function to list containing one or more Rows instances, and zero or more
    Python values.  Each Rows instance should have the same keys."""

    # Check that every Rows instance has the same keys.  This is a sense check for any
    # test data, and not a check that the QM has provided two frames with the same
    # domain.
    keys_list = [tuple(a) for a in args if isinstance(a, Rows)]
    assert len(set(keys_list)) == 1
    keys = keys_list[0]

    values = [a if isinstance(a, Rows) else {k: a for k in keys} for a in args]
    return Rows({k: fn(*[v[k] for v in values]) for k in keys})


def handle_null(fn):
    def fn_with_null(*values):
        if any(v is None for v in values):
            return None
        return fn(*values)

    return fn_with_null


def parse_value(value):
    value = value.strip()
    if value == "T":
        return True
    if value == "F":
        return False
    return int(value) if value else None


def nulls_first_order(key):
    # Usable as a key function to `sorted()` which sorts NULLs first
    return (0 if key is None else 1, key)
