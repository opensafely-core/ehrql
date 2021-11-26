class BaseConstraint:
    """
    Base class for Constraints to be enforced on Columns defined in a Contract
    """

    def validate(self, database):
        """Validate against data"""
        raise NotImplementedError


class ChoiceConstraint(BaseConstraint):
    """
    Defines a constraint on a choices Column to ensure data matches the allowed options
    """

    def __init__(self, *choices):
        self.choices = choices

    def validate(self, backend_table, column):
        """Validate against data"""
        # TODO


class NotNullConstraint(BaseConstraint):
    """
    Defines a constraint on a Column to ensure no null values
    """

    def validate(self, backend_table, column):
        """Validate values exist for all rows in column"""
        # TODO


class UniqueConstraint(BaseConstraint):
    """
    Defines a constraint on a Column to ensure values are unique
    """

    def validate(self, backend_table, column):
        """Validate no duplicated values"""
        # TODO


class DateConstraint(BaseConstraint):
    """
    Defines a constraint on a date Column to ensure it conforms to required date format(s)
    """

    base_format = "%Y-%m-%d"

    def __init__(self, match_format: str):
        """
        match_format: str.  A constraint format in the form '%Y-%m-%d' to compare with the base format.
        e.g. '%Y-%m-01' ensures that each date in the backend column repesents the 1st of a month
        """
        self.match_format = match_format

    def validate(self, backend_table, column):
        """Validate against data"""
        # TODO
        # Compare column value (a python date object) formatted with base_format and match_format
        # to ensure they match
