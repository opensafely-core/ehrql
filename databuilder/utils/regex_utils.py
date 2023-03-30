import re._parser as parser
from abc import ABC, abstractmethod
from dataclasses import dataclass


class RegexError(Exception):
    pass


def create_regex_generator(regex_str):
    """
    Accepts a regular expression string and returns a callable for generating random
    strings matching that expression.

    The callable itself takes an instance of `random.Random` so that the caller can
    control the random generation.
    """
    parsed = parser.parse(regex_str)
    return pattern_from_list(parsed).generate


def validate_regex(regex_str):
    try:
        create_regex_generator(regex_str)
    except parser.error as exc:
        raise RegexError(exc)
    return True


# MODELS
#
# Classes which represent elements of a regular expression and generate strings matching
# that element
#


class RegexElement(ABC):
    @abstractmethod
    def generate(self, rnd):
        raise NotImplementedError()


@dataclass(frozen=True)
class Literal(RegexElement):
    char: str

    def generate(self, rnd):
        return self.char


@dataclass(frozen=True)
class Pattern(RegexElement):
    elements: tuple[RegexElement]

    def generate(self, rnd):
        return "".join(elem.generate(rnd) for elem in self.elements)


@dataclass(frozen=True)
class Branch(RegexElement):
    branches: tuple[RegexElement]

    def generate(self, rnd):
        branch = rnd.choice(self.branches)
        return branch.generate(rnd)


@dataclass(frozen=True)
class Repeat(RegexElement):
    element: RegexElement
    min_repeats: int
    max_repeats: int

    def generate(self, rnd):
        repeats = rnd.randint(self.min_repeats, self.max_repeats)
        return "".join(self.element.generate(rnd) for _ in range(repeats))


@dataclass(frozen=True)
class Range(RegexElement):
    min_char_index: int
    max_char_index: int

    def generate(self, rnd):
        char_index = rnd.randint(self.min_char_index, self.max_char_index)
        return chr(char_index)


# TRANSFORM
#
# Functions to turn a parsed regular expression into a collection of models
#


# We don't attempt to support the full range of regular expressions available in Python
UNSUPPORTED_REGEX = RegexError("Regex uses unsupported features")


def create_regex_element(type_, args):
    handler = DISPATCH_TABLE.get(type_)
    if handler is None:
        raise UNSUPPORTED_REGEX
    return handler(args)


def handle_literal(char_index):
    return Literal(chr(char_index))


def pattern_from_list(items):
    return Pattern(
        tuple(create_regex_element(type_, args) for type_, args in items),
    )


def handle_subpattern(args):
    group_num, add_flags, del_flags, items = args
    # We don't care about the group number of this subpattern, and we can't handle flags
    # being set/unset within the subpattern
    if add_flags != 0 or del_flags != 0:
        raise UNSUPPORTED_REGEX
    return pattern_from_list(items)


def handle_branch(args):
    dummy, branches = args
    # As far as I call from the parser source code this argument no longer serves a
    # purpose and is always null
    assert dummy is None
    return Branch(tuple(pattern_from_list(i) for i in branches))


def handle_in(options):
    return Branch(
        tuple(create_regex_element(type_, args) for type_, args in options),
    )


def handle_max_repeat(args):
    min_repeats, max_repeats, pattern_args = args
    # Cap unlimited repetitions (e.g. "a*") at 10
    if max_repeats == parser.MAXREPEAT:
        max_repeats = 10
    return Repeat(
        pattern_from_list(pattern_args),
        min_repeats,
        max_repeats,
    )


def handle_range(args):
    return Range(min_char_index=args[0], max_char_index=args[1])


DISPATCH_TABLE = {
    parser.LITERAL: handle_literal,
    parser.SUBPATTERN: handle_subpattern,
    parser.BRANCH: handle_branch,
    parser.IN: handle_in,
    parser.MAX_REPEAT: handle_max_repeat,
    parser.RANGE: handle_range,
}
