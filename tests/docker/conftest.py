from pathlib import Path

import pytest


@pytest.fixture
def run_in_container(tmpdir, containers):
    workspace = Path(tmpdir.mkdir("workspace"))

    def run(command):
        output = containers.run_fg(
            image="databuilder:latest",
            command=command,
            volumes={workspace: {"bind": "/workspace", "mode": "rw"}},
        )

        return {
            "container_response": output,
            "workspace_dir": workspace,
        }

    return run
