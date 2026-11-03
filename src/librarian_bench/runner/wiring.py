"""Câblage de la passerelle mesurée depuis un profil (joint `llm` à `measure`)."""

from collections.abc import Callable
from functools import partial

from librarian_bench.config.catalog import ModelCatalog
from librarian_bench.config.experiment import RetrySettings
from librarian_bench.config.schemas import ProfileSettings
from librarian_bench.llm.budget import Ledger
from librarian_bench.llm.cache import ResponseCache
from librarian_bench.llm.gateway import MeteredGateway, Providers, build_providers
from librarian_bench.measure.energy import init_ecologits, make_estimator
from librarian_bench.measure.tokenizers import make_tokenizer, tokenizer_for
from librarian_bench.ports.measure import Tracer


def build_gateway(
    *,
    catalog: ModelCatalog,
    profile: ProfileSettings,
    providers: Providers | None = None,
    ledger: Ledger,
    cache: ResponseCache,
    tracer: Tracer,
    retries: RetrySettings | None = None,
    cache_scope: Callable[[], str | None] | None = None,
) -> MeteredGateway:
    """Tokenizer de référence du profil, estimateur d'énergie du profil, délai d'appel du profil.

    Sans `providers`, branche les adaptateurs du Catalogue (`build_providers`) ; avec l'estimateur
    `ecologits`, appelle `init_ecologits()` pour que les réponses Anthropic portent `impacts`.
    Le gestionnaire de `run.log` et `limiter_journaux` reviennent au runner (epic 4).
    """
    reference = make_tokenizer(profile.tokenizer)
    estimator = make_estimator(profile.energy)  # WlError sans l'extra `energy`
    if profile.energy.api == "ecologits":
        init_ecologits()
    if providers is None:
        providers = build_providers(catalog, profile.ollama)
    return MeteredGateway(
        catalog=catalog,
        providers=providers,
        ledger=ledger,
        cache=cache,
        tracer=tracer,
        tokenizer_for=partial(tokenizer_for, catalog=catalog, reference=reference),
        estimator=estimator,
        retries=retries,
        default_timeout_s=profile.defaults.call_timeout_s,
        cache_scope=cache_scope,
    )
