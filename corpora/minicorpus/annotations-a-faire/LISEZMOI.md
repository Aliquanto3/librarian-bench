# Double annotation partielle (story 9.12)

Objectif : mesurer le kappa inter-annotateurs prévu par FR-38. Un second annotateur note 25 lignes déjà annotées par Anaël (21 Réponses du run mini-cpu `20261018-115941-a2a512` : 11 completeness, 3 correctness, 11 faithfulness), sans voir les verdicts d'Anaël ni ceux des Juges.

Ce dossier est hors de `corpora/minicorpus/annotations/` : `librarian-bench calibrer` n'y lit pas de verdicts vides.

## Fichiers

- `annotateur2.yaml` : paquet à remplir, tiré de `anael.yaml` par `librarian-bench annotations exporter --depuis … --nombre 25 --graine 9` (stratifié par Critère, aucune ligne de q-044).
- `annotateur2.html` : page d'annotation autonome (hors ligne), produite par `librarian-bench annotations page`.
- `calibration-inter-annotateurs.yaml` : Expérience de calibration à lancer après l'import (2 passes, ~0,70 USD, plafond 1,00 USD).

## Pour l'annotateur

1. Ouvrir `annotateur2.html` dans un navigateur. Lire la consigne de chaque Critère, en particulier celle de la fidélité :
   - une Réponse est fidèle si tout ce qu'elle affirme est étayé par les extraits fournis, même si l'extrait est faux ;
   - une Réponse qui n'affirme rien de vérifiable est « sans objet ».
2. Pour chaque ligne, choisir Oui, Non ou Sans objet ; une note est facultative.
3. Exporter : le bouton produit `verdicts-annotateur2.json`.

## Pour Anaël, ensuite

Remplacer `annotateur2` par le nom réel si besoin (champ `annotator` du YAML et nom du fichier), puis, depuis la racine du dépôt :

```
uv run librarian-bench annotations importer corpora/minicorpus/annotations-a-faire/annotateur2.yaml verdicts-annotateur2.json
cp corpora/minicorpus/annotations-a-faire/annotateur2.yaml corpora/minicorpus/annotations/
LIBRARIAN_BENCH_HOME=../wl-runs-v0.2.0 uv run --extra energy librarian-bench calibrer corpora/minicorpus/annotations-a-faire/calibration-inter-annotateurs.yaml --annotations corpora/minicorpus/annotations --run 20261018-115941-a2a512 --sortie ../wl-runs-v0.2.0/runs/20261018-115941-a2a512/calibration-inter.json
```

Le kappa inter-annotateurs figure dans `calibration-inter.json` et dans la section « Calibration des Juges » du Rapport. Il porte sur les lignes doublement annotées (hors `na`), soit 25 lignes au plus.
