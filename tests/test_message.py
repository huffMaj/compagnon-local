from mon_compagnon.domain.message import Message, Role

m1 = Message(role=Role.USER, content="Bonjour")
print("Test 1 OK :", m1.role, "->", m1.content)

m2 = Message(role=Role.ASSISTANT, content="Salut")
print("Test 2 OK :", m2.role, "->", m2.content)

try:
    Message(role="utilisateur", content="test")
    print("Test 3 ÉCHEC : rôle invalide accepté")
except Exception:
    print("Test 3 OK : rôle invalide refusé par Pydantic")
