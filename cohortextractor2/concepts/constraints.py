class BaseConstraint:
    """
    Base class for Constraints to be enforced on Columns defined in a Contract
    """


class ChoiceConstraint(BaseConstraint):
    """
    Defines a constraint on a choices Column to ensure data matches the allowed options
    """

    def __init__(self, *choices):
        self.choices = choices


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
