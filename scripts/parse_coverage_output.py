import itertools
import sys


def is_line_break(line):
    return {token for token in line} == {"-"}


def main():
    if len(sys.argv) < 2:
        print("Pass a the text file to be parsed as an argument", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1]) as f:
        lines = f.readlines()

    # make future parsing easier
    # lstrip() because GHA prints all lines with two leading spaces
    # rstrip("\n") because readlines includes newlines
    lines = list(line.lstrip().rstrip("\n") for line in lines)

    # dropwhile processes the given iterator until its predicate becomes false,
    # so here we are saying "ignore lines until the first line break"
    lines = itertools.dropwhile(lambda l: not is_line_break(l), lines)

    # remove the line break line itself
    next(lines)

    # iterate the remaining lines until we find the next line break
    lines = list(itertools.takewhile(lambda l: not is_line_break(l), lines))

    print("\n".join(lines))


if __name__ == "__main__":
    main()
