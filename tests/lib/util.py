import databuilder.main
from databuilder import table


def extract(dataset, backend, database, **backend_kwargs):
    return list(
        databuilder.main.extract(
            dataset, backend(database.host_url(), **backend_kwargs)
        )
    )


class RecordingReporter:
    def __init__(self):
        self.msg = ""

    def __call__(self, msg):
        self.msg = msg


def null_reporter(msg):
    pass


def iter_flatten(iterable, iter_classes=(list, tuple)):
    """
    Iterate over `iterable` recursively flattening any lists or tuples
    encountered
    """
    for item in iterable:
        if isinstance(item, iter_classes):
            yield from iter_flatten(item, iter_classes)
        else:
            yield item


class OldDatasetWithPopulation:
    def __init_subclass__(cls):
        cls.population = table("practice_registrations").exists()
