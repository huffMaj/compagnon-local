"""
Le LlamaBackend : le traducteur entre l'application et llama-server.
"""
from __future__ import annotations

import threading
from typing import Iterator

import httpx

from mon_compagnon.domain.conversation import Conversation
from mon_compagnon.domain.settings import GenerationSettings
from mon_compagnon.services.llm.streaming import Chunk, ToolCallAssembler, parse_sse_line


class LlamaBackend:
    """Parle au llama-server local en HTTP (API compatible OpenAI)."""

    def __init__(self, base_url: str = "http://127.0.0.1:8080"):
        self._base_url = base_url
        self._abort_event = threading.Event()

    @property
    def is_ready(self) -> bool:
        try:
            r = httpx.get(f"{self._base_url}/health", timeout=3.0)
            return r.status_code == 200
        except httpx.HTTPError:
            return False

    def generate(
        self,
        conversation: Conversation,
        settings: GenerationSettings,
        tools: list[dict] | None = None,
    ) -> Iterator[Chunk]:
        """Envoie la conversation et produit les Chunks en streaming."""
        self._abort_event.clear()

        payload: dict = {
            "messages": conversation.messages_for_api(),
            "max_tokens": settings.max_tokens,
            "temperature": settings.temperature,
            "stream": True,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        assembler = ToolCallAssembler()
        has_tool_calls = False

        try:
            with httpx.Client(timeout=120.0) as client:
                with client.stream(
                    "POST", f"{self._base_url}/v1/chat/completions", json=payload
                ) as response:
                    for line in response.iter_lines():
                        if self._abort_event.is_set():
                            yield Chunk.aborted_chunk()
                            return

                        kind, data = parse_sse_line(line)
                        if kind == "done":
                            break
                        if kind != "delta" or not data:
                            continue

                        delta = data["delta"]
                        text = delta.get("content") or ""
                        if text:
                            yield Chunk.text_chunk(text)

                        if delta.get("tool_calls"):
                            has_tool_calls = True
                            assembler.feed(delta)

                        if data["finish_reason"] in ("tool_calls", "stop", "length"):
                            break
        except httpx.HTTPError as e:
            yield Chunk.error_chunk(str(e))
            return

        if has_tool_calls:
            for tc in assembler.get_all():
                yield Chunk.tool_chunk(tc.name, tc.arguments)

        yield Chunk.done_chunk()

    def count_tokens(self, text: str) -> int:
        """Estimation : 1 token ≈ 4 caractères."""
        return len(text) // 4

    def abort(self) -> None:
        """Bouton Stop."""
        self._abort_event.set()
