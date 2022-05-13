import json

from . import generate_docs

if __name__ == "__main__":
    print(json.dumps(generate_docs(), indent=2))
