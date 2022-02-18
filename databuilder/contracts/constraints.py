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

    @property
    def description(self):
        return ", ".join(self.choices)

    def validate(self, backend_table, column):
        """Validate against data"""
        # TODO


class NotNullConstraint(BaseConstraint):
    """
    Defines a constraint on a Column to ensure no null values
    """

    description = "Must have a value"

    def validate(self, backend_table, column):
        """Validate values exist for all rows in column"""
        # TODO


class UniqueConstraint(BaseConstraint):
    """
    Defines a constraint on a Column to ensure values are unique
    """

    description = "Must be unique"

    def validate(self, backend_table, column):
        """Validate no duplicated values"""
        # TODO


class FirstOfMonthConstraint(BaseConstraint):
    """
    Defines a constraint on a date Column to ensure the day is always the first of the month
    """

    description = "Must be the first day of a month"

    def validate(self, backend_table, column):
        """Validate against data"""
        # TODO
