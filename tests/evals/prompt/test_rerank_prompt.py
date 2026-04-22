"""Prompt eval: memory re-ranker temperature contract."""

import inspect

import pytest


@pytest.mark.unit
class TestRerankPromptContract:
    """Guard rails for the LLM memory re-ranker prompt surface."""

    def test_system_prompt_defined(self) -> None:
        """Re-ranker must declare a pinned system prompt constant."""
        from synthorg.memory.retrieval.reranking import llm_reranker

        source = inspect.getsource(llm_reranker)
        assert "_RERANK_SYSTEM_PROMPT" in source or "system_prompt" in source.lower(), (
            "llm_reranker must expose a named system prompt constant"
        )
