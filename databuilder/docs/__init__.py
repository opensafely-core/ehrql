import json
import operator

from .backends import build_backends
from .contracts import build_contracts


def generate_docs(location=None):
    data = {
        "backends": sorted(build_backends(), key=operator.itemgetter("name")),
        "contracts": sorted(build_contracts(), key=operator.itemgetter("dotted_path")),
    }

    path = "public_docs.json"  # default to cwd
    if location is not None:
        path = location / path

    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print("Generated data for documentation")
