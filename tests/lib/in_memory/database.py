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
        self.all_patients = set()

        input_data = list(iter_flatten(input_data))
        metadata = input_data[0].metadata
        assert all(item.metadata is metadata for item in input_data)

        sqla_table_to_items = {table: [] for table in metadata.sorted_tables}
        for item in input_data:
            sqla_table_to_items[item.__table__].append(item)

        self.tables = {}
        for sqla_table, items in sqla_table_to_items.items():
            self.tables[sqla_table.name] = self.build_table(sqla_table, items)

    def build_table(self, sqla_table, items):
        col_names = [col.name for col in sqla_table.columns if col.name != "Id"]
        row_records = [
            [getattr(item, col_name) for col_name in col_names] for item in items
        ]
        col_names[0] = "patient_id"
        table = Table.from_records(col_names, row_records)
        self.all_patients |= table["patient_id"].patient_to_values.keys()
        return table

    def host_url(self):
        # Hack!  Other test database classes deriving from tests.lib.databases.DbDetails
        # return a URL that can be used to connect to the database.  See
        # InMemoryQueryEngine.database.
        return self


@dataclass
class Table:
    name_to_col: dict

    @classmethod
    def from_records(cls, col_names, row_records):
        assert col_names[0] == "patient_id"
        if row_records:
            col_records = list(zip(*row_records))
        else:
            col_records = [[]] * len(col_names)
        patient_ids = col_records[0]
        name_to_col = {
            name: Column.from_values(patient_ids, values)
            for name, values in zip(col_names, col_records)
        }
        return cls(name_to_col)

    @classmethod
    def parse(cls, s):
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

        header, _, *lines = s.strip().splitlines()
        col_names = [token.strip() for token in header.split("|")]
        col_names[0] = "patient_id"
        row_records = [
            [parse_value(token.strip()) for token in line.split("|")] for line in lines
        ]
        return cls.from_records(col_names, row_records)

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
        return self["patient_id"].make_new_column(
            lambda p, vv: [bool(vv)], default=False
        )

    def count(self):
        return self["patient_id"].make_new_column(
            lambda p, vv: [len(vv)],
            default=0,
        )

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
    default: object

    @classmethod
    def from_values(cls, patient_ids, values, default=None):
        patient_to_values = defaultdict(list)
        for patient, value in zip(patient_ids, values):
            patient_to_values[patient].append(value)
        return cls(dict(patient_to_values), default)

    @classmethod
    def parse(cls, s, default=None):
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

        patient_ids = []
        values = []
        for line in s.strip().splitlines():
            patient, value = (token.strip() for token in line.split("|"))
            patient_ids.append(int(patient))
            values.append(parse_value(value))
        return cls.from_values(patient_ids, values, default)

    def get_values(self, patient):
        return self.patient_to_values.get(patient, [self.default])

    def get_value(self, patient):
        values = self.get_values(patient)
        assert len(values) == 1
        return values[0]

    def patients(self):
        return self.patient_to_values.keys()

    def any_patient_has_multiple_values(self):
        return any(len(self.get_values(p)) != 1 for p in self.patients())

    def __repr__(self):
        return "\n".join(
            f"{patient} | {value}"
            for patient, values in sorted(self.patient_to_values.items())
            for value in values
        )

    def unary_op(self, fn):
        default = fn(self.default)
        return self.make_new_column(lambda p, vv: [fn(v) for v in vv], default)

    def unary_op_with_null(self, fn):
        return self.unary_op(handle_null(fn))

    def binary_op(self, fn, other):
        patients = self.patients() | other.patients()

        self_values = self.patient_to_values
        other_values = other.patient_to_values
        if self.any_patient_has_multiple_values():
            if other.any_patient_has_multiple_values():
                # Check both columns have the same number of values for each patient.
                # This is a sense check for any test data, and not a check that the QM
                # has provided two frames with the same domain.
                assert all(
                    len(self.get_values(p)) == len(other.get_values(p))
                    for p in patients
                )
            else:
                # Convert other so that it has the same shape as self.
                other_values = {
                    p: other.get_values(p) * len(self.get_values(p)) for p in patients
                }
        else:
            if other.any_patient_has_multiple_values():
                # Convert self so that it has the same shape as other.
                self_values = {
                    p: self.get_values(p) * len(other.get_values(p)) for p in patients
                }
            else:
                # Nothing to be done.
                pass

        reshaped_self = Column(self_values, self.default)
        reshaped_other = Column(other_values, other.default)

        return Column(
            {
                p: [
                    fn(v1, v2)
                    for v1, v2 in zip(
                        reshaped_self.get_values(p), reshaped_other.get_values(p)
                    )
                ]
                for p in patients
            },
            default=fn(reshaped_self.default, reshaped_other.default),
        )

    def binary_op_with_null(self, fn, other):
        return self.binary_op(handle_null(fn), other)

    def aggregate_values(self, fn, default):
        def fn_with_null(values):
            if any(value is None for value in values):
                return None
            return fn(values)

        return self.make_new_column(lambda p, vv: [fn_with_null(vv)], default)

    def filter(self, predicate):  # noqa A003
        def fn(p, vv):
            pred_values = predicate.get_values(p)
            if len(pred_values) == 1:
                pred_values = pred_values * len(vv)
            return [v for v, pred_val in zip(vv, pred_values) if pred_val]

        return self.make_new_column(fn, self.default)

    def sort_index(self):
        def fn(p, vv):
            return [pair[0] for pair in sorted(enumerate(vv), key=lambda pair: pair[1])]

        return self.make_new_column(fn, default=None)

    def sort(self, sort_index):
        def fn(p, vv):
            return [
                pair[1]
                for pair in sorted(
                    zip(sort_index.get_values(p), vv), key=lambda pair: pair[0]
                )
            ]

        return self.make_new_column(fn, default=None)

    def pick_at_index(self, ix):
        return self.make_new_column(lambda p, vv: [vv[ix]], self.default)

    def make_new_column(self, fn, default):
        new_patient_to_values = {
            p: fn(p, vv) for p, vv in self.patient_to_values.items()
        }
        return Column(
            {p: vv for p, vv in new_patient_to_values.items() if vv},
            default,
        )


def handle_null(fn):
    def fn_with_null(*values):
        if any(value is None for value in values):
            return None
        return fn(*values)

    return fn_with_null


def parse_value(value):
    return int(value) if value else None
