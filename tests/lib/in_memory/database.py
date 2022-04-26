"""An implementation of a simple and fast in-memory database that can be driven by the
the in-memory engine.

There are two classes:

    * Tables contain a mapping from a name to a column.
    * Columns contain a mapping from a patient id to a list of values, and have a
      default value (which defaults to None) for any patients not in the mapping.

In most cases, this database does not care whether the table or column contains one row
per patient or many rows per patient, and instead relies on the in-memory engine doing
the right thing with a valid QM object.

There are two places where this database does care:

    * When applying a binary operation on two columns, if column C1 contains one row
      per patient and column C2 contains many rows per patient, we have to create
      a mapping with values from C1 with the shape of C2.
    * When getting the single value from a column with one row per patient, we verify
      that the column does contain one row per patient.
"""

from collections import defaultdict
from dataclasses import dataclass

from tests.lib.util import iter_flatten


class InMemoryDatabase:
    def setup(self, *input_data):
        # organize inputs by table for ease of use later
        self.inputs = defaultdict(list)

        input_data = list(iter_flatten(input_data))
        for item in input_data:
            self.inputs[item.__tablename__].append(item)

    def host_url(self):
        # Hack!  Other test database classes deriving from tests.lib.databases.DbDetails
        # return a URL that can be used to connect to the database.  See
        # InMemoryQueryEngine.database.
        return self

    def build_tables(self, patient_tables, event_tables, patient_join_column):
        self._patient_join_column = patient_join_column

        # We need to know the universe before we construct the tables, so we have to iterate over the inputs twice.
        self.universe = set()
        for table, rows in self.inputs.items():
            if table not in patient_tables:
                continue
            for row in rows:
                patient_id = getattr(row, patient_join_column)
                self.universe.add(patient_id)

        self._patient_tables = {}
        self._event_tables = {}
        for table, rows in self.inputs.items():
            if table in patient_tables:
                self._patient_tables[table] = self._build_table(rows, [None])
            elif table in event_tables:
                self._event_tables[table] = self._build_table(rows, [])
            else:  # pragma: no cover
                pass

    def patient_table(self, name):
        return self._patient_tables[name]

    def event_table(self, name):
        return self._event_tables[name]

    def _build_table(self, rows, default_value):
        model = type(rows[0])
        assert all(type(row) == model for row in rows)

        col_names = [col.name for col in model.__table__.columns if col.name != "Id"]
        row_records = [
            [getattr(row, col_name) for col_name in col_names] for row in rows
        ]
        col_names = [
            "patient_id" if name == self._patient_join_column else name
            for name in col_names
        ]

        # Tables need to be able to return values for patients for which they don't have records
        mentioned_ids = {r[0] for r in row_records}
        missing_ids = self.universe - mentioned_ids

        table = Table.from_records(col_names, row_records, missing_ids, default_value)
        return table


@dataclass
class Table:
    name_to_col: dict

    @classmethod
    def from_records(cls, col_names, row_records, missing_patient_ids, default_value):
        assert col_names[0] == "patient_id"
        col_records = list(zip(*row_records))
        patient_ids = col_records[0]
        name_to_col = {
            name: Column.from_values(
                patient_ids, values, missing_patient_ids, default_value
            )
            for name, values in zip(col_names, col_records)
        }
        return cls(name_to_col)

    @classmethod
    def parse(cls, s, missing_patient_ids=None, default_value=None):
        """Create Table instance by parsing string.

        >>> tbl = Table.parse(
        ...     '''
        ...       |  i1 |  i2
        ...     --+-----+-----
        ...     1 | 101 | 111
        ...     1 | 102 | 112
        ...     2 | 201 | 211
        ...     '''
        ... )
        >>> tbl.name_to_col.keys()
        dict_keys(['patient_id', 'i1', 'i2'])
        >>> tbl['patient_id'].patient_to_values
        {1: [1, 1], 2: [2]}
        >>> tbl['i1'].patient_to_values
        {1: [101, 102], 2: [201]}
        """
        missing_patient_ids = missing_patient_ids or []

        header, _, *lines = s.strip().splitlines()
        col_names = [token.strip() for token in header.split("|")]
        col_names[0] = "patient_id"
        row_records = [
            [parse_value(token.strip()) for token in line.split("|")] for line in lines
        ]
        return cls.from_records(
            col_names, row_records, missing_patient_ids, default_value
        )

    def __getitem__(self, name):
        return self.name_to_col[name]

    def __repr__(self):
        width = 17
        rows = []
        rows.append(" | ".join(name.ljust(width) for name in self.name_to_col))
        rows.append("-+-".join("-" * width for _ in self.name_to_col))
        for patient, values in sorted(self["patient_id"].patient_to_values.items()):
            for ix in range(len(values)):
                rows.append(
                    " | ".join(
                        str(col.get_values(patient)[ix]).ljust(width)
                        for col in self.name_to_col.values()
                    )
                )

        return "\n".join(rows)

    def to_records(self):
        for patient in self["patient_id"].patient_to_values:
            yield {
                name: col.get_value(patient) for name, col in self.name_to_col.items()
            }

    def exists(self):
        return self["patient_id"].make_new_column(lambda p, vv: [bool(vv)])

    def count(self):
        return self["patient_id"].make_new_column(lambda p, vv: [len(vv)])

    def filter(self, predicate):  # noqa A003
        return self.make_new_table(lambda col: col.filter(predicate))

    def sort(self, sort_index):
        return self.make_new_table(lambda col: col.sort(sort_index))

    def pick_at_index(self, ix):
        return self.make_new_table(lambda col: col.pick_at_index(ix))

    def make_new_table(self, fn):
        return Table({name: fn(col) for name, col in self.name_to_col.items()})


