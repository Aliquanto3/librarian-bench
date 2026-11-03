"""Compatibilité avec l'ancien nom WaveLibrarian : variable `WL_HOME` et dossier `./.wl`."""

import sqlite3
import warnings
from pathlib import Path

import pytest

from librarian_bench import compat


@pytest.fixture(autouse=True)
def _propre(monkeypatch, tmp_path):
    monkeypatch.delenv("LIBRARIAN_BENCH_HOME", raising=False)
    monkeypatch.delenv("WL_HOME", raising=False)
    monkeypatch.setattr(compat, "_deja_signale", set())
    monkeypatch.setattr(compat, "_echecs_migration", set())
    monkeypatch.chdir(tmp_path)


def test_nouvelle_variable_sans_avertissement(monkeypatch):
    monkeypatch.setenv("LIBRARIAN_BENCH_HOME", "/x/nouveau")
    monkeypatch.setenv("WL_HOME", "/x/ancien")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert compat.env_home() == "/x/nouveau"


def test_ancienne_variable_en_repli_avec_future_warning_unique(monkeypatch):
    monkeypatch.setenv("WL_HOME", "/x/ancien")
    with pytest.warns(FutureWarning, match="WL_HOME est dépréciée : utilisez LIBRARIAN_BENCH_HOME"):
        assert compat.env_home() == "/x/ancien"
    with warnings.catch_warnings():  # deuxième lecture : silence
        warnings.simplefilter("error")
        assert compat.env_home() == "/x/ancien"


def test_avertissement_visible_par_defaut(monkeypatch):
    """Un `FutureWarning` s'affiche par défaut (pas `DeprecationWarning`)."""
    monkeypatch.setenv("WL_HOME", "/x/ancien")
    with warnings.catch_warnings(record=True) as vus:
        warnings.resetwarnings()
        warnings.simplefilter("default")
        compat.env_home()
    assert [w.category for w in vus] == [FutureWarning]


def test_aucune_variable_donne_none():
    assert compat.env_home() is None


def test_migration_copie_fichiers_et_sqlite_sans_verrou_ni_venv(tmp_path):
    ancien = tmp_path / ".wl"
    (ancien / "runs" / "r1").mkdir(parents=True)
    (ancien / "runs" / "r1" / "answers.jsonl").write_text('{"a": 1}\n', encoding="utf-8")
    (ancien / "costs.yaml").write_text("x: 1\n", encoding="utf-8")
    (ancien / "run.lock").write_text("", encoding="utf-8")
    (ancien / ".venv").mkdir()
    (ancien / ".venv" / "pyvenv.cfg").write_text("v", encoding="utf-8")
    base = sqlite3.connect(ancien / "ledger.sqlite")
    base.execute("CREATE TABLE t (v INTEGER)")
    base.execute("INSERT INTO t VALUES (42)")
    base.commit()
    base.close()

    with pytest.warns(FutureWarning, match="copié vers"):
        assert compat.migrer_ancien_dossier() is True

    nouveau = tmp_path / ".librarian-bench"
    assert (nouveau / "runs" / "r1" / "answers.jsonl").read_text(encoding="utf-8") == '{"a": 1}\n'
    assert (nouveau / "costs.yaml").read_text(encoding="utf-8") == "x: 1\n"
    assert not (nouveau / "run.lock").exists()
    assert not (nouveau / ".venv").exists()
    copie = sqlite3.connect(nouveau / "ledger.sqlite")
    assert copie.execute("SELECT v FROM t").fetchall() == [(42,)]
    copie.close()
    assert (ancien / "run.lock").exists()  # ancien dossier intact
    assert (ancien / "ledger.sqlite").exists()
    assert not list(tmp_path.glob("*.migration-*"))


def test_seconde_migration_ne_fait_rien(tmp_path):
    (tmp_path / ".wl").mkdir()
    (tmp_path / ".wl" / "a.txt").write_text("1", encoding="utf-8")
    with pytest.warns(FutureWarning):
        assert compat.migrer_ancien_dossier() is True
    (tmp_path / ".wl" / "b.txt").write_text("2", encoding="utf-8")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert compat.migrer_ancien_dossier() is False
    assert not (tmp_path / ".librarian-bench" / "b.txt").exists()


def test_pas_d_ancien_dossier_rien_a_faire(tmp_path):
    assert compat.migrer_ancien_dossier() is False
    assert not (tmp_path / ".librarian-bench").exists()


