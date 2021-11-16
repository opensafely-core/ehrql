from ..lib.mock_backend import MockBackend


def test_backend_tables():
    """Test that a backend registers its table names"""
    assert MockBackend.tables == {
        "practice_registrations",
        "clinical_events",
        "patients",
        "positive_tests",
    }
