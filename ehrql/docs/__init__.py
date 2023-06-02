import shutil

from .backends import build_backends
from .render_includes.backends import render_backends
from .render_includes.schemas import render_schema, render_schema_index
from .render_includes.specs import render_specs
from .schemas import build_schemas
from .specs import build_specs


def generate_docs():
    backends = list(build_backends())
    schemas = list(build_schemas(backends))
    return {
        "backends": backends,
        "schemas": schemas,
        "specs": build_specs(),
    }


def render(docs_data, output_dir):
    output_dir.mkdir(exist_ok=True, parents=True)

    with open(output_dir / "backends.md", "w") as outfile:
        outfile.write(fix_whitespace(render_backends(docs_data["backends"])))

    with open(output_dir / "schemas.md", "w") as outfile:
        outfile.write(fix_whitespace(render_schema_index(docs_data["schemas"])))

    schema_dir = output_dir / "schemas"
    shutil.rmtree(schema_dir, ignore_errors=True)
    schema_dir.mkdir()
    for schema_data in docs_data["schemas"]:
        with open(schema_dir / f"{schema_data['name']}.md", "w") as outfile:
            outfile.write(fix_whitespace(render_schema(schema_data)))

    with open(output_dir / "specs.md", "w") as outfile:
        outfile.write(fix_whitespace(render_specs(docs_data["specs"])))


def fix_whitespace(s):
    # Our pre-commit hook doesn't like trailing whitespace but insists on a terminating
    # newline at the end of the file
    return s.rstrip() + "\n"
