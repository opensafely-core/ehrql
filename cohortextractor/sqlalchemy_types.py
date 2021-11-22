import sqlalchemy.types


TYPES_BY_NAME = {
    "boolean": sqlalchemy.types.Boolean,
    "date": sqlalchemy.types.Date,
    "datetime": sqlalchemy.types.DateTime,
    "float": sqlalchemy.types.Float,
    "integer": sqlalchemy.types.Integer,
    "varchar": sqlalchemy.types.Text,
    "code": sqlalchemy.types.Text,
}
