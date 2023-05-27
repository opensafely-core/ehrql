import operator
import shutil

from .backends import build_backends
from .contracts import build_contracts
from .render_includes.backends import render_backends
from .render_includes.backends_old import render_backend_old
from .render_includes.contracts import render_contracts
from .render_includes.schemas import render_schema, render_schema_index
from .render_includes.specs import render_specs
from .schemas import build_schemas
from .specs import build_specs


def generate_docs():
    backends = list(build_backends())
    schemas = list(build_schemas(backends))
    return {
        "backends": sorted(backends, key=operator.itemgetter("name")),
        "schemas": sorted(schemas, key=operator.itemgetter("dotted_path")),
        "contracts": sorted(build_contracts(), key=operator.itemgetter("dotted_path")),
        "specs": build_specs(),
    }


def render(docs_data, output_dir):
    output_dir.mkdir(exist_ok=True, parents=True)
    with open(output_dir / "contracts.md", "w") as outfile:
        outfile.write(render_contracts(docs_data["contracts"]))

    with open(output_dir / "backends.md", "w") as outfile:
        outfile.write(render_backends(docs_data["backends"]))

    with open(output_dir / "schemas.md", "w") as outfile:
        outfile.write(render_schema_index(docs_data["schemas"]))

    schema_dir = output_dir / "schemas"
    shutil.rmtree(schema_dir, ignore_errors=True)
    schema_dir.mkdir()
    for schema_data in docs_data["schemas"]:
        with open(schema_dir / f"{schema_data['name']}.md", "w") as outfile:
            outfile.write(render_schema(schema_data))

    backends = docs_data["backends"]
    for backend_data in backends:
        name = backend_data["dotted_path"].rpartition(".")[2]
        with open(output_dir / f"{name}.md", "w") as outfile:
            outfile.write(render_backend_old(backend_data))

    with open(output_dir / "specs.md", "w") as outfile:
        outfile.write(render_specs(docs_data["specs"]))
