import datetime
import functools
import json
import pathlib

from ehrql.codes import BaseCode
from ehrql.file_formats.base import BaseDatasetReader
from ehrql.measures.measures import Measure
from ehrql.query_language import DummyDataConfig
from ehrql.query_model.column_specs import ColumnSpec
from ehrql.query_model.nodes import Node, Position, Value
from ehrql.query_model.table_schema import BaseConstraint, Column, TableSchema
from ehrql.utils.module_utils import get_subclasses


TYPE_REGISTRY = {
    t.__qualname__: t
    for t in [
        bool,
        int,
        float,
        str,
        datetime.date,
        tuple,
        dict,
        frozenset,
        Position,
        TableSchema,
        Column,
        pathlib.Path,
        ColumnSpec,
        DummyDataConfig,
        Measure,
        *get_subclasses(Node),
        *get_subclasses(BaseCode),
        *get_subclasses(BaseConstraint),
        *get_subclasses(BaseDatasetReader),
    ]
}


def serialize(value):
    return json.dumps(Marshaller.to_dict(value), indent=2)


def deserialize(data):
    return Unmarshaller.from_dict(json.loads(data))


class Marshaller:
    @classmethod
    def to_dict(cls, value):
        marshaller = cls()
        return {
            "value": marshaller.marshal(value),
            **marshaller.get_refs(),
        }

    def __init__(self):
        self.refs = {}
        self.next_ref_id = (f"#{i}" for i in range(1, 2**32)).__next__

    def get_refs(self):
        return dict(reversed(self.refs.values()))

    @functools.singledispatchmethod
    def marshal(self, obj):
        assert False, f"Unsupported type '{type(obj)}': {obj!r}"

    @marshal.register(type(None))
    @marshal.register(bool)
    @marshal.register(str)
    @marshal.register(int)
    @marshal.register(float)
    def marshal_primitive(self, obj):
        return obj

    @marshal.register(datetime.date)
    def marshal_date(self, obj):
        return {"date": obj.isoformat()}

    @marshal.register(list)
    def marshal_list(self, obj):
        return [self.marshal(value) for value in obj]

    @marshal.register(tuple)
    @marshal.register(frozenset)
    def marshal_iterable(self, obj):
        return {obj.__class__.__qualname__: [self.marshal(value) for value in obj]}

    @marshal.register(dict)
    def marshal_dict(self, obj):
        return {
            "dict": [
                [self.marshal(key), self.marshal(value)] for key, value in obj.items()
            ],
        }

    @marshal.register(type)
    def marshal_type(self, obj):
        return {"type": obj.__qualname__}

    @marshal.register(pathlib.Path)
    def marshal_path(self, obj):
        return {"Path": self.marshal(str(obj))}

    @marshal.register(Position)
    @marshal.register(Value)
    @marshal.register(BaseCode)
    def marshal_value(self, obj):
        return {obj.__class__.__qualname__: self.marshal(obj.value)}

    @marshal.register(Column)
    @marshal.register(BaseConstraint)
    @marshal.register(BaseDatasetReader)
    @marshal.register(ColumnSpec)
    @marshal.register(DummyDataConfig)
    @marshal.register(Measure)
    def marshal_object(self, obj):
        return {
            obj.__class__.__qualname__: {
                key: self.marshal(value)
                for key, value in obj.__dict__.items()
                if not key.startswith("_")
            },
        }

    @marshal.register(TableSchema)
    def marshal_tableschema(self, obj):
        return {
            obj.__class__.__qualname__: {
                key: self.marshal(value) for key, value in obj.schema.items()
            }
        }

    @marshal.register(Node)
    def marshal_as_ref(self, obj):
        if obj in self.refs:
            ref_id = self.refs[obj][0]
        else:
            ref_id = self.next_ref_id()
            marshalled = self.marshal_object(obj)
            self.refs[obj] = (ref_id, marshalled)
        return {"ref": ref_id}


class Unmarshaller:
    @classmethod
    def from_dict(cls, refs):
        unmarshaller = cls(refs)
        return unmarshaller.unmarshal(refs["value"])

    def __init__(self, refs):
        self.refs = refs
        self.ref_cache = {}

    @functools.singledispatchmethod
    def unmarshal(self, obj):
        assert False, f"Unsupported type '{type(obj)}': {obj!r}"

    @unmarshal.register(type(None))
    @unmarshal.register(bool)
    @unmarshal.register(str)
    @unmarshal.register(int)
    @unmarshal.register(float)
    def unmarshal_primitive(self, obj):
        return obj

    @unmarshal.register(list)
    def unmarshal_list(self, obj):
        return [self.unmarshal(value) for value in obj]

    @unmarshal.register(dict)
    def unmarshal_object_from_dict(self, obj):
        assert len(obj) == 1
        type_name, value = next(iter(obj.items()))
        if type_name == "type":
            return self.unmarshal_type(value)
        elif type_name == "ref":
            return self.unmarshal_ref(value)
        else:
            type_ = TYPE_REGISTRY[type_name]
            dispatch_target = self.unmarshal_object.dispatch(type_)
            return dispatch_target(self, type_, value)

    @functools.singledispatch
    def unmarshal_object(self, type_, value):
        assert False, f"Unsupported type '{type_}'"

    @unmarshal_object.register(datetime.date)
    def unmarshal_date(self, _, date_str):
        return datetime.date.fromisoformat(date_str)

    @unmarshal_object.register(dict)
    def unmarshal_dict(self, _, items):
        return dict(
            ((self.unmarshal(key), self.unmarshal(value)) for key, value in items)
        )

    @unmarshal_object.register(tuple)
    @unmarshal_object.register(frozenset)
    def unmarshal_iterable(self, type_, items):
        return type_(self.unmarshal(value) for value in items)

    def unmarshal_ref(self, ref_id):
        if ref_id not in self.ref_cache:
            self.ref_cache[ref_id] = self.unmarshal(self.refs[ref_id])
        return self.ref_cache[ref_id]

    def unmarshal_type(self, type_name):
        return TYPE_REGISTRY[type_name]

    @unmarshal_object.register(Node)
    @unmarshal_object.register(TableSchema)
    @unmarshal_object.register(Column)
    @unmarshal_object.register(BaseConstraint)
    @unmarshal_object.register(ColumnSpec)
    @unmarshal_object.register(BaseDatasetReader)
    @unmarshal_object.register(DummyDataConfig)
    @unmarshal_object.register(Measure)
    def unmarshal_named_object(self, type_, value):
        attrs = {key: self.unmarshal(v) for key, v in value.items()}
        return type_(**attrs)

    @unmarshal_object.register(Position)
    @unmarshal_object.register(Value)
    @unmarshal_object.register(BaseCode)
    @unmarshal_object.register(pathlib.Path)
    def unmarshal_value(self, type_, value):
        return type_(self.unmarshal(value))
