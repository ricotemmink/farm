"""Prompt eval: decomposer temperature contract."""

import inspect

import pytest


@pytest.mark.unit
class TestDecomposerPromptContract:
    """Guard rails for the LLM criteria decomposer prompt surface."""

    def test_temperature_is_zero(self) -> None:
        """Decomposer must run at temperature=0 for deterministic splits."""
        from synthorg.engine.quality.decomposers.llm import (
            LLMCriteriaDecomposer,
        )

        source = inspect.getsource(LLMCriteriaDecomposer)
        assert "temperature=0.0" in source, (
            "LLMCriteriaDecomposer must pin temperature=0.0"
        )
