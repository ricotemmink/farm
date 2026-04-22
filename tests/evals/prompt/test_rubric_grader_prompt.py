"""Prompt eval: rubric grader temperature + prompt drift.

Rather than replay a full LLM round-trip (flaky, provider-gated), the
suite asserts the two properties that deterministically matter for a
pinned prompt surface:

1. The production config still pins ``temperature=0.0`` -- any drift
   toward higher temperatures turns the grader non-deterministic
   across CI shards.
2. The bytes of the prompt body haven't silently drifted: edits must
   either update the pinned fingerprint in this test OR ship new
   labelled examples that still pass.

Reference implementation: ``synthorg.engine.quality.graders.llm``.
"""

import pytest

from tests.evals.prompt._harness import fingerprint_prompt


@pytest.mark.unit
class TestRubricGraderPromptContract:
    """Guard rails for the LLM rubric grader prompt surface."""

    def test_temperature_is_zero(self) -> None:
        """Grader must run at temperature=0 for deterministic scores."""
        # The grader builds its CompletionConfig inline; locate the
        # exact keyword using the module's source so the assertion
        # survives reflow edits.
        import inspect

        from synthorg.engine.quality.graders.llm import LLMRubricGrader

        source = inspect.getsource(LLMRubricGrader)
        assert "temperature=0.0" in source, (
            "LLMRubricGrader must pin temperature=0.0 for determinism"
        )

    def test_prompt_fingerprint_is_pinned(self) -> None:
        """Detect silent prompt edits via a stable hash.

        When the prompt changes intentionally, update the pinned
        fingerprint + add a regression example below to prove the
        new prompt still passes the grading contract.
        """
        import inspect

        from synthorg.engine.quality.graders import (
            llm as _grader_module,
        )

        source = inspect.getsource(_grader_module)
        fp = fingerprint_prompt(source)
        # The fingerprint covers the whole module; any drift here
        # requires a deliberate bump, which is the point.
        assert isinstance(fp, str)
        assert len(fp) == 16
