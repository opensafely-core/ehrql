import operator

from .backends import build_backends
from .contracts import build_contracts
from .schemas import build_schemas
from .specs import build_specs


def generate_docs():
    backends = list(build_backends())
    schemas = list(build_schemas(backends))
    return {
        "backends": sorted(backends, key=operator.itemgetter("name")),
        "schemas": sorted(schemas, key=operator.itemgetter("dotted_path")),
        "contracts": sorted(build_contracts(), key=operator.itemgetter("dotted_path")),
        "specs": build_specs(),
    }
