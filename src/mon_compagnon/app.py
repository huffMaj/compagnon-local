"""
Point d'entrée de l'application.

1. Crée l'app Qt
2. Crée le backend (connexion au llama-server)
3. Crée le contrôleur
4. Crée et affiche la fenêtre
"""
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from mon_compagnon.controllers.chat import ChatController
from mon_compagnon.domain.settings import AppSettings
from mon_compagnon.services.llm.backend import LlamaBackend
from mon_compagnon.ui.window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Compagnon IA")

    settings = AppSettings()
    port = settings.llm.server_port or 8080
    backend = LlamaBackend(base_url=f"http://{settings.llm.server_host}:{port}")

    if not backend.is_ready:
        QMessageBox.critical(
            None,
            "Erreur de connexion",
            f"Impossible de joindre llama-server sur le port {port}.\n\n"
            "Lance d'abord llama-server (voir le README).",
        )
        sys.exit(1)

    controller = ChatController(backend=backend, settings=settings)
    window = MainWindow(controller=controller)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
