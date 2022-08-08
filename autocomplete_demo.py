from __future__ import annotations

from typing import Any, Generic, TypeVar, overload

T = TypeVar("T")


# QUERY LANGAUGE SKELETON
#


class BaseFrame:
    def count_for_patient(self) -> IntPatientSeries:
        ...


class EventFrame(BaseFrame):
    def take(self: T, condition: Any) -> T:
        ...


class PatientFrame(BaseFrame):
    def patient_frame_thing(self):
        ...


class BaseSeries:
    def series_thing(self: T) -> T:
        ...


class EventSeries(BaseSeries):
    def event_series_thing(self: T) -> T:
        ...


class PatientSeries(BaseSeries):
    def patient_series_thing(self: T) -> T:
        ...


class IntFunctions:
    def int_series_thing(self: T) -> T:
        ...


class StrFunctions:
    def str_series_thing(self: T) -> T:
        ...


class IntEventSeries(IntFunctions, EventSeries):
    ...


class IntPatientSeries(IntFunctions, PatientSeries):
    ...


class StrEventSeries(StrFunctions, EventSeries):
    ...


class StrPatientSeries(StrFunctions, PatientSeries):
    ...


def construct(cls: type[T]) -> T:
    return cls()


class Series(Generic[T]):
    def __init__(self, t: type[T]) -> None:
        self.t = t

    @overload
    def __get__(
        self: Series[int], instance: PatientFrame, cls: Any
    ) -> IntPatientSeries:
        ...

    @overload
    def __get__(
        self: Series[str], instance: PatientFrame, cls: Any
    ) -> StrPatientSeries:
        ...

    @overload
    def __get__(self: Series[int], instance: EventFrame, cls: Any) -> IntEventSeries:
        ...

    @overload
    def __get__(self: Series[str], instance: EventFrame, cls: Any) -> StrEventSeries:
        ...

    def __get__(self, instance: Any, cls: Any) -> BaseSeries:
        return NotImplemented()


# SCHEMA
#


@construct
class patients(PatientFrame):
    some_int = Series(int)
    some_str = Series(str)


@construct
class events(EventFrame):
    some_int = Series(int)
    some_str = Series(str)


# DATASET DEFINITION
#

# Try typing `events.` and `patients.` ...
