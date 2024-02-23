import pathlib


class ValidationError(Exception):
    pass


class BaseRowsReader:
    def __init__(self, filename, column_specs):
        if not isinstance(filename, pathlib.Path):
            raise ValidationError(
                f"`filename` must be a pathlib.Path instance got: {filename!r}"
            )
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

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return (
                self.filename == other.filename
                and self.column_specs == other.column_specs
            )
        return NotImplemented

    def __hash__(self):
        # The hash doesn't need to be unique, just cheap to compute and reasonably well
        # distributed across objects. In the event that we have a very large number of
        # RowsReader objects with the same file path and different columns our dicts may
        # underperform: I think we can live with this risk.
        return hash(self.filename)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.filename!r}, {self.column_specs!r})"


def validate_columns(columns, required_columns):
    missing = [c for c in required_columns if c not in columns]
    if missing:
        raise ValidationError(f"Missing columns: {', '.join(missing)}")
