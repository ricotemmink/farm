"""
OpenAI-compatible proxy that routes /v1/chat/completions to the Claude CLI.
SynthOrg points its LiteLLM driver here (openai provider, base_url=http://claude-proxy:5000/v1).
"""

import json
import os
import re
import subprocess
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Claude CLI Proxy", version="1.0.0")

CLAUDE_BIN = "/usr/local/bin/claude"
SUPPORTED_MODELS = [
    "claude-opus-4-7",
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001",
    "sonnet",
    "haiku",
]


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = "claude-sonnet-4-6"
    messages: list[Message]
    temperature: float | None = 0.7
    max_tokens: int | None = 4096
    stream: bool | None = False


def _run_claude(model: str, messages: list[Message]) -> str:
    system_prompt = None
    user_parts = []
    for m in messages:
        if m.role == "system":
            system_prompt = m.content
        else:
            user_parts.append(m.content)

    prompt = "\n".join(user_parts)

    cmd = [
        CLAUDE_BIN,
        "-p", prompt,
        "--model", model,
        "--no-session-persistence",
        "--output-format", "json",
    ]
    if system_prompt:
        cmd.extend(["--append-system-prompt", system_prompt])

    clean_env = {
        k: v for k, v in os.environ.items()
        if k not in ("ANTHROPIC_API_KEY", "CLAUDE_CODE_SIMPLE")
    }

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=180, env=clean_env
    )

    if result.returncode != 0:
        raise RuntimeError(f"claude CLI error (exit {result.returncode}): {result.stderr[:500]}")

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from claude CLI: {result.stdout[:300]}") from e

    if output.get("is_error"):
        raise RuntimeError(f"claude CLI returned error: {output.get('result', 'unknown')}")

    content = output.get("result", "")
    content = re.sub(r"<think>[\s\S]*?</think>", "", content).strip()
    return content


@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": m,
                "object": "model",
                "created": 1700000000,
                "owned_by": "anthropic",
            }
            for m in SUPPORTED_MODELS
        ],
    }


@app.post("/v1/chat/completions")
def chat_completions(req: ChatRequest):
    if req.stream:
        raise HTTPException(status_code=400, detail="Streaming not supported by this proxy")

    try:
        content = _run_claude(req.model, req.messages)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Claude CLI timed out")
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    created = int(time.time())
    prompt_tokens = sum(len(m.content.split()) for m in req.messages)
    completion_tokens = len(content.split())

    return JSONResponse({
        "id": completion_id,
        "object": "chat.completion",
        "created": created,
        "model": req.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    })


@app.get("/health")
def health():
    binary_ok = Path(CLAUDE_BIN).is_file() and os.access(CLAUDE_BIN, os.X_OK)
    return {"status": "ok" if binary_ok else "degraded", "binary": CLAUDE_BIN, "binary_ok": binary_ok}
