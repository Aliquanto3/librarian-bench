# Changelog

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
