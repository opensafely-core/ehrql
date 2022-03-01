class DatasetRegistry:  # pragma: no cover (re-implement when the QL is in)
    def __init__(self):
        self.datasets = set()

    def add(self, dataset):
        self.datasets.add(dataset)

    def reset(self):
        self.datasets = set()


dataset_registry = DatasetRegistry()
