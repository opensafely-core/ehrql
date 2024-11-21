#!/usr/bin/env python
"""
Reads a Python file defining a set of quiz questions and write an empty quiz ready to be
filled with answers to stdout
"""

import argparse
import importlib.util
import textwrap
from pathlib import Path

from ehrql.utils.string_utils import strip_indent


def main(quiz_answer_file):
    quiz = load_module(quiz_answer_file)
    introduction = quiz.introduction
    imports = get_imports(quiz_answer_file)
    questions = "\n\n".join(get_question_text(q) for q in quiz.questions.get_all())
    contents = (
        f"{as_comment(introduction)}\n"
        f"\n"
        f"from {quiz_answer_file.stem} import questions\n"
        f"\n"
        f"{imports}\n"
        f"\n"
        f"\n"
        f"{questions}\n"
        f"\n"
        f"questions.summarise()"
    )
    print(contents)


def load_module(module_path):
    # Taken from the official recipe for importing a module from a file path:
    # https://docs.python.org/3.9/library/importlib.html#importing-a-source-file-directly
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_imports(module_path):
    imports = []
    for line in module_path.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        # Skip imports related to the quiz mechanics itself
        if "ehrql.quiz" in line:
            continue
        # We take the line defining the introduction as marking the end of the imports
        if "introduction" in line:
            break
        imports.append(line)
    return "\n".join(imports)


def get_question_text(question):
    return "\n".join(
        [
            f"# Question {question.index}",
            as_comment(question.prompt),
            f"questions[{question.index}].check(...)",
        ]
    )


def as_comment(text):
    return textwrap.indent(strip_indent(text), "# ")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("quiz_answer_file", type=Path)
    kwargs = vars(parser.parse_args())
    main(**kwargs)
