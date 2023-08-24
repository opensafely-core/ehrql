class ValidationError(Exception):
    pass


class BaseDatasetReader:
    def __init__(self, filename, column_specs):
        self.filename = filename
        self.column_specs = column_specs
        self._open()
        try:
            self._validate_basic()
        except ValidationError:
            self.close()
            raise

    def _open(self):
        raise NotImplementedError()

    def _validate_basic(self):
        # We can't fully validate the file here because we don't want to read the whole
        # thing (which may be huge) immediately on opening it. But we can do some basic
        # checks that it has the expected columns and that they seem to contain the
        # right sort of thing.
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def __enter__(self):
        return self

    def __exit__(self, *exc_args):
        self.close()


def validate_columns(columns, required_columns):
    missing = [c for c in required_columns if c not in columns]
    if missing:
        raise ValidationError(f"Missing columns: {', '.join(missing)}")
