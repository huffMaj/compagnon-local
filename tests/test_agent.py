"""Nécessite llama-server lancé sur le port 8080."""
from pathlib import Path

from mon_compagnon.domain.conversation import Conversation
from mon_compagnon.domain.settings import AppSettings
from mon_compagnon.services.agent import Agent
from mon_compagnon.services.llm.backend import LlamaBackend
from mon_compagnon.services.llm.streaming import ChunkKind
from mon_compagnon.services.tools.registry import ToolRegistry

backend = LlamaBackend(base_url="http://127.0.0.1:8080")
if not backend.is_ready:
    raise SystemExit("Lance d'abord llama-server (voir README).")

agent = Agent(backend, ToolRegistry(allowed_roots=[Path.home()]), AppSettings())


def afficher(conv: Conversation) -> None:
    for chunk in agent.run(conv):
        if chunk.kind == ChunkKind.TEXT:
            print(chunk.text, end="", flush=True)
        elif chunk.kind == ChunkKind.DONE:
            print("\n\n✅ Terminé !")
        elif chunk.kind == ChunkKind.ERROR:
            print(f"\n❌ Erreur : {chunk.error}")


print("=== Test 1 : question simple ===\n")
c1 = Conversation()
c1.add_user("Dis bonjour en une phrase.")
afficher(c1)

print("\n=== Test 2 : question avec outil ===\n")
c2 = Conversation()
dossier = Path(__file__).resolve().parent.parent
c2.add_user(f"Liste les fichiers dans {dossier} et dis-moi juste combien il y en a.")
afficher(c2)
