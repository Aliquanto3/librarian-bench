"""Fixtures communes."""

from pathlib import Path

import pytest

from librarian_bench.core.types import ParsedCorpus
from librarian_bench.corpus.declare import declare
from librarian_bench.corpus.ingest import ingest

CORPUS_MINICORPUS = (
    Path(__file__).resolve().parent.parent / "corpora" / "minicorpus" / "corpus.yaml"
)


# Question de conformité du Jeu de référence : `factual`, un seul Ancrage, au moins 80 % de ses
# mots dans cet Ancrage (la suite de conformité de l'epic 4 la pose pour exiger une Citation).
CONFORMANCE_QUESTION_ID = "q-001"


@pytest.fixture
def bench_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Dossier d'état local isolé, exposé par la variable `LIBRARIAN_BENCH_HOME`."""
    dossier = tmp_path / "bench_home"
    dossier.mkdir()
    monkeypatch.setenv("LIBRARIAN_BENCH_HOME", str(dossier))
    return dossier


@pytest.fixture(scope="session")
def minicorpus(tmp_path_factory: pytest.TempPathFactory) -> ParsedCorpus:
    """Mini-corpus fictif ingéré avec les Parsers `auto` (sans modèle ni réseau, ce qu'exige le
    profil `test`) et un cache de parsing temporaire ; une seule ingestion pour la session."""
    bench_home = tmp_path_factory.mktemp("bench_home_minicorpus")
    return ingest(declare(CORPUS_MINICORPUS), bench_home=bench_home)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Les tests `real_local` et `real_api` appellent un service réel : le blocage des sockets
    (`--disable-socket`, actif par défaut) ne doit pas les empêcher de joindre Ollama ou l'API."""
    for item in items:
        if item.get_closest_marker("real_local") or item.get_closest_marker("real_api"):
            item.add_marker(pytest.mark.enable_socket)
