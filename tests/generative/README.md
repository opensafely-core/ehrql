# Generative Tests Overview

The generative (property-based) tests use Hypothesis to generate query model variable definitions.

There are detailed docstrings in the code, and a description of how to run the tests in the
[developer docs](../../DEVELOPERS.md#generative-tests). This document is an attempt to
provide an overview and introduction to what the tests are doing.

There is one main test, `test_query_model` in [test_query_model.py](test_query_model.py). This
generates a variable definition, executes it using the MSSQL, SQLite and in-memory query engines,
and checks that the results are the same.

Note that because the inputs are automatically generated, we can't test that the results are
*correct*, but we rely on other (unit, integration, acceptance) tests to check the exact outputs
produced by the query engines, and we assume that the engines are sufficiently different in
implementation that it is a sufficient test to check that they always produce the same results
from the same inputs.

## Background

The most difficult part of the generative tests is teaching Hypothesis how to construct queries
out of query model objects. The query model has various constraints or validation rules which tell
you, given a particular object, what sort of operations you can apply to it and what other kinds of
object you can combine it with.

One way of trying to produce valid queries is just to generate lots of different objects, try sticking
them together and reject any structures that are invalid. This is what we did at first. It has the benefit
of being simple, but as the number of different types in the query model grows it becomes harder and harder
to randomly generate valid examples and eventually it stops working altogether.

The approach we take now involves, effectively, applying the query model validation rules backwards. We start
by deciding on the sort of object we want to end up with e.g. a Series of one-row-per-patient integers. Then
we ask, given we've got this object, what sorts of operation could validly produce an object like that? We
then get Hypothesis to pick one. That operation in turn requires other inputs and so, again, we ask what
sorts of operation could validly produce it and get Hypothesis to pick one. This process repeats until we
reach a "terminal node" i.e. an operation which doesn't require any inputs. (And if Hypothesis doesn't
naturally give us a terminal node after reaching a certain depth, we force it to choose one.)

This is very efficient at generating large and complex queries for testing. But applying the validation rules
backwards is fundamentally quite a mind-stretching exercise so don't be surprised if it takes a little while
for everything to fall into place.

## Terminology

We are used to thinking about query model things such as `Series` as representing a concrete column
in a table. The generative tests require a mental shift from thinking in terms of concrete objects to
thinking in terms of  `strategies` - i.e. a `value` strategy is a recipe for generating a `Value`,
rather than a `Value` itself.

### Building strategies

