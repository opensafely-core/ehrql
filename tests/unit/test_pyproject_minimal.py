import toml


def test_pyproject_minimal_is_subset_of_pyproject():
    with open("pyproject.toml") as f:
        pyproject = toml.load(f)
    with open("pyproject.minimal.toml") as f:
        minimal = toml.load(f)

    # `pyproject.minimal.toml` doesn't need to contain everything `pyproject.toml`
    # contains, but whatever it does contain should agree with `pyproject.toml`
    assert minimal.keys() == {"project"}
    for key, value in minimal["project"].items():
        assert value == pyproject["project"][key]
