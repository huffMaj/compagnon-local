"""Nécessite llama-server lancé sur le port 8080."""
from mon_compagnon.domain.conversation import Conversation
from mon_compagnon.domain.settings import AppSettings
from mon_compagnon.services.context import ContextCompressor
from mon_compagnon.services.llm.backend import LlamaBackend

backend = LlamaBackend(base_url="http://127.0.0.1:8080")
if not backend.is_ready:
    raise SystemExit("Lance d'abord llama-server (voir README).")

# Fenêtre volontairement minuscule pour forcer la compression
compressor = ContextCompressor(backend, AppSettings(), context_size=10)

conv = Conversation()
conv.add_user("Bonjour, comment vas-tu ?")
conv.add_assistant("Très bien merci ! Et toi ?")
conv.add_user("Je prépare un voyage à Lisbonne en mai.")
conv.add_assistant("D'accord, je peux t'aider à l'organiser.")
conv.add_user("Mon budget est de 800 euros pour 5 jours.")
conv.add_assistant("Je note : 5 jours, budget de 800 euros.")
conv.add_user("Je veux visiter le quartier de l'Alfama.")
conv.add_assistant("Alfama ajouté à la liste des visites.")

print(f"Avant compression : {len(conv)} messages")
if compressor.compresser(conv):
    print(f"Après compression : {len(conv)} messages\n")
    for msg in conv.messages:
        print(f"[{msg.role}] : {msg.content[:100]}")
else:
    print("Pas de compression effectuée")
