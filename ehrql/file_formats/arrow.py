import datetime
from itertools import islice

import pyarrow

from ehrql.file_formats.base import (
    BaseRowsReader,
    FileValidationError,
    validate_columns,
)


PYARROW_TYPE_MAP = {
    bool: pyarrow.bool_,
    # Note ints are handled separately
    float: pyarrow.float64,
    str: pyarrow.string,
    datetime.date: pyarrow.date32,
}

PYARROW_TYPE_TEST_MAP = {
    bool: pyarrow.types.is_boolean,
    int: pyarrow.types.is_integer,
    float: pyarrow.types.is_floating,
    str: pyarrow.types.is_string,
    datetime.date: pyarrow.types.is_date,
}

# When dumping a `pyarrow.Table` or `pandas.DataFrame` to disk, pyarrow takes care of
# chunking up the RecordBatches into "reasonable" sized pieces for us based on the
# number of bytes consumed. But when streaming results to disk as we do below we have to
# do the chunking ourselves. Tracking bytes consumed and splitting batches accordingly
# gets very fiddly and my understanding is that for our purposes the precise size
# doesn't really matter. If we set it very low (tens of rows) then we might get
# performance issues and file bloating due to the overhead each batch adds. If we set it
# very high (millions of rows) then we negate the point of streaming results to disk and
# our memory usage will get noticebly high. Between these bounds I think it makes very
# little practice difference to us.
#
# Reading around bits of old blog posts suggests that we want batches in roughly the
# single to low double-digit megabyte range. Assuming 30 columns, each of an average of
# 32 bits wide, then 64,000 rows takes about 7.7MB, which seems roughly in the right
# ballpark.
ROWS_PER_BATCH = 64000


def write_rows_arrow(filename, rows, column_specs):
    schema, batch_to_pyarrow = get_schema_and_convertor(column_specs)
    options = pyarrow.ipc.IpcWriteOptions(compression="zstd", use_threads=True)

    with pyarrow.OSFile(str(filename), "wb") as sink:
        with pyarrow.ipc.new_file(sink, schema, options=options) as writer:
            for row_batch in batch_and_transpose(rows, ROWS_PER_BATCH):
                record_batch = pyarrow.record_batch(
                    batch_to_pyarrow(row_batch), schema=schema
                )
                writer.write(record_batch)


def get_schema_and_convertor(column_specs):
    fields = []
    convertors = []
    for name, spec in column_specs.items():
        field, column_to_pyarrow = get_field_and_convertor(name, spec)
        fields.append(field)
        convertors.append(column_to_pyarrow)

    def batch_to_pyarrow(columns):
        return [f(column) for f, column in zip(convertors, columns)]

    return pyarrow.schema(fields), batch_to_pyarrow


def get_field_and_convertor(name, spec):
    if spec.type == int:
        type_ = smallest_int_type_for_range(spec.min_value, spec.max_value)
    else:
        type_ = PYARROW_TYPE_MAP[spec.type]()

    # Arrow supports creating dictionaries of any type, but downstream software often
    # only expects strings here so we restrict dictionaries to strings only
    if spec.type is str and spec.categories is not None:
        # Although pyarrow.dictionary indices can obviously never be negative we use
        # `-1` as the minimum below so we always get a signed type; this is because
        # Pandas can't read dictionaries with unsigned index types. See:
        # https://github.com/opensafely-core/ehrql/issues/945
        index_type = smallest_int_type_for_range(-1, len(spec.categories) - 1)
        value_type = type_
        type_ = pyarrow.dictionary(index_type, value_type, ordered=True)
        column_to_pyarrow = make_column_to_pyarrow_with_categories(
            name, index_type, value_type, spec.categories
        )
    else:
        column_to_pyarrow = make_column_to_pyarrow(name, type_)

    field = pyarrow.field(name, type_, nullable=spec.nullable)
    return field, column_to_pyarrow


def make_column_to_pyarrow(name, type_):
    def column_to_pyarrow(column):
        try:
            return pyarrow.array(column, type=type_, size=len(column))
        except Exception as exc:
            exc.add_note(f"Error when writing column '{name}'")
            raise exc

    return column_to_pyarrow


def smallest_int_type_for_range(minimum, maximum):
    """
    Return smallest pyarrow integer type capable of representing all values in the
    supplied range

    Note: this was cribbed from the OpenPrescribing codebase and handles a large range
    of types than we need right now.
    """
    # If either bound is unknown return the default type
    if minimum is None or maximum is None:
        return pyarrow.int64()
    signed = minimum < 0
    abs_max = max(maximum, abs(minimum))
    if signed:
        if abs_max < 1 << 7:
            return pyarrow.int8()
        elif abs_max < 1 << 15:
            return pyarrow.int16()
        elif abs_max < 1 << 31:
            return pyarrow.int32()
        elif abs_max < 1 << 63:
            return pyarrow.int64()
        else:
            assert False
    else:
        if abs_max < 1 << 8:
            return pyarrow.uint8()
        elif abs_max < 1 << 16:
            return pyarrow.uint16()
        elif abs_max < 1 << 32:
            return pyarrow.uint32()
        elif abs_max < 1 << 64:
            return pyarrow.uint64()
        else:
            assert False


