class CohortRegistry:
    def __init__(self):
        self.cohorts = set()

    def add(self, cohort):
        self.cohorts.add(cohort)

    def reset(self):
        self.cohorts = set()


cohort_registry = CohortRegistry()
