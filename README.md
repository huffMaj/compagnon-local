# Compagnon — Assistant IA agentique 100 % local

Assistant conversationnel qui tourne entièrement sur la machine, sans
connexion internet. Il répond en streaming et peut lire des fichiers
grâce à des appels d'outils (function calling).

Projet personnel d'apprentissage : reconstruction pas à pas d'une
architecture d'assistant LLM local.

## Fonctionnalités

- Modèle exécuté en local avec **llama.cpp** (format GGUF quantifié)
- Réponses **en streaming**, mot par mot (SSE)
- **Appels d'outils** : lister un dossier, lire un fichier
- **Sandbox** : les outils n'accèdent qu'aux dossiers autorisés
- **Boucle agentique** avec limite d'itérations
- **Compression automatique** de l'historique à 70 % du contexte
- **Personnalité** définie dans des fichiers Markdown (`resources/`)
- Interface **PySide6** qui reste réactive (QThreadPool + signaux Qt)

## Architecture

```
src/mon_compagnon/
├── domain/        # données : Message, Conversation, réglages (Pydantic)
├── services/
│   ├── llm/       # backend HTTP + streaming
│   ├── tools/     # outils + registre
│   ├── agent.py   # boucle agentique
│   └── context.py # compression du contexte
├── controllers/   # workers Qt + contrôleur de chat
├── ui/            # fenêtre principale
├── paths.py       # chemins + chargement de la personnalité
└── app.py         # point d'entrée
resources/         # identity.md, constraints.md, soul.md
tests/             # scripts de test de chaque brique
```

## Installation

Prérequis : Python 3.12 et [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/huffMaj/compagnon-local.git
cd compagnon-local
uv sync
```

### 1. llama-server

Télécharger une version de llama.cpp depuis
https://github.com/ggml-org/llama.cpp/releases (testé avec `b5614`,
`llama-b5614-bin-ubuntu-x64.zip`), puis copier `llama-server`
**et tous les fichiers `.so`** dans un dossier `bin/` :

```bash
mkdir -p bin && cd bin
wget https://github.com/ggml-org/llama.cpp/releases/download/b5614/llama-b5614-bin-ubuntu-x64.zip
unzip llama-b5614-bin-ubuntu-x64.zip
cp build/bin/llama-server build/bin/*.so .
cd ..
```

### 2. Le modèle

Modèle testé : **Mistral-7B-Instruct-v0.3, Q4_K_M** (~4 Go).

```bash
wget "https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3-Q4_K_M.gguf"
```

## Lancement

Terminal 1 — le moteur :

```bash
cd bin
./llama-server --model ../Mistral-7B-Instruct-v0.3-Q4_K_M.gguf \
  --host 127.0.0.1 --port 8080 --ctx-size 4096 --threads 4 --jinja
```

Terminal 2 — l'application :

```bash
PYTHONPATH=src uv run python src/mon_compagnon/app.py
```

## Tests

Les tests sans moteur :

```bash
PYTHONPATH=src uv run python tests/test_message.py
PYTHONPATH=src uv run python tests/test_conversation.py
PYTHONPATH=src uv run python tests/test_settings.py
PYTHONPATH=src uv run python tests/test_tools.py
```

Les tests avec llama-server lancé :

```bash
PYTHONPATH=src uv run python tests/test_backend.py
PYTHONPATH=src uv run python tests/test_agent.py
PYTHONPATH=src uv run python tests/test_context.py
PYTHONPATH=src uv run python tests/test_controller.py
```

## Limites connues

- Avec ce modèle, l'agent fait **un seul cycle d'outil** puis répond :
  le modèle avait tendance à rappeler l'outil en boucle, donc la réponse
  finale est générée sans outils.
- Le nombre de tokens est estimé (1 token ≈ 4 caractères), pas compté exactement.
- Fonctionne sur CPU : environ 4 tokens/seconde sur un portable récent.

## Technologies

Python 3.12 · Pydantic · httpx · PySide6 · llama.cpp · uv
