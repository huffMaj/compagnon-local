"""
La fenêtre principale : zone de conversation, zone de saisie, bouton Envoyer/Stop.
"""
from __future__ import annotations

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QMainWindow, QPushButton, QScrollArea,
    QTextEdit, QVBoxLayout, QWidget,
)

from mon_compagnon.controllers.chat import ChatController

_BTN_SEND = """
QPushButton { background-color: #0084ff; color: white; border-radius: 8px; padding: 8px 16px; }
QPushButton:hover { background-color: #0066cc; }
"""
_BTN_STOP = """
QPushButton { background-color: #e04444; color: white; border-radius: 8px; padding: 8px 16px; }
"""


class MessageBubble(QWidget):
    """Bulle bleue à droite (utilisateur) ou grise à gauche (IA)."""

    def __init__(self, text: str, is_user: bool, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(500)
        self.label.setFont(QFont("Arial", 11))
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        if is_user:
            self.label.setStyleSheet(
                "background-color:#0084ff; color:white; border-radius:12px; padding:8px 12px;"
            )
            layout.addStretch()
            layout.addWidget(self.label)
        else:
            self.label.setStyleSheet(
                "background-color:#e8e8e8; color:black; border-radius:12px; padding:8px 12px;"
            )
            layout.addWidget(self.label)
            layout.addStretch()


class MainWindow(QMainWindow):

    def __init__(self, controller: ChatController, parent=None):
        super().__init__(parent)
        self._controller = controller
        self._current_label: QLabel | None = None
        self._is_generating = False
        self._setup_ui()
        self._connect_signals()

    # ── Construction ──────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self.setWindowTitle("Compagnon IA")
        self.setMinimumSize(700, 600)

        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        title = QLabel("💬 Compagnon IA")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("background-color:#1a1a2e; color:white; padding:15px;")
        main.addWidget(title)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("background-color:#f5f5f5;")
        messages_widget = QWidget()
        self._messages_layout = QVBoxLayout(messages_widget)
        self._messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._scroll.setWidget(messages_widget)
        main.addWidget(self._scroll, stretch=1)

        input_widget = QWidget()
        input_widget.setStyleSheet("background-color:white;")
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(10, 10, 10, 10)

        self._input = QTextEdit()
        self._input.setPlaceholderText("Écris ton message ici... (Ctrl+Entrée pour envoyer)")
        self._input.setMaximumHeight(80)
        self._input.setFont(QFont("Arial", 11))
        input_layout.addWidget(self._input, stretch=1)

        self._btn = QPushButton("Envoyer")
        self._btn.setMinimumSize(100, 40)
        self._btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self._btn.setStyleSheet(_BTN_SEND)
        input_layout.addWidget(self._btn)
        main.addWidget(input_widget)

        self._add_bubble("Bonjour ! Je suis Compagnon. Comment puis-je vous aider ?", is_user=False)

    def _connect_signals(self) -> None:
        self._btn.clicked.connect(self._on_button_clicked)
        self._input.installEventFilter(self)
        self._controller.text_received.connect(self._on_text_received)
        self._controller.generation_done.connect(self._on_generation_done)
        self._controller.generation_aborted.connect(self._on_generation_done)
        self._controller.error_occurred.connect(self._on_error)

    # ── Actions ───────────────────────────────────────────────────

    def _on_button_clicked(self) -> None:
        if self._is_generating:
            self._controller.stop()
        else:
            self._send_message()

    def _send_message(self) -> None:
        text = self._input.toPlainText().strip()
        if not text or self._is_generating:
            return
        self._add_bubble(text, is_user=True)
        self._input.clear()
        self._current_label = self._add_bubble("", is_user=False)

        self._is_generating = True
        self._btn.setText("⏹ Stop")
        self._btn.setStyleSheet(_BTN_STOP)
        self._input.setEnabled(False)
        self._controller.send_message(text)

    def _on_text_received(self, text: str) -> None:
        if self._current_label is not None:
            self._current_label.setText(self._current_label.text() + text)
            self._scroll_to_bottom()

    def _on_generation_done(self) -> None:
        self._is_generating = False
        self._current_label = None
        self._btn.setText("Envoyer")
        self._btn.setStyleSheet(_BTN_SEND)
        self._input.setEnabled(True)
        self._input.setFocus()

    def _on_error(self, error: str) -> None:
        if self._current_label is not None:
            self._current_label.setText(f"❌ Erreur : {error}")
        self._on_generation_done()

    # ── Utilitaires ───────────────────────────────────────────────

    def _add_bubble(self, text: str, is_user: bool) -> QLabel:
        bubble = MessageBubble(text, is_user=is_user)
        self._messages_layout.addWidget(bubble)
        self._scroll_to_bottom()
        return bubble.label

    def _scroll_to_bottom(self) -> None:
        bar = self._scroll.verticalScrollBar()
        bar.setValue(bar.maximum())

    def eventFilter(self, obj, event) -> bool:
        """Ctrl+Entrée envoie le message."""
        if obj is self._input and event.type() == QEvent.Type.KeyPress:
            if (event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter)
                    and event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                self._send_message()
                return True
        return super().eventFilter(obj, event)
