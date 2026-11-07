"""Nécessite llama-server lancé sur le port 8080."""
from mon_compagnon.domain.conversation import Conversation
from mon_compagnon.domain.settings import GenerationSettings
from mon_compagnon.services.llm.backend import LlamaBackend
from mon_compagnon.services.llm.streaming import ChunkKind

backend = LlamaBackend(base_url="http://127.0.0.1:8080")
print("llama-server prêt ?", backend.is_ready)
if not backend.is_ready:
    raise SystemExit("Lance d'abord llama-server (voir README).")

conv = Conversation()
conv.add_user("Dis bonjour en une seule phrase courte")

print("\nL'IA répond mot par mot :\n")
reponse = ""
for chunk in backend.generate(conv, GenerationSettings(max_tokens=50)):
    if chunk.kind == ChunkKind.TEXT:
        print(chunk.text, end="", flush=True)
        reponse += chunk.text
    elif chunk.kind == ChunkKind.DONE:
        print("\n\n✅ Réponse complète reçue !")
    elif chunk.kind == ChunkKind.ERROR:
        print(f"\n❌ Erreur : {chunk.error}")
