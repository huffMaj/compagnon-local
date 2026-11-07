"""
La couche DOMAIN : les données pures du projet.

Un message = une bulle de texte, avec un rôle (qui parle) et un contenu.
"""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Role(StrEnum):
    """Les 4 acteurs possibles d'une conversation (liste fermée)."""
    SYSTEM = "system"        # les instructions de départ (la personnalité)
    USER = "user"            # l'humain
    ASSISTANT = "assistant"  # l'IA qui répond
    TOOL = "tool"            # le résultat d'un outil


class Message(BaseModel):
    """Un message dans une conversation = une bulle de texte."""
    role: Role
    content: str = ""
    created_at: float | None = Field(default=None)
