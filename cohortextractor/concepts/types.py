class BaseType:
    pass


class PseudoPatientId(BaseType):
    pass


class Date(BaseType):
    pass


class Choice:
    def __init__(self, *choices):
        self.choices = choices
