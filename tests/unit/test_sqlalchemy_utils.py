import pytest
import sqlalchemy

from databuilder.sqlalchemy_utils import is_predicate

table = sqlalchemy.Table(
    "some_table",
    sqlalchemy.MetaData(),
    sqlalchemy.Column("i", type_=sqlalchemy.Integer()),
    sqlalchemy.Column("b", type_=sqlalchemy.Boolean()),
)

integer = table.c.i
boolean = table.c.b


@pytest.mark.parametrize(
    "expected,clause",
    [
        # All comparisons are predicates
        (True, integer == integer),
        (True, integer >= integer),
        (True, integer > integer),
        (True, integer < integer),
        (True, integer <= integer),
        (True, integer != integer),
        # As are boolean operations
        (True, boolean | boolean),
        (True, boolean & boolean),
        (True, ~boolean),
        # And null checks
        (True, integer.is_(None)),
        (True, integer.is_not(None)),
        #
        # But not direct references to boolean columns
        (False, boolean),
        # Or other, non-boolean, binary operations
        (False, integer + integer),
        # Or arbitrary function calls
        (False, sqlalchemy.func.log10(integer)),
    ],
)
def test_is_predicate(expected, clause):
    assert is_predicate(clause) == expected, f"Expected {expected}: {clause}"
