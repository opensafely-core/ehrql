from tests.lib.mock_backend import MockBackend


def test_backend_tables():
    """Test that a backend registers its table names"""

    assert set(MockBackend.tables) == {
        "patients",
        "practice_registrations",
        "clinical_events",
        "positive_tests",
    }
