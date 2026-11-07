"""
Outils fichiers : lister un dossier, lire un fichier texte.
"""
from __future__ import annotations

from pathlib import Path

from mon_compagnon.services.tools.base import SandboxedTool

_PATH_PARAM = {
    "type": "object",
    "properties": {"path": {"type": "string", "description": "Le chemin à utiliser"}},
    "required": ["path"],
}


class ListFiles(SandboxedTool):
    name = "list_files"
    description = (
        "Liste les fichiers et dossiers dans un chemin donné. "
        "Utilise cet outil quand l'utilisateur veut voir ce qu'il y a dans un dossier."
    )
    parameters = _PATH_PARAM

    def run(self, path: str) -> str:
        try:
            dossier = self._check_path(Path(path))
            if not dossier.exists():
                return f"Erreur : le dossier '{path}' n'existe pas."
            if not dossier.is_dir():
                return f"Erreur : '{path}' n'est pas un dossier."

            elements = sorted(dossier.iterdir())
            if not elements:
                return f"Le dossier '{path}' est vide."

            lignes = [f"Contenu de '{path}' :"]
            for e in elements:
                if e.is_dir():
                    lignes.append(f"  📁 {e.name}/")
                else:
                    lignes.append(f"  📄 {e.name} ({e.stat().st_size} octets)")
            return "\n".join(lignes)
        except PermissionError as e:
            return f"Accès refusé : {e}"
        except OSError as e:
            return f"Erreur : {e}"


class ReadFile(SandboxedTool):
    name = "read_file"
    description = (
        "Lit et renvoie le contenu d'un fichier texte. "
        "Utilise cet outil quand l'utilisateur veut lire ou analyser un fichier."
    )
    parameters = _PATH_PARAM

    MAX_BYTES = 100_000

    def run(self, path: str) -> str:
        try:
            fichier = self._check_path(Path(path))
            if not fichier.exists():
                return f"Erreur : le fichier '{path}' n'existe pas."
            if not fichier.is_file():
                return f"Erreur : '{path}' n'est pas un fichier."

            taille = fichier.stat().st_size
            if taille > self.MAX_BYTES:
                return f"Fichier trop grand ({taille} octets). Maximum 100 Ko."

            contenu = fichier.read_text(encoding="utf-8", errors="replace")
            return f"Contenu de '{path}' :\n\n{contenu}"
        except PermissionError as e:
            return f"Accès refusé : {e}"
        except OSError as e:
            return f"Erreur : {e}"
