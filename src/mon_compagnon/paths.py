"""
Les chemins du projet et le chargement de la personnalité.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RESOURCES = ROOT / "resources"

IDENTITY_FILE = RESOURCES / "identity.md"
CONSTRAINTS_FILE = RESOURCES / "constraints.md"
SOUL_FILE = RESOURCES / "soul.md"

BIN_DIR = ROOT / "bin"
LLAMA_SERVER = BIN_DIR / "llama-server"


def load_system_prompt() -> str:
    """identity.md + constraints.md + soul.md = system prompt."""
    parties = []
    for fichier in (IDENTITY_FILE, CONSTRAINTS_FILE, SOUL_FILE):
        if fichier.exists():
            contenu = fichier.read_text(encoding="utf-8").strip()
            if contenu:
                parties.append(contenu)
        else:
            print(f"⚠️ Fichier manquant : {fichier.name}")
    return "\n\n---\n\n".join(parties)


def find_model(model_name: str) -> Path | None:
    for dossier in (ROOT, BIN_DIR):
        chemin = dossier / model_name
        if chemin.exists():
            return chemin
    return None
