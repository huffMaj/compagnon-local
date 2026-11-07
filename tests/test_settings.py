from mon_compagnon.domain.settings import AppSettings

settings = AppSettings()

print("=== Moteur ===")
print("Modèle :", settings.llm.instruct_model)
print("Fenêtre de contexte :", settings.llm.n_ctx, "tokens")
print("Threads CPU :", settings.llm.n_threads)
print()
print("=== Génération ===")
print("Température :", settings.generation.temperature)
print("Max tokens :", settings.generation.max_tokens)
print()
print("=== Agent ===")
print("Max tours :", settings.agent.max_tool_iterations)
print("Compression à :", int(settings.agent.compression_ratio * 100), "%")
print()
try:
    AppSettings(generation={"temperature": 999})
    print("ÉCHEC : température 999 acceptée")
except Exception:
    print("Température 999 refusée ✅")
