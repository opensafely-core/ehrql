import json
from urllib.parse import quote


def parse_metadata(environ):
    """
    Parse metadata from the environment, to be included with generated queries
    Metadata is expected to be a dict of simple key: value string pairs
    """
    metadata_str = environ.get("EHRQL_METADATA") or "{}"
    metadata_dict = json.loads(metadata_str)
    assert all(isinstance(val, str) for val in metadata_dict.values()), (
        "metadata values must be strings"
    )
    return metadata_dict


def metadata_to_list(metadata_dict):
    """
    Turn a metadata dict into a flat list of "k=v" string pairs, with the key and
    value urlencoded so that they can contain arbitrary characters without needing
    to worry about breaking the formatting of whatever they get embedded in (Trino
    client tags, SQL comments).
    """
    return [f"{quote(k)}={quote(v)}" for k, v in metadata_dict.items()]
