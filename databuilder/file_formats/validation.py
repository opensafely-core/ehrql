class ValidationError(Exception):
    pass


def validate_columns(columns, required_columns):
    missing = [c for c in required_columns if c not in columns]
    if missing:
        raise ValidationError(f"Missing columns: {', '.join(missing)}")
