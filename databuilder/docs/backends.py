import operator

from ..backends.base import BaseBackend
from ..module_utils import get_sibling_subclasses


def build_backends():
    backends = get_sibling_subclasses(BaseBackend)
    backends.sort(key=operator.attrgetter("__name__"))

    for backend in backends:
        yield {
            "name": backend.__name__,
            # TODO: Re-establish a listing of the tables a given backend supports once
            # we decide exactly how this is going to work
            "contracts": [],
        }
