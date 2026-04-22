"""Prompt eval: memory consolidation prompt contract."""

import inspect

import pytest


@pytest.mark.unit
class TestMemoryConsolidationPromptContract:
    """Guard rails for the abstractive memory consolidation surface."""

    def test_config_accepts_temperature(self) -> None:
        """Consolidation must expose a ``temperature`` knob on its config."""
        from synthorg.memory.consolidation import abstractive

        source = inspect.getsource(abstractive)
        assert "temperature" in source, (
            "abstractive consolidation must expose a temperature parameter"
        )
