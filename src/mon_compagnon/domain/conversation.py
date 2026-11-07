"""
La Conversation = la boîte qui contient tous les messages.
"""
from __future__ import annotations

import datetime
import time
import uuid

from pydantic import BaseModel, Field

from mon_compagnon.domain.message import Message, Role


def _new_id() -> str:
    """Identifiant unique court (ex: "a3f9bc12")."""
    return uuid.uuid4().hex[:8]


def _now() -> float:
    """Date/heure actuelle en secondes."""
    return time.time()


def _date_actuelle() -> str:
    """Date en français, injectée dans le prompt (le LLM ignore le jour actuel)."""
    now = datetime.datetime.now()
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    mois = ["janvier", "février", "mars", "avril", "mai", "juin",
            "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    return (
        "Date et heure actuelles : "
        f"{jours[now.weekday()]} {now.day} {mois[now.month - 1]} {now.year}, "
        f"{now.strftime('%H:%M')}"
    )


_INSTRUCTIONS_OUTILS = """Quand tu utilises un outil :
1. Utilise l'outil UNE SEULE FOIS
2. Lis le résultat
3. Réponds à l'utilisateur en français avec ce résultat
4. NE rappelle JAMAIS le même outil deux fois de suite"""


class Conversation(BaseModel):
    """La boîte qui contient tous les messages."""
    id: str = Field(default_factory=_new_id)
    title: str = "Nouvelle conversation"
    system_prompt: str = ""
    messages: list[Message] = Field(default_factory=list)
    created_at: float = Field(default_factory=_now)
    updated_at: float = Field(default_factory=_now)

    # ── Ajouter des messages ──────────────────────────────────────

    def add(self, message: Message) -> Message:
        """Point d'entrée unique pour ajouter un message."""
        if message.created_at is None:
            message.created_at = _now()
        self.messages.append(message)
        self.updated_at = message.created_at
        return message

    def add_user(self, content: str) -> Message:
        return self.add(Message(role=Role.USER, content=content))

    def add_assistant(self, content: str = "") -> Message:
        return self.add(Message(role=Role.ASSISTANT, content=content))

    def add_system(self, content: str) -> Message:
        return self.add(Message(role=Role.SYSTEM, content=content))

    # ── Préparer les messages pour le LLM ────────────────────────

    def messages_for_api(self) -> list[dict]:
        """Prépare les messages à envoyer au LLM.

        Ajoute automatiquement en tête : les consignes d'outils,
        la personnalité (system_prompt) et la date du jour.
        """
        parties = [_INSTRUCTIONS_OUTILS]
        if self.system_prompt.strip():
            parties.append(self.system_prompt)
        parties.append(_date_actuelle())

        prefix = [{"role": "system", "content": "\n\n".join(parties)}]
        messages = [{"role": str(m.role), "content": m.content} for m in self.messages]
        return prefix + messages

    # ── Utilitaires ───────────────────────────────────────────────

    def clear(self) -> None:
        self.messages.clear()
        self.updated_at = _now()

    @property
    def last_message(self) -> Message | None:
        return self.messages[-1] if self.messages else None

    def __len__(self) -> int:
        return len(self.messages)

    def __repr__(self) -> str:
        return f"Conversation(id={self.id}, {len(self)} messages)"
