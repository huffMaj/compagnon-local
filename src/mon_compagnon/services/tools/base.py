"""
La base de tous les outils : un nom, une description, des paramètres, un run().
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class Tool(ABC):
    name: str = ""
    description: str = ""          # lue par l'IA pour choisir l'outil
    parameters: dict = {}          # JSON Schema des arguments
    requires_confirmation: bool = False

    @abstractmethod
    def run(self, **kwargs) -> str:
        """Le travail de l'outil. Renvoie toujours du texte."""

    def to_api_dict(self) -> dict:
        """Format compris par llama-server (style OpenAI)."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class SandboxedTool(Tool, ABC):
    """Outil limité aux dossiers autorisés."""

    def __init__(self, allowed_roots: list[Path] | None = None):
        self._allowed_roots = allowed_roots or [Path.home()]

    def _check_path(self, path: Path) -> Path:
        path = path.expanduser().resolve()
        for root in self._allowed_roots:
            if path.is_relative_to(root.resolve()):
                return path
        roots = ", ".join(str(r) for r in self._allowed_roots)
        raise PermissionError(f"{path} n'est pas dans {roots}")
