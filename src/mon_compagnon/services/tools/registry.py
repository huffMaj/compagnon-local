"""
Le registre : le catalogue de tous les outils disponibles.
"""
from __future__ import annotations

from pathlib import Path

from mon_compagnon.services.tools.base import Tool
from mon_compagnon.services.tools.filesystem import ListFiles, ReadFile


class ToolRegistry:

    def __init__(self, allowed_roots: list[Path] | None = None):
        roots = allowed_roots or [Path.home()]
        self._tools: dict[str, Tool] = {}
        self._add(ListFiles(allowed_roots=roots))
        self._add(ReadFile(allowed_roots=roots))

    def _add(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    @property
    def tools(self) -> list[Tool]:
        return list(self._tools.values())

    def to_api_list(self) -> list[dict]:
        """Liste envoyée au LLM pour qu'il connaisse les outils."""
        return [t.to_api_dict() for t in self.tools]

    def run(self, name: str, **kwargs) -> str:
        if name not in self._tools:
            return f"Erreur : outil '{name}' inconnu."
        try:
            return self._tools[name].run(**kwargs)
        except TypeError as e:
            return f"Erreur : arguments invalides pour '{name}' ({e})"

    def __repr__(self) -> str:
        return f"ToolRegistry({list(self._tools)})"
