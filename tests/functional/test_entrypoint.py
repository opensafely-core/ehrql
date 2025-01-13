import os.path
import subprocess
import sys


def test_entrypoint():
    # Include the Python executable directory on the path so that even if the virtualenv
    # isn't activated we can still find the `ehrql` executable.
    path = os.pathsep.join(
        [os.path.dirname(sys.executable), os.environ.get("PATH", "")]
    )

    result = subprocess.run(
        ["ehrql", "--help"],
        capture_output=True,
        text=True,
        check=True,
        env={"PATH": path},
    )
    assert "usage: ehrql [-h]" in result.stdout
