"""
Le ChatController : le chef d'orchestre entre l'écran et les services.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, QThreadPool, Signal

from mon_compagnon.controllers.workers import GenerationWorker
from mon_compagnon.domain.conversation import Conversation
from mon_compagnon.domain.settings import AppSettings
from mon_compagnon.paths import load_system_prompt
from mon_compagnon.services.context import ContextCompressor
from mon_compagnon.services.llm.backend import LlamaBackend


class ChatController(QObject):
    text_received = Signal(str)
    generation_done = Signal()
    error_occurred = Signal(str)
    generation_aborted = Signal()

    def __init__(self, backend: LlamaBackend, settings: AppSettings, parent: QObject | None = None):
        super().__init__(parent)
        self._backend = backend
        self._settings = settings
        self._thread_pool = QThreadPool.globalInstance()
        self._current_worker: GenerationWorker | None = None
        self._compressor = ContextCompressor(
            backend=backend, settings=settings, context_size=settings.llm.n_ctx
        )
        self._conversation = self._new_conversation()

    def _new_conversation(self) -> Conversation:
        return Conversation(system_prompt=load_system_prompt())

    def send_message(self, text: str) -> None:
        if not text.strip():
            return
        self._conversation.add_user(text)
        self._compressor.compresser(self._conversation)

        worker = GenerationWorker(self._conversation, self._backend, self._settings)
        worker.signals.text_received.connect(self.text_received)
        worker.signals.finished.connect(self.generation_done)
        worker.signals.error.connect(self.error_occurred)
        worker.signals.aborted.connect(self.generation_aborted)

        self._current_worker = worker
        self._thread_pool.start(worker)

    def stop(self) -> None:
        if self._current_worker:
            self._current_worker.stop()

    def new_conversation(self) -> None:
        self._conversation = self._new_conversation()

    @property
    def conversation(self) -> Conversation:
        return self._conversation
