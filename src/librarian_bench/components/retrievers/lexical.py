"""Retriever `lexical` : classement BM25 de l'index lexical."""

from typing import Any

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict

from librarian_bench.core.errors import LibrarianBenchError
from librarian_bench.core.types import ScoredPassage
from librarian_bench.ports.components import SearchIndex
from librarian_bench.registry import register


@register("retriever", "lexical")
class LexicalRetriever:
    """Les k Passages les mieux classés par l'index lexical de l'`SearchIndex`."""

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)

    def __init__(self, params: "LexicalRetriever.Params", ctx: Any) -> None:
        pass

    def retrieve(
        self,
        query: str,
        k: int,
        index: SearchIndex,
        query_vector: NDArray[np.float32] | None = None,
    ) -> list[ScoredPassage]:
        if index.lexical is None:
            raise LibrarianBenchError("le retriever `lexical` exige un index lexical")
        # `k` s'applique après le filtre : on élargit la recherche tant que des ids inconnus
        # des Passages réduisent la liste sous `k`.
        demande = k
        while True:
            bruts = index.lexical.search(query, demande)
            trouves = [(i, s) for i, s in bruts if i in index.passages][:k]
            if len(trouves) >= k or len(bruts) < demande:
                break
            demande *= 2
        return [
            ScoredPassage(passage=index.passages[i], score=s, rank=r)
            for r, (i, s) in enumerate(trouves, start=1)
        ]
