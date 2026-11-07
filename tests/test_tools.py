import json
from pathlib import Path

from mon_compagnon.services.tools.registry import ToolRegistry

registry = ToolRegistry(allowed_roots=[Path.home()])

print("=== Outils disponibles ===")
for tool in registry.tools:
    print(f"  🔧 {tool.name} : {tool.description[:50]}...")

print()
print("=== Lister le dossier personnel ===")
print(registry.run("list_files", path=str(Path.home()))[:300])

print()
print("=== Sécurité : dossier interdit ===")
print(registry.run("list_files", path="/etc"))

print()
print("=== Format envoyé au LLM ===")
print(json.dumps(registry.to_api_list(), indent=2, ensure_ascii=False)[:400])
