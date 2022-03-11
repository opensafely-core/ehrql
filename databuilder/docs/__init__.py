import operator

from .backends import build_backends
from .contracts import build_contracts


def generate_docs():
    return {
        "backends": sorted(build_backends(), key=operator.itemgetter("name")),
        "contracts": sorted(build_contracts(), key=operator.itemgetter("dotted_path")),
    }
