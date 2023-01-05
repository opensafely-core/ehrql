from datetime import date

import hypothesis as hyp
import hypothesis.strategies as st

# Data generation strategies are complicated by the need for patient ids in patient tables to
# be unique (see `patient_records()`).

patient_id_column = "patient_id"
max_patient_id = 10
max_num_patient_records = max_patient_id  # <= max_patient_id, hasn't been fine-tuned
max_num_event_records = max_patient_id  # could be anything, hasn't been fine-tuned


def record(
    class_, id_strategy, schema, int_values, bool_values, date_values, float_values
):
    # We don't construct the actual objects here because it's easier to extract stats for the generated data if we
    # pass around simple objects.
    columns = {patient_id_column: id_strategy}
    for name, type_ in schema.column_types:
        type_strategy = {
            int: int_values,
            bool: bool_values,
            date: date_values,
            float: float_values,
        }[type_]
        columns[name] = type_strategy

    return st.builds(dict, type=st.just(class_), **columns)


@st.composite
def concat(draw, *list_strategies):
    results = []
    for list_strategy in list_strategies:
        for example in draw(list_strategy):
            results.append(example)
    return results


patient_ids = st.integers(min_value=1, max_value=max_patient_id)


def event_records(class_, schema, int_values, bool_values, date_values, float_values):
    return st.lists(
        record(
            class_,
            patient_ids,
            schema,
            int_values,
            bool_values,
            date_values,
            float_values,
        ),
        min_size=0,
        max_size=max_num_event_records,
    )


@st.composite
def patient_records(
    draw, class_, schema, int_values, bool_values, date_values, float_values
):
    # This strategy ensures that the patient ids are unique. We need to maintain the state to ensure that uniqueness
    # inside the strategy itself so that we can ensure the tests are idempotent as Hypothesis requires. That means that
    # this strategy must be called once only for a given table in a given test.
    used_ids = []

    @st.composite
    def one_patient_record(draw_):
        id_ = draw_(patient_ids)
        hyp.assume(id_ not in used_ids)
        used_ids.append(id_)
        return draw(
            record(
                class_,
                st.just(id_),
                schema,
                int_values,
                bool_values,
                date_values,
                float_values,
            )
        )

    return draw(
        st.lists(one_patient_record(), min_size=0, max_size=max_num_patient_records)
    )


def data(
    patient_classes,
    event_classes,
    schema,
    int_values,
    bool_values,
    date_values,
    float_values,
):
    return concat(
        *[
            patient_records(
                c, schema, int_values, bool_values, date_values, float_values
            )
            for c in patient_classes
        ],
        *[
            event_records(c, schema, int_values, bool_values, date_values, float_values)
            for c in event_classes
        ]
    )
