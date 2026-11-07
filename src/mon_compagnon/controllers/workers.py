"""
Le worker : lance l'agent en arrière-plan et parle à l'écran par signaux Qt.
"""
from __future__ import annotations

import threading
from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, Signal

from mon_compagnon.domain.conversation import Conversation
from mon_compagnon.domain.settings import AppSettings
from mon_compagnon.services.agent import Agent
from mon_compagnon.services.llm.backend import LlamaBackend
from mon_compagnon.services.llm.streaming import ChunkKind
from mon_compagnon.services.tools.registry import ToolRegistry


class GenerationSignals(QObject):
    text_received = Signal(str)
    finished = Signal()
    error = Signal(str)
    aborted = Signal()


class GenerationWorker(QRunnable):

    def __init__(self, conversation: Conversation, backend: LlamaBackend, settings: AppSettings):
        super().__init__()
        self.signals = GenerationSignals()
        self._conversation = conversation
        self._backend = backend
        self._settings = settings
        self._stop_event = threading.Event()

    def run(self) -> None:
        try:
            agent = Agent(
                backend=self._backend,
                registry=ToolRegistry(allowed_roots=[Path.home()]),
                settings=self._settings,
            )
            for chunk in agent.run(self._conversation):
                if self._stop_event.is_set():
                    self.signals.aborted.emit()
                    return
                if chunk.kind == ChunkKind.TEXT:
                    self.signals.text_received.emit(chunk.text)
                elif chunk.kind == ChunkKind.DONE:
                    self.signals.finished.emit()
                    return
                elif chunk.kind == ChunkKind.ERROR:
                    self.signals.error.emit(chunk.error)
                    return
                elif chunk.kind == ChunkKind.ABORTED:
                    self.signals.aborted.emit()
                    return
        except Exception as e:  # noqa: BLE001 - on remonte toute erreur à l'écran
            self.signals.error.emit(str(e))

    def stop(self) -> None:
        self._stop_event.set()
        self._backend.abort()
