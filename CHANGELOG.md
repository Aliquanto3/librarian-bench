# Changelog

## 0.3.1

Contenu

- Page d'annotation des Juges (`librarian-bench annotations page`) migrée vers la charte générique v2.1 : thème sombre par défaut, clair sous `prefers-color-scheme: light` et `[data-theme="light"]`, jetons de la charte, bouton principal neutre, verdicts Oui / Non en aplats de statut, bascule « Sans objet » en modèle de sélection (`primaire-doux`, texte `texte`, contour `primaire`), texte indicatif du champ de note en `texte-attenue`, contours `trait-fort`, focus visible, filet or sous le titre, Sora et Atkinson Hyperlegible avec leurs piles de repli.
- Test de la page (`tests/unit/report/test_page_annotation_charte.py`) : contrastes 4,5:1 et 3:1 dans les deux thèmes, pas d'aplat bleu de bouton, pas de couleur hors jetons.
- Captures dans `docs/media/charte-v2/`.

Limites

- La page reste autonome et hors ligne : les polices de la charte ne sont pas incorporées, le repli système s'applique si elles sont absentes du poste.
- Le README n'a ni schéma mermaid ni badge : rien à migrer. Les polices DejaVu de `scripts/fonts/` (génération de PDF) et les corpus (`corpora/`) ne changent pas.
- Les pages d'annotation déjà générées gardent l'ancien style jusqu'à leur régénération.
- Exemption de provenance : la clé `localStorage` garde le préfixe `wl-annot-` de l'ancien nom du projet (WaveLibrarian). La renommer ferait perdre aux annotateurs leur progression enregistrée dans le navigateur.

## 0.3.0

- Changement de nom : WaveLibrarian devient **LibrarianBench** (dépôt `librarian-bench`, paquet
  `librarian_bench`, commande `librarian-bench`). Pas d'alias de l'ancienne commande `wl`.
  Les anciens liens GitHub `Aliquanto3/wavelibrarian` redirigent vers le nouveau dépôt.
- Dépôt rendu générique : plus de référence à une marque tierce, ni d'information interne.
- Migration des données : le dossier d'état par défaut passe de `./.wl` à `./.librarian-bench`.
  Au premier lancement, l'ancien dossier est copié (bases SQLite reconnues à leur en-tête et copiées
  par l'API de sauvegarde, sans leurs `-wal`/`-shm` ni les fichiers de verrou et les venvs) ; il
  n'est jamais supprimé. Si la copie échoue, LibrarianBench continue d'utiliser `./.wl` (avec un
  avertissement) et retente la migration au lancement suivant. Arrêtez les Exécutions lancées avec
  l'ancienne version avant de migrer.
- Variables d'environnement : `LIBRARIAN_BENCH_HOME` remplace `WL_HOME`. L'ancienne reste lue en
  repli, avec un `FutureWarning` unique (visible par défaut).
- Les attributs de trace `wl.*` et le marqueur interne `[[wl:role=…]]` ne changent pas, pour que les
  anciennes Exécutions, caches et empreintes restent lisibles.
- La clé de stockage local `wl-annot-…` des pages d'annotation ne change pas non plus : les verdicts
  déjà saisis dans un navigateur restent retrouvés.
- Code : l'exception racine `WlError` devient `LibrarianBenchError`.

## 0.2.0

Version précédente (WaveLibrarian).
