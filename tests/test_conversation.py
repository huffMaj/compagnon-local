from mon_compagnon.domain.conversation import Conversation

conv = Conversation(title="Mon premier test")
print("Conversation créée :", repr(conv))

conv.add_user("Bonjour, comment tu t'appelles ?")
conv.add_assistant("Je m'appelle Compagnon !")
conv.add_user("Tu peux lire mes fichiers ?")

print("Nombre de messages :", len(conv))
print("Dernier message :", conv.last_message.content)
print()
print("=== Messages envoyés au LLM ===")
for msg in conv.messages_for_api():
    print(f"[{msg['role']}] : {msg['content'][-60:]}")
