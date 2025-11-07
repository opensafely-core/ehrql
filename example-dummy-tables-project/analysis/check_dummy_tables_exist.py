import sys
from pathlib import Path


def main(outfile):
    found = Path("generated_tables").exists()
    Path(outfile).write_text(str(found))


if __name__ == "__main__":
    main(sys.argv[1])
