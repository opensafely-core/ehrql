import operator

from .backends import build_backends
from .contracts import build_contracts
from .specs import build_specs


def generate_docs():
    return {
        "backends": sorted(build_backends(), key=operator.itemgetter("name")),
        "contracts": sorted(build_contracts(), key=operator.itemgetter("dotted_path")),
        "specs": build_specs(),
    }
