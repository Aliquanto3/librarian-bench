"""Compatibilité avec l'ancien nom du produit (WaveLibrarian, renommé LibrarianBench en 0.3.0).

Un seul module :
- la variable `WL_HOME` reste lue en repli quand `LIBRARIAN_BENCH_HOME` est absente, avec un
  `FutureWarning` unique par processus (un `DeprecationWarning` serait masqué hors `__main__`) ;
- l'ancien dossier d'état `./.wl` est copié vers `./.librarian-bench` au premier usage, si le
  nouveau n'existe pas. La copie ne bloque jamais : staging par processus, `OSError` attrapée,
  avertissement visible, ancien dossier intact. Les bases SQLite passent par l'API de sauvegarde
  de `sqlite3` (source en lecture seule) ; les fichiers de verrou et les venvs ne sont pas copiés.
"""

import os
import shutil
import sqlite3
import warnings
from pathlib import Path

ENV_HOME = "LIBRARIAN_BENCH_HOME"
ANCIEN_ENV_HOME = "WL_HOME"
DOSSIER_HOME = ".librarian-bench"
ANCIEN_DOSSIER_HOME = ".wl"
_EXT_SQLITE = {".sqlite", ".sqlite3", ".db"}
_IGNORES_DOSSIERS = {".venv", "venv", "__pycache__"}
_IGNORES_SUFFIXES = {".lock"}

_deja_signale: set[str] = set()


def _avertir_une_fois(cle: str, message: str) -> None:
    if cle in _deja_signale:
        return
    _deja_signale.add(cle)
    warnings.warn(message, FutureWarning, stacklevel=3)


def lire_env(nom: str, ancien_nom: str) -> str | None:
    """Valeur de `nom`, sinon (repli déprécié) de `ancien_nom`. Une valeur vide compte comme
    absente."""
    valeur = os.environ.get(nom)
    if valeur:
        return valeur
    ancienne = os.environ.get(ancien_nom)
    if ancienne:
        _avertir_une_fois(
            ancien_nom,
            f"La variable d'environnement {ancien_nom} est dépréciée : utilisez {nom}.",
        )
        return ancienne
    return None


def env_home() -> str | None:
    """`LIBRARIAN_BENCH_HOME`, sinon `WL_HOME` (déprécié), sinon `None`."""
    return lire_env(ENV_HOME, ANCIEN_ENV_HOME)


def _copier_sqlite(source: Path, cible: Path) -> None:
    src = sqlite3.connect(f"{source.resolve().as_uri()}?mode=ro", uri=True)
    try:
        dst = sqlite3.connect(cible)
        try:
            src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()


def _copier_arbre(source: Path, cible: Path) -> None:
    cible.mkdir(parents=True, exist_ok=True)
    for entree in sorted(source.iterdir()):
        if entree.is_dir():
            if entree.name in _IGNORES_DOSSIERS:
                continue
            _copier_arbre(entree, cible / entree.name)
        elif entree.suffix in _IGNORES_SUFFIXES:
            continue
        elif entree.suffix in _EXT_SQLITE:
            _copier_sqlite(entree, cible / entree.name)
        elif entree.name.endswith(("-wal", "-shm", "-journal")):
            continue
        else:
            shutil.copy2(entree, cible / entree.name)


def migrer_ancien_dossier(
    ancien: Path = Path(ANCIEN_DOSSIER_HOME), nouveau: Path = Path(DOSSIER_HOME)
) -> bool:
    """Copie `ancien` vers `nouveau` si `ancien` existe et `nouveau` non. Rend vrai si copié.

    Ne lève jamais : en cas d'`OSError` (ou d'erreur SQLite), avertit et laisse `nouveau` absent ;
    l'ancien dossier n'est jamais modifié ni supprimé.
    """
    try:
        if nouveau.exists() or not ancien.is_dir():
            return False
        staging = nouveau.with_name(f"{nouveau.name}.migration-{os.getpid()}")
        shutil.rmtree(staging, ignore_errors=True)
        try:
            _copier_arbre(ancien, staging)
            staging.rename(nouveau)
        except (OSError, sqlite3.Error) as e:
            shutil.rmtree(staging, ignore_errors=True)
            warnings.warn(
                f"Migration de {ancien} vers {nouveau} impossible ({e}) : l'ancien dossier "
                "reste utilisable tel quel, copiez-le à la main.",
                FutureWarning,
                stacklevel=2,
            )
            return False
    except OSError as e:  # même l'inspection des dossiers ne doit rien bloquer
        warnings.warn(f"Migration du dossier {ancien} ignorée ({e}).", FutureWarning, stacklevel=2)
        return False
    warnings.warn(
        f"Le dossier d'état {ancien} a été copié vers {nouveau} (LibrarianBench, "
        "ex-WaveLibrarian) ; "
        "l'ancien dossier est conservé, vous pouvez le supprimer.",
        FutureWarning,
        stacklevel=2,
    )
    return True


def dossier_home() -> Path:
    """Dossier d'état par défaut : `LIBRARIAN_BENCH_HOME` (ou `WL_HOME`), sinon
    `./.librarian-bench`.

    Sans variable, migre `./.wl` au premier usage. Si la copie échoue, le nouveau dossier est
    créé à la demande, comme avant.
    """
    env = env_home()
    if env:
        return Path(env)
    migrer_ancien_dossier()
    return Path(DOSSIER_HOME)
