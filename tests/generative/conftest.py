from tests.generative.recording import show_input_summary

from .recording import recorder

__all__ = ["recorder"]


def pytest_terminal_summary(terminalreporter, exitstatus, config):  # pragma: no cover
    show_input_summary()
