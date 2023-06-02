import sys
from pathlib import Path

from . import generate_docs, render


if __name__ == "__main__":
    output_dir = sys.argv[1]
    render(generate_docs(), Path(output_dir))
