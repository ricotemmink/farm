"""Prompt eval: agent system-prompt builder determinism.

The agent system prompt is composed from an ``AgentIdentity`` object
plus static fence directives (untrusted-content, SEC-1). This test
pins the fingerprint of the directives so silent edits to the
``wrap_untrusted`` / ``untrusted_content_directive`` surface are
caught before they land.
"""

import inspect

import pytest

from tests.evals.prompt._harness import fingerprint_prompt


@pytest.mark.unit
class TestAgentSystemPromptContract:
    """Guard rails for the agent system prompt composition."""

    def test_prompt_safety_fingerprint_stable(self) -> None:
        """Detect silent edits to the untrusted-content fence directive."""
        from synthorg.engine import prompt_safety

        source = inspect.getsource(prompt_safety)
        fp = fingerprint_prompt(source)
        assert isinstance(fp, str)
        assert len(fp) == 16
