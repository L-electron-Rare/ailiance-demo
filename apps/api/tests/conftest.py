"""Shared pytest fixtures."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from kiki_cockpit.main import EU_KIKI_ALIASES, create_app
from kiki_cockpit.models import ModelCard, ModelStatus, ChatBackend
from kiki_cockpit.services.featured import FeaturedConfig
from kiki_cockpit.services.hf_cache import HFCache
from kiki_cockpit.services.eval_index import EvalIndex


@pytest.fixture
def empty_hf_cache(tmp_path: Path) -> HFCache:
    return HFCache(
        owners=[],
        eu_kiki_aliases=EU_KIKI_ALIASES,
        featured=FeaturedConfig(),
        cache_dir=tmp_path / "cache",
    )


@pytest.fixture
def sample_card() -> ModelCard:
    return ModelCard(
        id="clemsail/micro-kiki-v3",
        owner="clemsail",
        name="micro-kiki-v3",
        display_name="Micro-KIKI v3",
        status=ModelStatus.FEATURED,
        chat_backend=ChatBackend.HF_EXTERNAL,
        chat_eligible=False,
        downloads=242,
        likes=4,
        hf_url="https://huggingface.co/clemsail/micro-kiki-v3",
    )


@pytest.fixture
def client_with_cache(empty_hf_cache: HFCache, sample_card: ModelCard) -> TestClient:
    """Build a TestClient with a pre-populated HFCache and skip the lifespan refresh."""
    app = create_app()
    empty_hf_cache._cards = [sample_card]
    # Replace the lifespan-installed cache by overriding app.state directly via dependency_overrides
    from kiki_cockpit.deps import get_hf_cache
    app.dependency_overrides[get_hf_cache] = lambda: empty_hf_cache
    return TestClient(app)


@pytest.fixture
def empty_eval_index(tmp_path: Path) -> EvalIndex:
    return EvalIndex(roots=[tmp_path / "no_evals"])


@pytest.fixture
def client_with_full_state(
    empty_hf_cache: HFCache,
    empty_eval_index: EvalIndex,
    sample_card: ModelCard,
) -> TestClient:
    app = create_app()
    empty_hf_cache._cards = [sample_card]
    from kiki_cockpit.deps import get_hf_cache, get_eval_index
    app.dependency_overrides[get_hf_cache] = lambda: empty_hf_cache
    app.dependency_overrides[get_eval_index] = lambda: empty_eval_index
    return TestClient(app)


@pytest.fixture
def client(client_with_full_state: TestClient) -> TestClient:
    return client_with_full_state
