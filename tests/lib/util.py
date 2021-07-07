import os


def get_mode(name, values, default):
    key = f"{name}_MODE"
    mode = os.environ.get(key, default)
    if mode not in values:
        raise ValueError(
            f"Unknown {key} {mode}. Possible values are {','.join(values)}."
        )
    return mode