@dataclass
class Column:
    patient_to_values: dict

    @classmethod
    def from_values(cls, patient_ids, values, missing_patient_ids, default_value):
        patient_to_values = defaultdict(list)
        for patient, value in zip(patient_ids, values):
            patient_to_values[patient].append(value)
        for patient_id in missing_patient_ids:
            patient_to_values[patient_id] = default_value
        return cls(dict(patient_to_values))

    @classmethod
    def parse(cls, s, missing_patient_ids=None, default_value=None):
        """Create Column instance by parsing string.

        >>> col = Column.parse(
        ...     '''
        ...     1 | 101
        ...     1 | 102
        ...     2 | 201
        ...     '''
        ... )
        >>> col.patient_to_values
        {1: [101, 102], 2: [201]}
        """
        missing_patient_ids = missing_patient_ids or []

        patient_ids = []
        values = []
        for line in s.strip().splitlines():
            patient, value = (token.strip() for token in line.split("|"))
            patient_ids.append(int(patient))
            values.append(parse_value(value))
        return cls.from_values(patient_ids, values, missing_patient_ids, default_value)

    def get_values(self, patient):
        return self.patient_to_values.get(patient)

    def get_value(self, patient):
        values = self.get_values(patient)
        assert len(values) == 1
        return values[0]

    def __repr__(self):
        return "\n".join(
            f"{patient} | {value}"
            for patient, values in sorted(self.patient_to_values.items())
            for value in values
        )

    def unary_op(self, fn):
        return self.make_new_column(lambda p, vv: [fn(v) for v in vv])

    def unary_op_with_null(self, fn):
        return self.unary_op(handle_null(fn))

    def binary_op(self, fn, other):
        p_to_vv_1 = self.patient_to_values

        if isinstance(other, Column):
            p_to_vv_2 = other.patient_to_values
        else:
            p_to_vv_2 = {p: [other] for p in self.patient_to_values}

        patients = p_to_vv_1.keys() & p_to_vv_2.keys()

        if any_patient_has_multiple_values(p_to_vv_1):
            if any_patient_has_multiple_values(p_to_vv_2):
                # Check both columns have the same number of values for each patient.
                # This is a sense check for any test data, and not a check that the QM
                # has provided two frames with the same domain.
                assert all(len(p_to_vv_1[p]) == len(p_to_vv_2[p]) for p in patients)
            else:
                # Convert p_to_vv_2 so that it has the same shape as p_to_vv_1.
                p_to_vv_2 = {p: p_to_vv_2[p] * len(p_to_vv_1[p]) for p in patients}
        else:
            if any_patient_has_multiple_values(p_to_vv_2):
                # Convert p_to_vv_1 so that it has the same shape as p_to_vv_2.
                p_to_vv_1 = {p: p_to_vv_1[p] * len(p_to_vv_2[p]) for p in patients}
            else:
                # Nothing to be done.
                pass

        return Column(
            {
                p: [fn(v1, v2) for v1, v2 in zip(p_to_vv_1[p], p_to_vv_2[p])]
                for p in patients
            }
        )

    def binary_op_with_null(self, fn, other):
        return self.binary_op(handle_null(fn), other)

    def aggregate_values(self, fn):
        return self.make_new_column(lambda p, vv: [fn(vv)])

    def filter(self, predicate):  # noqa A003
        def fn(p, vv):
            return [v for v, pred_val in zip(vv, predicate.get_values(p)) if pred_val]

        return self.make_new_column(fn)

    def sort_index(self):
        def fn(_p, vv):
            return [pair[0] for pair in sorted(enumerate(vv), key=lambda pair: pair[1])]

        return self.make_new_column(fn)

    def sort(self, sort_index):
        def fn(p, vv):
            return [
                pair[1]
                for pair in sorted(
                    zip(sort_index.get_values(p), vv), key=lambda pair: pair[0]
                )
            ]

        return self.make_new_column(fn)

    def pick_at_index(self, ix):
        return self.make_new_column(lambda p, vv: [vv[ix]])

    def make_new_column(self, fn):
        return Column({p: fn(p, vv) for p, vv in self.patient_to_values.items()})


def any_patient_has_multiple_values(patient_to_values):
    return any(len(values) != 1 for values in patient_to_values.values())


def handle_null(fn):
    def fn_with_null(*values):
        if any(value is None for value in values):
            return None
        return fn(*values)

    return fn_with_null


def parse_value(value):
    if value == "T":
        return True
    if value == "F":
        return False
    return int(value) if value else None
