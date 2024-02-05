"""Statistical Disclosure Control (SDC)

For more information, see:
https://docs.opensafely.org/releasing-files/
"""

SUPPRESSION_THRESHOLD = 7
ROUNDING_MULTIPLE = 5


def apply_sdc(value):
    assert value >= 0
    assert isinstance(value, int)
    value = 0 if value <= SUPPRESSION_THRESHOLD else value
    value = int(ROUNDING_MULTIPLE * round(value / ROUNDING_MULTIPLE, ndigits=0))
    return value


def apply_sdc_to_measure_results(results):
    for result in results:
        (
            measure_name,
            interval_start,
            interval_end,
            _,
            old_numerator,
            old_denominator,
            *group_names,
        ) = result
        numerator = apply_sdc(old_numerator)
        denominator = apply_sdc(old_denominator)
        ratio = numerator / denominator if denominator else None
        yield (
            measure_name,
            interval_start,
            interval_end,
            ratio,
            numerator,
            denominator,
            *group_names,
        )
