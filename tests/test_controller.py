"""Test du ChatController sans fenêtre. Nécessite llama-server lancé."""
import sys

from PySide6.QtCore import QCoreApplication, QTimer

from mon_compagnon.controllers.chat import ChatController
from mon_compagnon.domain.settings import AppSettings
from mon_compagnon.services.llm.backend import LlamaBackend

app = QCoreApplication(sys.argv)

backend = LlamaBackend(base_url="http://127.0.0.1:8080")
if not backend.is_ready:
    raise SystemExit("Lance d'abord llama-server (voir README).")

controller = ChatController(backend=backend, settings=AppSettings())


def on_text(text: str) -> None:
    print(text, end="", flush=True)


def on_done() -> None:
    print("\n\n✅ Génération terminée !")
    app.quit()


def on_error(error: str) -> None:
    print(f"\n❌ Erreur : {error}")
    app.quit()


controller.text_received.connect(on_text)
controller.generation_done.connect(on_done)
controller.error_occurred.connect(on_error)

print("=== Test du ChatController ===\n")
QTimer.singleShot(100, lambda: controller.send_message("Présente-toi en une phrase courte."))
sys.exit(app.exec())
