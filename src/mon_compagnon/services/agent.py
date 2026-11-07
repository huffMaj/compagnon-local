"""
L'agent : le chef d'orchestre de la boucle.

1. Envoie messages + outils au LLM
2. Pas d'outil demandé -> réponse finale, fin
3. Outil demandé -> exécution, puis réponse finale générée SANS outils
   (évite que le modèle rappelle l'outil en boucle)
"""
from __future__ import annotations

from typing import Iterator

from loguru import logger

from mon_compagnon.domain.conversation import Conversation
from mon_compagnon.domain.message import Message, Role
from mon_compagnon.domain.settings import AppSettings
from mon_compagnon.services.llm.backend import LlamaBackend
from mon_compagnon.services.llm.streaming import Chunk, ChunkKind
from mon_compagnon.services.tools.registry import ToolRegistry


class Agent:

    def __init__(self, backend: LlamaBackend, registry: ToolRegistry, settings: AppSettings):
        self._backend = backend
        self._registry = registry
        self._settings = settings

    def run(self, conversation: Conversation) -> Iterator[Chunk]:
        max_tours = self._settings.agent.max_tool_iterations

        for _tour in range(max_tours):
            tool_calls_recus = []
            texte_complet = ""

            # ── 1. Le LLM réfléchit, avec les outils disponibles ──
            for chunk in self._backend.generate(
                conversation, self._settings.generation, tools=self._registry.to_api_list()
            ):
                if chunk.kind == ChunkKind.TEXT:
                    texte_complet += chunk.text
                    yield chunk
                elif chunk.kind == ChunkKind.TOOL_CALL:
                    tool_calls_recus.append(chunk.tool_call)
                elif chunk.kind in (ChunkKind.ERROR, ChunkKind.ABORTED):
                    yield chunk
                    return

            # ── 2. Pas d'outil -> c'est fini ──
            if not tool_calls_recus:
                if texte_complet:
                    conversation.add_assistant(texte_complet)
                yield Chunk.done_chunk()
                return

            # ── 3. Exécuter les outils demandés ──
            conversation.add_assistant(texte_complet)
            for tc in tool_calls_recus:
                yield Chunk.text_chunk(f"\n🔧 Utilisation de l'outil : {tc.name}\n")
                resultat = self._registry.run(tc.name, **tc.arguments)
                logger.debug("Résultat de l'outil {} :\n{}", tc.name, resultat[:1000])
                conversation.add(Message(role=Role.TOOL, content=resultat))
                yield Chunk.text_chunk("✅ Résultat reçu\n")

            # ── 4. Réponse finale SANS outils ──
            yield Chunk.text_chunk("\n💭 L'IA analyse le résultat...\n")
            texte_final = ""
            for chunk in self._backend.generate(
                conversation, self._settings.generation, tools=None
            ):
                if chunk.kind == ChunkKind.TEXT:
                    texte_final += chunk.text
                    yield chunk
                elif chunk.kind in (ChunkKind.ERROR, ChunkKind.ABORTED):
                    yield chunk
                    return

            if texte_final:
                conversation.add_assistant(texte_final)
            yield Chunk.done_chunk()
            return

        yield Chunk.text_chunk(f"\n⚠️ Limite de tours atteinte (max : {max_tours})\n")
        yield Chunk.done_chunk()
