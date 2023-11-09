import datetime

import sqlalchemy


TYPE_MAP = {
    bool: sqlalchemy.Boolean,
    datetime.date: sqlalchemy.Date,
    float: sqlalchemy.Float,
    int: sqlalchemy.Integer,
    str: sqlalchemy.String,
}


def type_from_python_type(type_):
    "Return the SQLAlchemy Type for a given Python type"
    if hasattr(type_, "_primitive_type"):
        lookup_type = type_._primitive_type()
    else:
        lookup_type = type_
    try:
        return TYPE_MAP[lookup_type]
    except KeyError:
        raise TypeError(f"Unsupported column type: {type_}")
