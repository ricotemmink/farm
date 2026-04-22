"""Prompt eval: safety classifier temperature contract."""

import inspect

import pytest


@pytest.mark.unit
class TestSafetyClassifierPromptContract:
    """Guard rails for the approval safety classifier prompt surface."""

    def test_temperature_is_zero(self) -> None:
        """Safety classifier must run at temperature=0 for a stable verdict."""
        from synthorg.security import safety_classifier

        source = inspect.getsource(safety_classifier)
        assert "temperature=0.0" in source, "safety_classifier must pin temperature=0.0"