def make_column_to_pyarrow_with_categories(name, index_type, value_type, categories):
    value_array = pyarrow.array(categories, type=value_type)
    # NULL values should remain NULL
    mapping = {None: None}
    for index, category in enumerate(categories):
        mapping[category] = index

    def column_to_pyarrow(column):
        try:
            indices = map(mapping.__getitem__, column)
            index_array = pyarrow.array(indices, type=index_type, size=len(column))
        except KeyError as exc:
            raise ValueError(
                f"Invalid value {exc.args[0]!r} for column '{name}'\n"
                f"Allowed are: {', '.join(map(repr, categories))}"
            )
        # This looks a bit like we're including another copy of the `value_array` along
        # with each batch of results. However, Arrow only stores a single copy of this
        # and enforces that subsequent batches use the same set of values.
        return pyarrow.DictionaryArray.from_arrays(index_array, value_array)

    return column_to_pyarrow


def batch_and_transpose(iterable, batch_size):
    """
    Takes an iterable over rows and returns an iterator over batches of columns e.g.

    >>> results = batch_and_transpose(
    ...   [(1, "a"), (2, "b"), (3, "c"), (4, "d")],
    ...   batch_size=3,
    ... )
    >>> list(results)
    [[(1, 2, 3), ('a', 'b', 'c')], [(4,), ('d',)]]

    This is the structure required by Arrow, which is a columar format.
    """
    iterator = iter(iterable)

    def next_transposed_batch():
        row_batch = islice(iterator, batch_size)
        return list(zip(*row_batch))

    return iter(next_transposed_batch, [])


class ArrowRowsReader(BaseRowsReader):
    def _open(self):
        self._fileobj = pyarrow.memory_map(str(self.filename), "rb")
        self._reader = pyarrow.ipc.open_file(self._fileobj)
        self._column_fetchers = []

    def _validate_basic(self):
        # Arrow enforces that all record batches have a consistent schema and that any
        # categorical columns use the same dictionary, so we only need to get the first
        # batch in order to validate
        batch = self._reader.get_record_batch(0)
        validate_columns(
            batch.schema.names, self.column_specs, self.allow_missing_columns
        )

        errors = []
        for name, spec in self.column_specs.items():
            if name not in batch.schema.names:
                self._column_fetchers.append(self._null_fetcher)
                continue

            column = batch.column(name)
            if error := self._validate_column(name, column, spec):
                errors.append(error)
            else:
                self._column_fetchers.append(self._create_fetcher(name))

        if errors:
            raise FileValidationError("\n".join(errors))

    def _validate_column(self, name, column, spec):
        type_test = PYARROW_TYPE_TEST_MAP[spec.type]
        column_type = column.type
        if pyarrow.types.is_dictionary(column_type):
            column_type = column_type.value_type
        if not type_test(column_type):
            return (
                f"Type mismatch in column '{name}': "
                f"expected {spec.type}, got {column.type}"
            )
        if spec.categories is not None:
            if pyarrow.types.is_dictionary(column.type):
                column_categories = column.dictionary.to_pylist()
            else:
                column_categories = sorted(
                    {v for v in column.to_pylist() if v is not None}
                )
            unexpected_categories = set(column_categories) - set(spec.categories)
            if unexpected_categories:
                return (
                    f"Unexpected categories in column '{name}'\n"
                    f"  Categories: {', '.join(column_categories)}\n"
                    f"  Expected: {', '.join(spec.categories)}\n"
                )

    def __iter__(self):
        for i in range(self._reader.num_record_batches):
            batch = self._reader.get_record_batch(i)
            # Use `zip(*...)` to transpose from column-wise to row-wise
            yield from zip(*(fetcher(batch) for fetcher in self._column_fetchers))

    @staticmethod
    def _create_fetcher(column_name):
        def fetcher(batch):
            return batch.column(column_name).to_pylist()

        return fetcher

    @staticmethod
    def _null_fetcher(batch):
        return [None] * batch.num_rows

    def close(self):
        # `self._reader` does not need closing: it acts as a contextmanager, but its exit
        # method is a no-op, see:
        # https://github.com/apache/arrow/blob/1706b095/python/pyarrow/ipc.pxi#L1032-L1036
        self._fileobj.close()
