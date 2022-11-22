import operator

from databuilder.utils.module_utils import get_sibling_subclasses

from ..backends.base import BaseBackend


def build_backends():
    backends = get_sibling_subclasses(BaseBackend)
    backends.sort(key=operator.attrgetter("__name__"))

    for backend in backends:
        implements = [namespace.__name__ for namespace in backend.implements]
        yield {
            "name": backend.__name__,
            "implements": implements,
            # TODO: Backends no longer implement individual contracts but we leave this
            # empty list in place for now while we update the docs code which expects it
            "contracts": [],
        }
