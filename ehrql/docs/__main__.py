import shutil
import sys
from pathlib import Path

from .backends import build_backends
from .cli import build_cli
from .language import build_language
from .render_includes.backends import render_backends
from .render_includes.cli import render_cli
from .render_includes.language import render_language_section
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
        "language": build_language(),
        "cli": build_cli(),
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

    with open(output_dir / "cli.md", "w") as outfile:
        outfile.write(fix_whitespace(render_cli(docs_data["cli"])))

    section_filenames = []
    for section_name, section in docs_data["language"].items():
        filename = f"language__{section_name}.md"
        section_filenames.append(filename)
        with open(output_dir / filename, "w") as outfile:
            outfile.write(fix_whitespace(render_language_section(section)))

    # Make sure each reference section we generate above is actually included in the
    # reference documentation
    reference_index = Path(__file__).parents[2] / "docs/reference/language.md"
    reference_index_text = reference_index.read_text()
    for filename in section_filenames:
        assert filename in reference_index_text, (
            f"{filename} not included by {reference_index}"
        )


def fix_whitespace(s):
    # Our pre-commit hook doesn't like trailing whitespace but insists on a terminating
    # newline at the end of the file
    return s.rstrip() + "\n"


if __name__ == "__main__":
    output_dir = sys.argv[1]
    render(generate_docs(), Path(output_dir))
