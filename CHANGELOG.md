# Changelog

## 0.3.0

- Changement de nom : WaveLibrarian devient **LibrarianBench** (dépôt `librarian-bench`, paquet
  `librarian_bench`, commande `librarian-bench`). Pas d'alias de l'ancienne commande `wl`.
  Les anciens liens GitHub `Aliquanto3/wavelibrarian` redirigent vers le nouveau dépôt.
- Dépôt rendu générique : plus de référence à une marque tierce, ni d'information interne.
- Migration des données : le dossier d'état par défaut passe de `./.wl` à `./.librarian-bench`.
  Au premier lancement, l'ancien dossier est copié (bases SQLite par l'API de sauvegarde, sans les
  fichiers de verrou ni les venvs) ; il n'est jamais supprimé, et un échec de copie n'empêche rien.
- Variables d'environnement : `LIBRARIAN_BENCH_HOME` remplace `WL_HOME`. L'ancienne reste lue en
  repli, avec un `FutureWarning` unique (visible par défaut).
- Les attributs de trace `wl.*` et le marqueur interne `[[wl:role=…]]` ne changent pas, pour que les
  anciennes Exécutions, caches et empreintes restent lisibles.

## 0.2.0

Version précédente (WaveLibrarian).
