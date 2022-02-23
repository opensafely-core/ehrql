def test_generate_dataset_in_container(run_in_container):
    output = run_in_container(
        [
            "generate_dataset",
            "--help",
        ]
    )

    assert output


def test_validate_dataset_definition_in_container(run_in_container):
    output = run_in_container(
        [
            "validate_dataset_definition",
            "--help",
        ]
    )

    assert output


def test_generate_measures_in_container(run_in_container):
    output = run_in_container(
        [
            "generate_measures",
            "--help",
        ]
    )

    assert output


def test_test_connection_in_container(run_in_container):
    output = run_in_container(
        [
            "test_connection",
            "--help",
        ]
    )

    assert output


def test_generate_docs_in_container(run_in_container):
    output = run_in_container(
        [
            "generate_docs",
            "--help",
        ]
    )

    assert output
