import datetime
import functools
import importlib
import json
import pathlib

from ehrql import serializer_registry
from ehrql.codes import BaseCode, BaseMultiCodeString
from ehrql.file_formats.base import BaseRowsReader
from ehrql.measures.measures import DisclosureControlConfig, Measure, MeasureCollection
from ehrql.query_language import DummyDataConfig
from ehrql.query_model.column_specs import ColumnSpec
from ehrql.query_model.nodes import (
    Node,
    Position,
    SelectPatientTable,
    SelectTable,
    Value,
)
from ehrql.query_model.table_schema import BaseConstraint, Column, TableSchema
from ehrql.utils.module_utils import get_all_subclasses


class SerializerError(Exception):
    pass


# Mapping of names to types for all types that we support serializing/deserializing
TYPE_REGISTRY = {
    type_.__qualname__: type_
    for type_ in [
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
        MeasureCollection,
        DisclosureControlConfig,
        *get_all_subclasses(Node),
        *get_all_subclasses(BaseCode),
        *get_all_subclasses(BaseMultiCodeString),
        *get_all_subclasses(BaseConstraint),
        *get_all_subclasses(BaseRowsReader),
    ]
}

TYPE_REGISTRY_INVERSE = {type_: name for name, type_ in TYPE_REGISTRY.items()}

# Ensure no name clashes
assert len(TYPE_REGISTRY) == len(TYPE_REGISTRY_INVERSE)


def type_name(obj):
    return TYPE_REGISTRY_INVERSE[type(obj)]


def serialize(value):
    return json.dumps(Marshaller.to_dict(value), indent=2)


def deserialize(data, *, root_dir):
    return Unmarshaller.from_dict(json.loads(data), root_dir=root_dir)


class Marshaller:
    """
    Convert arbitrary values to nested structures of JSON-supported values ready to be
    serialized
    """

    @classmethod
    def to_dict(cls, value):
        marshaller = cls()
        return {
            "value": marshaller.marshal(value),
            **marshaller.get_references(),
        }

    def __init__(self):
        self.references = {}
        # Sequence of unique IDs (strings not ints so they can be used as JSON keys)
        id_sequence = (str(i) for i in range(1, 2**32))  # pragma: no branch
        self.get_next_reference_id = id_sequence.__next__

    def get_references(self):
        return dict(self.references.values())

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
        return {type_name(obj): obj.isoformat()}

    @marshal.register(list)
    def marshal_list(self, obj):
        return [self.marshal(value) for value in obj]

    @marshal.register(tuple)
    @marshal.register(frozenset)
    def marshal_iterable(self, obj):
        return {type_name(obj): [self.marshal(value) for value in obj]}

    @marshal.register(dict)
    def marshal_dict(self, obj):
        return {
            type_name(obj): [
                [self.marshal(key), self.marshal(value)] for key, value in obj.items()
            ],
        }

    @marshal.register(type)
    def marshal_type(self, obj):
        # Sometimes we need to marshal refences to types rather than instances of those
        # types (e.g. `int` as opposed to 10). We don't need to support this for every
        # type in the registry, but there's no harm in supporting more types that we
        # need and it saves creating a separate registry.
        return {"type": TYPE_REGISTRY_INVERSE[obj]}

    @marshal.register(pathlib.Path)
    def marshal_path(self, obj):
        # Paths are unusual in that we always want to encode it as the platform-agnostic
        # alias `Path`, not as the specific subclass (e.g. `PosixPath`) it happens to be
        return {"Path": self.marshal(str(obj))}

    # We need special handling for enums like `Position` as the value attribute doesn't
    # appear inside `__dict__` as it does for other objects
    @marshal.register(Position)
    # `BaseCode` objects _can_ be marshalled like other objects, but we'd rather not
    # leak the implementation detail that their one attribute happens to be called
    # "value" so we marshal them as e.g.
    #
    #   {"SNOMEDCTCode": "123456"}
    #
    # rather than
    #
    #   {"SNOMEDCTCode": {"value": "123456"}}
    #
    @marshal.register(BaseCode)
    # Ditto for `Value` objects
    @marshal.register(Value)
    def marshal_value(self, obj):
        return {type_name(obj): self.marshal(obj.value)}

    @marshal.register(Column)
    @marshal.register(BaseConstraint)
    @marshal.register(BaseRowsReader)
    @marshal.register(ColumnSpec)
    @marshal.register(DummyDataConfig)
    @marshal.register(Measure)
    @marshal.register(MeasureCollection)
    @marshal.register(DisclosureControlConfig)
    def marshal_object(self, obj):
        return {
            type_name(obj): {
                key: self.marshal(value)
                for key, value in obj.__dict__.items()
                if not key.startswith("_")
            },
        }

    @marshal.register(TableSchema)
    def marshal_tableschema(self, obj):
        # TableSchema needs special treatment because its attributes don't map directly
        # to its constructor signature
        return {
            type_name(obj): {
                key: self.marshal(value) for key, value in obj.schema.items()
            }
        }

    @marshal.register(SelectTable)
    @marshal.register(SelectPatientTable)
    def marshal_external_reference(self, obj):
        # We don't serialize the contents of table nodes; instead we serialize a
        # reference to their definition. The primary benefit is that we can then trust
        # the definitions of the table nodes because they can't be modified by the user:
        # definitions can only come from code which is importable by the ehrQL process
        # and, by design, no user code is on the import path.
        #
        # This also means that we're free to add content to the table nodes (e.g. custom
        # dummy data methods) which can't be easily serialized.
        module, name = serializer_registry.get_id_for_object(obj)
        return {"external_ref": {"module": module, "name": name}}

    @marshal.register(Node)
    def marshal_as_reference(self, obj):
        # To avoid repeatedly re-serializing the same node each time it's referenced we
        # populate a dictionary of references, giving each node a unique ID.
        if obj in self.references:
            reference_id = self.references[obj][0]
        else:
            reference_id = self.get_next_reference_id()
            marshalled = self.marshal_object(obj)
            self.references[obj] = (reference_id, marshalled)
        return {"ref": reference_id}