Strategies for query model nodes are built in hypothesis by using
[`hypothesis.strategies.builds`](https://hypothesis.readthedocs.io/en/latest/data.html#hypothesis.strategies.builds)
or the [`hypothesis.strategies.composite`](https://hypothesis.readthedocs.io/en/latest/data.html#composite-strategies)
decorator.

Calling `builds` with a callable and strategies for the callable's arguments
creates a new strategy that works by drawing the arguments and then
passing them to the callable
e.g. if we have defined strategies for choosing integers and strings, we can create a query model
`Value` strategy with:

```
from hypothesis import strategies as st

integer_strategy = st.integers(min_value=0, max_value=10)
str_strategy = st.text(alphabet=["a", "b", "c"], min_size=0, max_size=3)
value = st.builds(Value, value=st.one_of(integer_strategy, str_strategy))
```

`value` here is still a *strategy*, not a concrete thing.

```
>>> value
builds(Value, value=one_of(integers(min_value=0, max_value=10), text(alphabet=['a', 'b', 'c'], max_size=3)))
```

We can get an actual example by calling `example()` on a strategy:
```
>>> value.example()
Value(value='ca')
```

(The `example()` method is intended to be used for exploration only, and not in tests or strategy
definitions. Hypothesis will complain if you try to do that.)

If we need to reason about the examples being drawn, we can use the `composite` decorator. This gives us a magic `draw` argument that we can use to get examples out of a component strategy:

```
@st.composite
def value(draw, integer_strategy, str_strategy):
    raw_value = draw(st.one_of(integer_strategy, str_strategy))
    if isinstance(raw_value, str):
        # do something
        ...
    return Value(value=raw_value)
```

Note that the function we've written here creates one example `Value`, which we're calling in
the normal way, with a concrete `value` keyword argument. The `composite` decorator works by
taking a function like this which returns *one* example, and converting it into function that
returns a *strategy* that produces such examples.

When we call `value()`, we get the function back:
```
>>> value(integer_strategy, str_strategy)
value(integer_strategy=integers(min_value=0, max_value=10), str_strategy=text(alphabet=['a', 'b', 'c'], max_size=3))
```

As it's a strategy, we can call example() on it to get an actual example:
```
>>> value_st = value(integer_strategy, str_strategy)
>>> value_st.example()
Value(value=5)
```

### Value vs Series

Note that in the query model, a `Value` is a type of `Series` which wraps a single static value
in a one-row-per-patient series which just has that value for every patient. The variable strategies
treat `Value` somewhat differently to other types of `Series`; the overall strategy for a `series`
selects from all possible query model nodes that return a `Series`, *except* `Value`. This is to
avoid generating a lot of examples that do not involve the database at all.

It's import to remember that when a strategy for a node uses input arguments that are
`series` and `value` strategies, those *both* represent `Series` nodes of different types.


## test_query_model

`test_query_model` is the main generative test, and takes a `variable` and `data`, both hypothesis
strategies.

```
@hyp.given(variable=variable_strategy, data=data_strategy)
@hyp.settings(**settings)
def test_query_model(query_engines, variable, data, recorder):
    recorder.record_inputs(variable, data)  # this is used to record and report on some helpful data about the tests
    run_test(query_engines, data, variable, recorder)
```

## data strategy

We define a simplified table schema that contains columns of various types. The [`data_setup`](data_setup.py) uses this schema to setup up a number of patient and event tables (2 of each), and
the [`data_strategy`](data_strategies.py) populates the tables with hypothesis-generated data
for each test.

## value strategies

The value strategies are strategies defining simple types; `int`, `bool`, `date`, `float` and `str`.

```
value_strategies = {
    int: st.integers(min_value=0, max_value=10),
    bool: st.booleans(),
    datetime.date: st.dates(
        min_value=datetime.date(2010, 1, 1), max_value=datetime.date(2020, 12, 31)
    ),
    float: st.floats(min_value=0.0, max_value=11.0, width=16, allow_infinity=False),
    str: st.text(alphabet=["a", "b", "c"], min_size=0, max_size=3),
}
```

The same value strategies are used for defining both data strategies and variable (query model)
strategies. Generally, we try to define these values with narrow enough ranges that they will
sometimes overlap, and we can test equality. e.g. if we are testing an addition operation that
takes 2 ints, we can be reasonably sure that `st.integers(min_value=0, max_value=10)` will
test addition of two ints that are the same at some point.

## variable strategies

The variable strategies are the most complex part of ehrQL's generative test strategies.

A variable is defined by calling `variable()` in [`variable_strategies.py`](variable_strategies.py),
with the tables, schema and value strategies as described above.

`variable` defines lots of inner functions, each of which returns a strategy for creating the
thing it is named for, not the thing itself.
For example, the `value` inner function returns a strategy for creating `Value` objects, and not a `Value` object itself.

A valid variable is a `Series`, chosen by selecting a type (one of the types in `value_strategies`) and a frame
that the variable must be consistent with (with one row per patient, because we require that any
variable on a dataset represents one row per patient). The variable returned will be a
series of the chosen type, consistent with the chosen frame.

```
def variable(patient_tables, event_tables, schema, value_strategies):
   ...

    @st.composite
    def valid_variable(draw):
        type_ = draw(any_type())
        frame = draw(one_row_per_patient_frame())
        return draw(series(type_, frame))

    return valid_variable()
```

Let's take a closer look at the elements of the `valid_variable`.

`type_` is a type, drawn using the `any_type()` strategy, that chooses one of the types used as the keys for `value_strategies`:
```
    def any_type():
        return st.sampled_from(list(value_strategies.keys()))
```

`frame` is a frame with one row per patient, drawn using the `one_row_per_patient_frame()`
strategy. That could be a simple patient table (picked from one of the two
`SelectPatientTable` nodes defined by our data strategies), or a `PickOneRowPerPatient`
node, which is the result of a number of sorting and filtering operations.

Each of the sort and filter operations are themselves defined by strategies which require a
series to sort/filter on, so a frame strategy can quickly become deeply nested. The nesting
can potentially become so deep that it exceeds Hypothesis' max allowed depth, resulting in the
generated example being discarded; to prevent this, various strategies check the depth, and if
it's gone too far, they return a strategy that will pick a "terminal" node; i.e. one that we know
won't recurse any more. In the case of a one-row-per-patient frame, that is a `SelectPatientTable`
node, which can only take one of the two patient tables.

```
    def one_row_per_patient_frame():
        if depth_exceeded():
            return select_patient_table()
        return st.one_of(select_patient_table(), pick_one_row_per_patient_frame())
```

### The `series` strategy

The `series` strategy is where things become particularly complex!

`series()` is a strategy for choosing another strategy. Specifically, it chooses a strategy
that will generate a particular type of `Series` node. Whenever a series is needed, we call `series()`
passing in the type of the series that we want to generate, and a frame that it should be consistent
with. The `series()` strategy does the job of finding all the available strategies, and choosing one.

>**NOTE**
>
>The `type_` and `frame` arguments to `series()` can be thought of as describing properties of the
>series we want to generate from the strategy. So when we pass in `int` as the `type_` and a patient
>frame, it means that we expect to generate an int-type series that has one row per patient. The way
>that series is generated (and whether it uses the `type_` and `frame` arguments itself) is determined
>by the specific strategy that `series()` chooses.


Within `series()`, we define `series_constraints`; this is a dict of all possible strategies for
operations that produce a series. The keys are strategy callables. The values are 2-tuples representing the possible return types of the series that will be generated by that strategy,
and the possible domains of the frame it can be drawn from.

Frame domains indicate whether a particular `Series` node needs to be drawn from a patient table (i.e.one-row-per-patient), a non-patient table, or either.

The `series()` strategy chooses from the possible operation strategies that meet the constraints of
the `type_` and `frame` passed into it.

### A simple example: count

For example, if we only had strategies for `exists` and `count`, and we call `series(int, patient_table)`,
where `patient_table` has been chosen via `one_row_per_patient_frame()`:
```
    def series(type_, frame):
        ...
        # define contraints for possible series strategies
        series_constraints = {
            exists: ({bool}, DomainConstraint.PATIENT),
            count: ({int}, DomainConstraint.PATIENT),
        }
        ...
        def constraints_match(s):
            ...

        # find possible series strategies that match constraints, and choose one
        possible_series = [s for s in series_types if constraints_match(s)]
        series_strategy = draw(st.sampled_from(possible_series))

        # draw a series from the chosen strategy
        return draw(series_strategy(type_, frame))

```
`exists` returns a bool series with one row per patient.

`count` returns an int series with one row per patient.

The `frame` we've passed in matches the domain constriants for both strategies (it's a
one-row-per-patient frame). However, `exists` produces a bool series, and we need a strategy
that produces an int series, so `count` is the only possible strategy that matches. `series()`
will draw from the `count` strategy.

Note that the `type_` and `frame` are always passed on as arguments to the selected series
strategy, so that all series operation strategies have the same function signature.
However, whether they are actually used depends on the individual strategy.

For individual series strategies, it's important to remember that the `type_` argument they
receive represents the type of the **resulting series**; it may be important for that particular
series node that we know what that resulting type is
(e.g. see the example of [`Add`](#a-more-complex-example-add) below).

Following through to the `count` strategy, called by our call to `series(int, frame)`:

```
    def count(_type, _frame):
        return st.builds(AggregateByPatient.Count, any_frame())
```

`count` is passed a type (int) from the `series()` strategy; this is the expected return
type of the series, but it's not required here; it's also not necessary to use the
one-row-per-patient frame we passed in. (By convention, the arguments are named with leading
underscores to indicate this).

`count` generates an `AggregateByPatient.Count` node which can drawn from either patient-level
or an event-level frame, so we let Hypothesis choose one to use as the input to
`AggregateByPatient.Count`. (Note that the `series` returned *from* `AggregateByPatient.Count`
will be a one-row-per-patient series, consistent with `frame`.)


### A more complex example: add

If we now assume we also have a stratgey for `add`, and we again call `series(int, frame)`,
where `frame` has been chosen via `one_row_per_patient_frame()`:
```
    def series(type_, frame):
        ...
        # define contraints for possible series strategies
        series_constraints = {
            exists: ({bool}, DomainConstraint.PATIENT),
            count: ({int}, DomainConstraint.PATIENT),
            add: ({int, float}, DomainConstraint.PATIENT))
        }
        ...
```
`add` returns either an int or a float series, with one row per patient.

This time, the `frame` we've passed in again matches the domain constriants for all strategies.
We need a strategy that produces an int series, so now `series` can select from the `count` and
`add` strategies. Let's assume it chooses `add`.

```
    def add(type_, frame):
        ...
```

`add` is passed a type (int) from the `series()` strategy; this is the **expected return
type** of the series. In the case of the `add` strategy, this IS important. An `add` strategy
produces an `Add` query model node, which takes two series as arguments, and returns another series.
It can return an int or a float, and the aruments can be either int or float, BUT they all must be
the same.

This is the definition of `Add` in [`query_model.nodes`](ehrql/query_model/nodes.py)
```
class Function:

    class Add(Series[Numeric]):
        lhs: Series[Numeric]
        rhs: Series[Numeric]
```

A numeric type `Series` can be float or int, but both arguments to `Add` must be of the same type,
and return another `Series` of that type. In other words, if the expected return type is an int, we
know that we need to build our `add` strategy with int inputs.

So, for each of the lhs and rhs of the `Add` operation, we need a Hypothesis strategy that
produces an int `Series`. We can do that with `series(type_, frame)`.

However, there's a bit more to consider here. As mentioned before, a `Value` is also a type of
`Series`. `Value`s represent constants, and in order to cover the case where the `rhs` or `lhs` is
a constant, we need our strategy to allow a `Value` to be chosen as well. In addition, we have a
`frame` passed to the `add` strategy, but the `lhs` and `rhs` arguments can be chosen from different
tables, so we need our strategy to allow for this too.

So, we have two arguments; we say that one of them MUST be an int series drawn from the provided frame. This ensures that we don't end up with operations on two `Value` series, which don't touch
the database.

For the second argument, this could be a series drawn from the same frame as the first series, or
from a different frame, OR it could be a value.

And finally, these arguments could be either the `lhs` or the `rhs` of the `Add` operation, so we
need the strategy to choose that too.

This logic is implemented in the `binary_operation_with_types()` helper method, which deals with the
many query model nodes operate on two inputs, a `lhs` and `rhs` `Series`.

### Adding a new variable strategy

Let's assume we want to add the `GT` node as a new variable strategy.

First, look at how the `GT` node is implemented:

```
class Function:
    class GT(Series[bool]):
        lhs: Series[Comparable]
        rhs: Series[Comparable]
```

A `GT` node takes two `Comparable` series as inputs, and returns a boolean series. A `Comparable`
series can be of any type except bool, but the `lhs` and `rhs` series must be of the same type.

We can add a new entry to the `series_constraints` dict in `series()`, defining the return type of
the series (bool), and the domain constraint.
A `GT` operation can return a series consistent with *either* a one-row-per-patient frame, or a many-rows-per-patient frame:

```
    def series(type_, frame):
        ...
        # define contraints for possible series strategies
        series_constraints = {
            exists: ({bool}, DomainConstraint.PATIENT),
            count: ({int}, DomainConstraint.PATIENT),
            gt: ({bool}, DomainContstraint.ANY),
        }
        ...
```

Next we define the `gt` strategy. We can use a helper function `any_comparable_type()` to draw a
suitable type. Note that the `_type` passed in to the `gt` function is the expected return type of the series (bool), and in this case it does not have an impact on the implementation of the `gt`
strategy.

This is a binary operation like many other nodes, so the implementation follows the same strategy as
described for the `add` strategy above.

```
    @st.composite
    def gt(draw, _type, frame):
        type_ = draw(any_comparable_type())
        return draw(binary_operation(type_, frame, Function.GT))
```
