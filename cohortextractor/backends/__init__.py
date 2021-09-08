# All backends need to be imported here so they get registered
from .base import BACKENDS
from .graphnet import GraphnetBackend
from .tpp import TPPBackend


__all__ = ("BACKENDS", "TPPBackend", "GraphnetBackend")
