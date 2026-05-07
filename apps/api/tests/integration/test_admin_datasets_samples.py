"""Integration tests for /api/admin/datasets/{domain}/samples."""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ailiance_demo.deps import get_datasets_service
from ailiance_demo.main import app
from ailiance_demo.services.datasets import DatasetsService

HEADERS = {"X-Tailscale-User": "test"}


@pytest.fixture
def client_with_samples(tmp_path: Path):
    domain = tmp_path / "python"
    domain.mkdir()
    (domain / "MANIFEST.json").write_text(
        json.dumps({"hf_dataset_id": "org/python", "license": "MIT", "download_date": "2026-01-01"})
    )
    lines = [
        json.dumps(
            {
                "messages": [
                    {"role": "user", "content": f"user {i}"},
                    {"role": "assistant", "content": f"assistant {i}"},
                ]
            }
        )
        for i in range(30)
    ]
    (domain / "train.jsonl").write_text("\n".join(lines) + "\n")

    app.dependency_overrides[get_datasets_service] = lambda: DatasetsService(roots=[tmp_path])
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_samples_requires_auth(client_with_samples: TestClient) -> None:
    r = client_with_samples.get("/api/admin/datasets/python/samples")
    assert r.status_code == 401


def test_samples_returns_page(client_with_samples: TestClient) -> None:
    r = client_with_samples.get(
        "/api/admin/datasets/python/samples?limit=5", headers=HEADERS
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 30
    assert len(body["samples"]) == 5
    assert body["has_more"] is True
    assert body["offset"] == 0


def test_samples_pagination_offset(client_with_samples: TestClient) -> None:
    r = client_with_samples.get(
        "/api/admin/datasets/python/samples?offset=28&limit=10", headers=HEADERS
    )
    assert r.status_code == 200
    body = r.json()
    assert len(body["samples"]) == 2
    assert body["has_more"] is False


def test_samples_search(client_with_samples: TestClient) -> None:
    r = client_with_samples.get(
        "/api/admin/datasets/python/samples?search=user+1&limit=50", headers=HEADERS
    )
    assert r.status_code == 200
    body = r.json()
    # "user 1", "user 10".."user 19" = 11
    assert body["total"] == 11


def test_samples_unknown_domain_returns_404(client_with_samples: TestClient) -> None:
    r = client_with_samples.get(
        "/api/admin/datasets/missing/samples", headers=HEADERS
    )
    assert r.status_code == 404
