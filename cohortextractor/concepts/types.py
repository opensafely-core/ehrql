class BaseType:
    """
    Base class for Column types defined in a Contract
    """

    # Subclasses must specify the backend Column types that they allow, as
    # tuples of one or more keys from cohortextractor.sqlalchemy_types.TYPES_BY_NAME
    allowed_backend_types: tuple = NotImplemented


class PseudoPatientId(BaseType):
    """A type representing a pseudonymised patient ID"""

    allowed_backend_types = ("integer", "varchar")


class Date(BaseType):
    """A type representing a date"""

    allowed_backend_types = ("date",)


class Choice(BaseType):
    """
    A type which restricts column values to a limited set of choices.
    """

    allowed_backend_types = ("integer", "varchar")

    def __init__(self, *choices):
        self.choices = choices
