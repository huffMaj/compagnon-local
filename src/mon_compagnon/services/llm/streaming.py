"""
Le streaming : l'IA répond morceau par morceau (Chunks),
y compris les appels d'outils (tool_calls).
"""
from __future__ import annotations

import json
from enum import StrEnum

from pydantic import BaseModel


class ChunkKind(StrEnum):
    TEXT = "text"
    TOOL_CALL = "tool_call"
    DONE = "done"
    ERROR = "error"
    ABORTED = "aborted"


class ToolCall(BaseModel):
    """Un appel d'outil demandé par l'IA."""
    name: str
    arguments: dict = {}


class Chunk(BaseModel):
    """Un petit morceau de la réponse de l'IA."""
    kind: ChunkKind
    text: str = ""
    tool_call: ToolCall | None = None
    error: str = ""

    @classmethod
    def text_chunk(cls, text: str) -> "Chunk":
        return cls(kind=ChunkKind.TEXT, text=text)

    @classmethod
    def tool_chunk(cls, name: str, arguments: dict) -> "Chunk":
        return cls(kind=ChunkKind.TOOL_CALL, tool_call=ToolCall(name=name, arguments=arguments))

    @classmethod
    def done_chunk(cls) -> "Chunk":
        return cls(kind=ChunkKind.DONE)

    @classmethod
    def error_chunk(cls, error: str) -> "Chunk":
        return cls(kind=ChunkKind.ERROR, error=error)

    @classmethod
    def aborted_chunk(cls) -> "Chunk":
        return cls(kind=ChunkKind.ABORTED)


class ToolCallAssembler:
    """Recolle les morceaux de tool_calls reçus en streaming."""

    def __init__(self) -> None:
        self._calls: dict[int, dict] = {}

    def feed(self, delta: dict) -> None:
        for tc in delta.get("tool_calls", []) or []:
            idx = tc.get("index", 0)
            call = self._calls.setdefault(idx, {"name": "", "arguments": ""})
            fn = tc.get("function", {}) or {}
            call["name"] += fn.get("name") or ""
            call["arguments"] += fn.get("arguments") or ""

    def get_all(self) -> list[ToolCall]:
        result = []
        for call in self._calls.values():
            if call["name"]:
                try:
                    args = json.loads(call["arguments"] or "{}")
                except json.JSONDecodeError:
                    args = {}
                result.append(ToolCall(name=call["name"], arguments=args))
        return result

    def reset(self) -> None:
        self._calls = {}


def parse_sse_line(line: str) -> tuple[str | None, dict | None]:
    """Lit une ligne SSE.

    ("done", None)   -> fin du flux
    ("delta", {...}) -> un morceau de réponse
    (None, None)     -> ligne à ignorer
    """
    if not line.startswith("data:"):
        return None, None

    data = line[len("data:"):].strip()
    if data == "[DONE]":
        return "done", None

    try:
        obj = json.loads(data)
        choice = obj["choices"][0]
        return "delta", {
            "delta": choice.get("delta", {}) or {},
            "finish_reason": choice.get("finish_reason"),
        }
    except (json.JSONDecodeError, KeyError, IndexError):
        return None, None
