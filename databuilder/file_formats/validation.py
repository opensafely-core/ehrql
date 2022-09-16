class ValidationError(Exception):
    pass


def validate_headers(headers, expected_headers):
    headers_set = set(headers)
    expected_set = set(expected_headers)
    if headers_set != expected_set:
        errors = []
        missing = expected_set - headers_set
        if missing:
            errors.append(f"Missing columns: {', '.join(missing)}")
        extra = headers_set - expected_set
        if extra:
            errors.append(f"Unexpected columns: {', '.join(extra)}")
        raise ValidationError("\n".join(errors))
    elif headers != expected_headers:
        # We could be more relaxed about things here, but I think it's worth insisting
        # that columns be in the same order. We've seen analysis code before which is
        # sensitive to column ordering.
        raise ValidationError(
            f"Headers not in expected order:\n"
            f"  expected: {', '.join(expected_headers)}\n"
            f"  found: {', '.join(headers)}"
        )