def test_echec_de_copie_ne_bloque_pas(tmp_path, monkeypatch):
    (tmp_path / ".wl").mkdir()
    (tmp_path / ".wl" / "a.txt").write_text("1", encoding="utf-8")

    def boom(*_a, **_k):
        raise PermissionError("refusé")

    monkeypatch.setattr(compat.shutil, "copy2", boom)
    with pytest.warns(FutureWarning, match="impossible"):
        assert compat.migrer_ancien_dossier() is False
    assert not (tmp_path / ".librarian-bench").exists()
    assert not list(tmp_path.glob("*.migration-*"))
    assert (tmp_path / ".wl" / "a.txt").read_text(encoding="utf-8") == "1"


def test_dossier_home_defaut_migre_puis_rend_le_nouveau(tmp_path):
    (tmp_path / ".wl").mkdir()
    (tmp_path / ".wl" / "a.txt").write_text("1", encoding="utf-8")
    with pytest.warns(FutureWarning):
        assert compat.dossier_home() == Path(".librarian-bench")
    assert (tmp_path / ".librarian-bench" / "a.txt").is_file()


def test_dossier_home_variable_rend_son_chemin_sans_migrer(monkeypatch, tmp_path):
    (tmp_path / ".wl").mkdir()
    monkeypatch.setenv("LIBRARIAN_BENCH_HOME", str(tmp_path / "ailleurs"))
    assert compat.dossier_home() == tmp_path / "ailleurs"
    assert not (tmp_path / ".librarian-bench").exists()


def test_base_sqlite_reconnue_a_son_entete_et_wal_integre(tmp_path):
    """Une base au nom quelconque (`cache.bin`) en mode WAL : copiée par l'API de sauvegarde,
    avec le contenu encore dans le `-wal` ; ni `-wal` ni `-shm` copiés à part."""
    ancien = tmp_path / ".wl"
    ancien.mkdir()
    base = sqlite3.connect(ancien / "cache.bin")
    base.execute("PRAGMA journal_mode=WAL")
    base.execute("PRAGMA wal_autocheckpoint=0")
    base.execute("CREATE TABLE t (v INTEGER)")
    base.execute("INSERT INTO t VALUES (7)")
    base.commit()  # connexion gardée ouverte : les données restent dans le -wal
    try:
        assert (ancien / "cache.bin-wal").exists()
        with pytest.warns(FutureWarning, match="copié vers"):
            assert compat.migrer_ancien_dossier() is True
    finally:
        base.close()
    nouveau = tmp_path / ".librarian-bench"
    assert not (nouveau / "cache.bin-wal").exists()
    assert not (nouveau / "cache.bin-shm").exists()
    copie = sqlite3.connect(nouveau / "cache.bin")
    assert copie.execute("SELECT v FROM t").fetchall() == [(7,)]
    copie.close()


def test_echec_partiel_garde_l_ancien_dossier_puis_reussit_au_lancement_suivant(
    tmp_path, monkeypatch
):
    ancien = tmp_path / ".wl"
    (ancien / "runs").mkdir(parents=True)
    (ancien / "a.txt").write_text("1", encoding="utf-8")
    (ancien / "runs" / "b.txt").write_text("2", encoding="utf-8")
    vrai_copy2 = compat.shutil.copy2
    appels = []

    def copie_partielle(src, dst, *a, **k):  # premier fichier copié, le second échoue
        appels.append(src)
        if len(appels) > 1:
            raise PermissionError("refusé")
        return vrai_copy2(src, dst, *a, **k)

    monkeypatch.setattr(compat.shutil, "copy2", copie_partielle)
    with pytest.warns(FutureWarning, match=r"continue d'utiliser \.wl.*retentée"):
        assert compat.dossier_home() == Path(".wl")
    assert not (tmp_path / ".librarian-bench").exists()
    assert not list(tmp_path.glob("*.migration-*"))
    # même processus : pas de nouvelle tentative, toujours l'ancien dossier
    n = len(appels)
    assert compat.dossier_home() == Path(".wl")
    assert len(appels) == n

    # lancement suivant (nouvel état de processus), copie réparée : migration réussie
    monkeypatch.setattr(compat.shutil, "copy2", vrai_copy2)
    monkeypatch.setattr(compat, "_echecs_migration", set())
    with pytest.warns(FutureWarning, match="copié vers"):
        assert compat.dossier_home() == Path(".librarian-bench")
    assert (tmp_path / ".librarian-bench" / "runs" / "b.txt").read_text(encoding="utf-8") == "2"


def test_dossier_home_repli_wl_home_avec_future_warning(monkeypatch, tmp_path):
    (tmp_path / ".wl").mkdir()
    monkeypatch.setenv("WL_HOME", str(tmp_path / "etat"))
    with pytest.warns(FutureWarning, match="WL_HOME est dépréciée"):
        assert compat.dossier_home() == tmp_path / "etat"
    assert not (tmp_path / ".librarian-bench").exists()
