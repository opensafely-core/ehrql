import datetime
from itertools import islice

import pyarrow

from databuilder.file_formats.validation import ValidationError, validate_headers

PYARROW_TYPE_MAP = {
    bool: pyarrow.bool_,
    # If we added some kind of range specification as part of ColumnSpec we could use
    # that to select smaller numeric types where appropriate
    int: pyarrow.int64,
    float: pyarrow.float64,
    str: pyarrow.string,
    datetime.date: pyarrow.date32,
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


def write_dataset_arrow(filename, results, column_specs):
    schema = schema_from_column_specs(column_specs)
    options = pyarrow.ipc.IpcWriteOptions(compression="zstd", use_threads=True)

    with pyarrow.OSFile(str(filename), "wb") as sink:
        with pyarrow.ipc.new_file(sink, schema, options=options) as writer:
            for results_batch in batch_and_transpose(results, ROWS_PER_BATCH):
                record_batch = pyarrow.record_batch(results_batch, schema=schema)
                writer.write(record_batch)


def schema_from_column_specs(column_specs):
    return pyarrow.schema(
        pyarrow.field(
            name,
            PYARROW_TYPE_MAP[spec.type](),
            nullable=spec.nullable,
        )
        for name, spec in column_specs.items()
    )


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


def validate_dataset_arrow(filename, column_specs):
    target_schema = schema_from_column_specs(column_specs)
    file_schema = read_schema_from_file(filename)
    validate_headers(file_schema.names, target_schema.names)
    if not file_schema.equals(target_schema):
        # This isn't most user-friendly error message, but it will do for now
        raise ValidationError(
            f"File does not have expected schema\n\n"
            f"Schema:\n{file_schema.to_string()}\n\n"
            f"Expected:\n{target_schema.to_string()}"
        )


def read_schema_from_file(filename):
    with pyarrow.OSFile(str(filename), "rb") as f:
        with pyarrow.ipc.open_file(f) as reader:
            return reader.schema
