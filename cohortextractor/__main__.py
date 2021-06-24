from pathlib import Path


if __name__ == "__main__":
    path = Path("/workspace/outputs/some_file.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
