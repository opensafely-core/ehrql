import sqlalchemy
import sqlalchemy.orm


def setup(schema):
    registry = sqlalchemy.orm.registry()
    ids = iter(range(1, 2**63)).__next__
    patient_id_column = "PatientId"
    patient_tables = [
        build_table(name, schema, patient_id_column, ids, registry)
        for name in ["p1", "p2"]
    ]
    event_tables = [
        build_table(name, schema, patient_id_column, ids, registry)
        for name in ["e1", "e2"]
    ]
    return patient_id_column, patient_tables, event_tables


def build_table(name, schema_, patient_id_column_, ids, registry):
    columns = [
        sqlalchemy.Column("Id", sqlalchemy.Integer, primary_key=True, default=ids),
        sqlalchemy.Column(patient_id_column_, sqlalchemy.Integer),
    ]
    for col_name, type_ in schema_.items():
        sqla_type = {int: sqlalchemy.Integer, bool: sqlalchemy.Boolean}[type_]
        columns.append(sqlalchemy.Column(col_name, sqla_type))

    table = sqlalchemy.Table(name, registry.metadata, *columns)
    class_ = type(name, (object,), dict(__tablename__=name))
    registry.map_imperatively(class_, table)

    return class_
