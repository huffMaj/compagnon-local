"""
Compression du contexte : quand la conversation dépasse 70 % de la
fenêtre, les anciens messages sont résumés par le modèle lui-même.
"""
from __future__ import annotations

from mon_compagnon.domain.conversation import Conversation
from mon_compagnon.domain.message import Message, Role
from mon_compagnon.domain.settings import AppSettings
from mon_compagnon.services.llm.backend import LlamaBackend
from mon_compagnon.services.llm.streaming import ChunkKind

_PROMPT_RESUME = """Tu es un assistant qui résume des conversations.

Résume la conversation ci-dessous en :
- gardant les décisions importantes
- gardant les fichiers mentionnés
- gardant les faits importants
- ignorant les politesses
- restant court et factuel (200 mots maximum)

Réponds UNIQUEMENT avec le résumé."""


class ContextCompressor:

    def __init__(self, backend: LlamaBackend, settings: AppSettings, context_size: int = 4096):
        self._backend = backend
        self._settings = settings
        self._context_size = context_size
        self._seuil = int(context_size * settings.agent.compression_ratio)

    def _compter_tokens(self, conversation: Conversation) -> int:
        return self._backend.count_tokens(" ".join(m.content for m in conversation.messages))

    def doit_compresser(self, conversation: Conversation) -> bool:
        return self._compter_tokens(conversation) >= self._seuil

    def _trouver_point_de_coupure(self, conversation: Conversation) -> int:
        """Coupe vers le milieu, sur un message utilisateur :
        jamais entre un appel d'outil et son résultat."""
        messages = conversation.messages
        for i in range(len(messages) // 2, 0, -1):
            if messages[i].role == Role.USER:
                return i
        return 1

    def compresser(self, conversation: Conversation) -> bool:
        """Compresse si nécessaire. Renvoie True si c'est fait."""
        if not self.doit_compresser(conversation):
            return False

        messages = list(conversation.messages)
        point = self._trouver_point_de_coupure(conversation)
        vieux, recents = messages[:point], messages[point:]
        if not vieux:
            return False

        texte = "\n".join(f"[{m.role}] : {m.content[:200]}" for m in vieux)
        conv_resume = Conversation(system_prompt=_PROMPT_RESUME)
        conv_resume.add_user(f"Voici la conversation à résumer :\n\n{texte}")

        resume = ""
        for chunk in self._backend.generate(conv_resume, self._settings.generation, tools=None):
            if chunk.kind == ChunkKind.TEXT:
                resume += chunk.text
        if not resume.strip():
            return False

        conversation.clear()
        conversation.add(Message(
            role=Role.SYSTEM,
            content=f"[RÉSUMÉ DE LA CONVERSATION PRÉCÉDENTE]\n{resume.strip()}",
        ))
        for m in recents:
            conversation.add(m)
        return True