class Unmarshaller:
    """
    Given a nested dictionary of JSON-supported values, convert these back into the
    appropriate Python types
    """

    @classmethod
    def from_dict(cls, references, *, root_dir):
        unmarshaller = cls(references, root_dir=root_dir)
        return unmarshaller.unmarshal(references["value"])

    def __init__(self, references, *, root_dir):
        self.references = references
        self.reference_cache = {}
        self.root_dir = root_dir.resolve()

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
    def unmarshal_dict(self, obj):
        assert len(obj) == 1
        type_name, value = next(iter(obj.items()))
        if type_name == "type":
            return self.unmarshal_type(value)
        elif type_name == "ref":
            return self.unmarshal_reference(value)
        elif type_name == "external_ref":
            return self.unmarshal_external_reference(**value)
        else:
            # This is an abuse of the singledispatch mechanism: we don't have an
            # instance of the appropriate type to dispatch on (that's the thing we're
            # trying to create) but we can look up the dispatch target for the type and
            # call it directly. This avoids us having to write all the type matching
            # code ourselves.
            type_ = TYPE_REGISTRY[type_name]
            dispatch_target = self.unmarshal_for.dispatch(type_)
            return dispatch_target(self, type_, value)

    def unmarshal_type(self, type_name):
        return TYPE_REGISTRY[type_name]

    def unmarshal_reference(self, reference_id):
        if reference_id not in self.reference_cache:
            self.reference_cache[reference_id] = self.unmarshal(
                self.references[reference_id]
            )
        return self.reference_cache[reference_id]

    def unmarshal_external_reference(self, *, module, name):
        # Where a node has been serialized as a reference to an externally defined
        # object we need to make sure we've imported the module in which it was defined
        # before we can dereference it.
        #
        # NOTE: This does mean that we're passing a user-supplied value to
        # `import_module`. Here is why I believe that is safe:
        #
        #  * `import_module` does its own sanity checks on the module name so you can't
        #     make it misbehave by passing "weird" values in.
        #
        #  * By design, no user controlled files are on `sys.path` so nothing is
        #    importable apart from ehrQL code, installed third-party modules and stdlib.
        #
        #  * The mechanism we are using does not allow referencing arbitrary objects
        #    from arbitrary modules: only objects explicitly registered with the ehrQL
        #    registry can be dereferenced.
        #
        #  * While it's possbile to trigger the import of any module on `sys.path`, if
        #    that module does not register any objects with the ehrQL registry then the
        #    `get_object_by_id()` call will immediately fail. This means that even if
        #    some third-party module has unanticipated import-time side-effects it would
        #    be very hard to exploit these in any way.
        #
        importlib.import_module(module)
        return serializer_registry.get_object_by_id((module, name))

    @functools.singledispatch
    def unmarshal_for(self, type_, value):
        assert False, f"Unsupported type '{type_}'"

    @unmarshal_for.register(datetime.date)
    def unmarshal_for_date(self, type_, date_str):
        return type_.fromisoformat(date_str)

    @unmarshal_for.register(dict)
    def unmarshal_for_dict(self, type_, items):
        return type_(
            ((self.unmarshal(key), self.unmarshal(value)) for key, value in items)
        )

    @unmarshal_for.register(tuple)
    @unmarshal_for.register(frozenset)
    def unmarshal_for_iterable(self, type_, items):
        return type_(self.unmarshal(value) for value in items)

    @unmarshal_for.register(Node)
    @unmarshal_for.register(TableSchema)
    @unmarshal_for.register(Column)
    @unmarshal_for.register(BaseConstraint)
    @unmarshal_for.register(ColumnSpec)
    @unmarshal_for.register(BaseRowsReader)
    @unmarshal_for.register(DummyDataConfig)
    @unmarshal_for.register(Measure)
    @unmarshal_for.register(MeasureCollection)
    @unmarshal_for.register(DisclosureControlConfig)
    def unmarshal_for_object(self, type_, value):
        attrs = {key: self.unmarshal(v) for key, v in value.items()}
        return type_(**attrs)

    @unmarshal_for.register(SelectTable)
    @unmarshal_for.register(SelectPatientTable)
    def unmarshal_for_prohibited(self, type_, value):
        # We want any table nodes in the resulting query graph to be trustworthy (i.e.
        # not user-supplied) so that any permission restrictions they impose can be
        # relied upon. This means that such nodes can only be serialized as "external
        # references" i.e. references to nodes defined outside of the user's query
        # graph.
        raise SerializerError(
            f"Objects of type {type_.__qualname__!r} cannot be constructed directly "
            f"but must be serialized as external references"
        )

    @unmarshal_for.register(pathlib.Path)
    def unmarshal_for_path(self, type_, value):
        path = type_(self.unmarshal(value))
        if not path.resolve().is_relative_to(self.root_dir):
            raise SerializerError(
                f"Path {str(path)!r} is not contained within the directory"
                f" {str(self.root_dir)!r}"
            )
        return path

    @unmarshal_for.register(Position)
    @unmarshal_for.register(BaseCode)
    @unmarshal_for.register(Value)
    def unmarshal_for_value(self, type_, value):
        return type_(self.unmarshal(value))
