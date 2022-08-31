import sqlalchemy

from databuilder.query_model import has_one_row_per_patient
from databuilder.sqlalchemy_types import Integer, type_from_python_type

# Generate an integer sequence to use as default IDs. Normally you'd rely on the DBMS to
# provide these, but we need to support DBMSs like Spark which don't have this feature.
next_id = iter(range(1, 2**63)).__next__


# We need each NULL-able column to have an explicit default of NULL. Without this,
# SQLAlchemy will just omit empty columns from the INSERT. That's fine for most DBMSs
# but Spark needs every column in the table to be specified, even if it just has a NULL
# value. Note: we have to use a callable returning `None` here because if we use `None`
# directly SQLAlchemy interprets this is "there is no default".
def null():
    return None


def orm_class_from_schema(base_class, table_name, schema, has_one_row_per_patient):
    """
    Given a SQLAlchemy ORM "declarative base" class, a table name and a schema, return
    an ORM class with the schema of that table
    """
    attributes = {"__tablename__": table_name}

    if has_one_row_per_patient:
        attributes["patient_id"] = sqlalchemy.Column(Integer, primary_key=True)
    else:
        attributes["patient_id"] = sqlalchemy.Column(Integer, nullable=False)
        attributes["row_id"] = sqlalchemy.Column(
            Integer, primary_key=True, default=next_id
        )

    for col_name, type_ in schema.items():
        attributes[col_name] = sqlalchemy.Column(
            type_from_python_type(type_), default=null
        )

    class_name = table_name.title().replace("_", "")

    return type(class_name, (base_class,), attributes)


def orm_class_from_qm_table(base_class, qm_table):
    """
    Given a SQLAlchemy ORM "declarative base" class and a QM table, return an ORM
    class with the schema of that table
    """
    return orm_class_from_schema(
        base_class, qm_table.name, qm_table.schema, has_one_row_per_patient(qm_table)
    )


def orm_class_from_ql_table(base_class, table):
    """
    Given a SQLAlchemy ORM "declarative base" class and a QL table, return an ORM
    class with the schema of that table
    """
    return orm_class_from_qm_table(base_class, table.qm_node)


def table_has_one_row_per_patient(table):
    """Given a SQLAlchemy ORM table, return boolean indicating whether the table has one
    row per patient."""
    return table.columns["patient_id"].primary_key
