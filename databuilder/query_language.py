import dataclasses

from . import query_model as qm


class Dataset:
    def set_population(self, population):
        # TODO raise proper error here
        assert isinstance(population, BoolSeries)
        object.__setattr__(self, "population", population)

    def use_unrestricted_population(self):  # pragma: no cover
        self.set_population(BoolSeries(qm.Value(True)))

    def __setattr__(self, name, value):
        # TODO raise proper errors here
        assert name != "population"
        assert qm.has_one_row_per_patient(value.qm_node)
        super().__setattr__(name, value)


def compile(dataset):  # noqa A003
    return {k: v.qm_node for k, v in vars(dataset).items() if isinstance(v, Series)}


@dataclasses.dataclass(frozen=True)
class Series:
    qm_node: qm.Node

    def __eq__(self, other):
        return BoolSeries(self._make_binary_fn(other, qm.Function.EQ))

    def __ne__(self, other):
        return BoolSeries(self._make_binary_fn(other, qm.Function.NE))

    def is_null(self):
        return BoolSeries(qm.Function.IsNull(self.qm_node))

    def _make_binary_fn(self, other, fn):
        other_qm_node = other.qm_node if isinstance(other, Series) else qm.Value(other)
        return fn(lhs=self.qm_node, rhs=other_qm_node)


class IdSeries(Series):
    pass


class BoolSeries(Series):
    def __invert__(self):
        return BoolSeries(qm.Function.Not(self.qm_node))

    def __and__(self, other):
        return BoolSeries(self._make_binary_fn(other, qm.Function.And))

    def __or__(self, other):
        return BoolSeries(self._make_binary_fn(other, qm.Function.Or))


class IntSeries(Series):
    def __neg__(self):
        return IntSeries(qm.Function.Negate(self.qm_node))

    def __add__(self, other):
        return IntSeries(self._make_binary_fn(other, qm.Function.Add))

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return IntSeries(self._make_binary_fn(other, qm.Function.Subtract))

    def __rsub__(self, other):
        return other + -self

    def __lt__(self, other):
        return BoolSeries(self._make_binary_fn(other, qm.Function.LT))

    def __le__(self, other):
        return BoolSeries(self._make_binary_fn(other, qm.Function.LE))

    def __ge__(self, other):
        return BoolSeries(self._make_binary_fn(other, qm.Function.GE))

    def __gt__(self, other):
        return BoolSeries(self._make_binary_fn(other, qm.Function.GT))

    def sum_for_patient(self):
        return IntSeries(qm.AggregateByPatient.Sum(self.qm_node))


class DateSeries(Series):
    @property
    def year(self):
        return IntSeries(qm.Function.YearFromDate(source=self.qm_node))

    def __rsub__(self, other: str):
        return None


class StrSeries(Series):
    pass


class CodeSeries(Series):
    pass


class FloatSeries(Series):
    pass


class Frame:
    def __init__(self, qm_node, name_to_series_cls):
        self.qm_node = qm_node
        self.name_to_series_cls = name_to_series_cls

    def __getattr__(self, name):
        cls = self.name_to_series_cls[name]
        return cls(qm.SelectColumn(source=self.qm_node, name=name))


class PatientFrame(Frame):
    pass


class EventFrame(Frame):
    def exists_for_patient(self):
        return BoolSeries(qm.AggregateByPatient.Exists(source=self.qm_node))

    def count_for_patient(self):
        return IntSeries(qm.AggregateByPatient.Count(source=self.qm_node))

    def take(self, series):
        return EventFrame(
            qm.Filter(
                source=self.qm_node,
                condition=series.qm_node,
            ),
            self.name_to_series_cls,
        )

    def drop(self, series):
        return EventFrame(
            qm.Filter(
                source=self.qm_node,
                condition=qm.Function.Or(
                    lhs=qm.Function.Not(series.qm_node),
                    rhs=qm.Function.IsNull(series.qm_node),
                ),
            ),
            self.name_to_series_cls,
        )

    def sort_by(self, series):
        return SortedEventFrame(
            qm.Sort(
                source=self.qm_node,
                sort_by=series.qm_node,
            ),
            self.name_to_series_cls,
        )


class SortedEventFrame(Frame):
    def first_for_patient(self):
        return PatientFrame(
            qm.PickOneRowPerPatient(
                position=qm.Position.FIRST,
                source=self.qm_node,
            ),
            self.name_to_series_cls,
        )

    def last_for_patient(self):
        return PatientFrame(
            qm.PickOneRowPerPatient(
                position=qm.Position.LAST,
                source=self.qm_node,
            ),
            self.name_to_series_cls,
        )


def build_patient_table(name, name_to_series_cls, contract=None):
    qm_node = qm.SelectPatientTable(name)
    table = PatientFrame(qm_node, name_to_series_cls)
    if contract is not None:
        contract.validate_table(table)
    return table


def build_event_table(name, name_to_series_cls, contract=None):
    qm_node = qm.SelectTable(name)
    table = EventFrame(qm_node, name_to_series_cls)
    if contract is not None:  # pragma: no cover
        contract.validate_table(table)
    return table
