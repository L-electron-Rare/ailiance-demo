"""Unit tests for DatasetsService.stats()."""
import json
from pathlib import Path

import pytest

from ailiance_demo.services.datasets import DatasetsService


@pytest.fixture
def datasets_root(tmp_path: Path) -> Path:
    domain = tmp_path / "stats-domain"
    domain.mkdir()
    (domain / "MANIFEST.json").write_text(
        json.dumps({"hf_dataset_id": "org/stats", "license": "MIT", "download_date": "2026-01-01"})
    )
    # 4 samples with varying lengths and 1 duplicate user
    samples = [
        ("short", "x" * 50),          # asst < 200
        ("short", "x" * 300),          # duplicate user; asst 200-500
        ("unique1", "x" * 700),        # asst 500-1000
        ("unique2", "x" * 1500),       # asst 1000-2000
        ("unique3", "x" * 2500),       # asst >= 2000
    ]
    lines = [
        json.dumps(
            {
                "messages": [
                    {"role": "user", "content": u},
                    {"role": "assistant", "content": a},
                ]
            }
        )
        for u, a in samples
    ]
    (domain / "train.jsonl").write_text("\n".join(lines) + "\n")
    return tmp_path


def svc(root: Path) -> DatasetsService:
    return DatasetsService(roots=[root])


def test_stats_total(datasets_root: Path) -> None:
    s = svc(datasets_root).stats("stats-domain")
    assert s is not None
    assert s.total == 5


def test_stats_averages(datasets_root: Path) -> None:
    s = svc(datasets_root).stats("stats-domain")
    assert s is not None
    assert s.user_len_avg > 0
    assert s.assistant_len_avg > 0


def test_stats_percentiles(datasets_root: Path) -> None:
    s = svc(datasets_root).stats("stats-domain")
    assert s is not None
    assert s.user_len_p50 >= 0
    assert s.user_len_p95 >= s.user_len_p50
    assert s.assistant_len_p95 >= s.assistant_len_p50


def test_stats_duplicate_user(datasets_root: Path) -> None:
    s = svc(datasets_root).stats("stats-domain")
    assert s is not None
    # "short" appears twice
    assert s.duplicate_user_count == 1


def test_stats_length_buckets(datasets_root: Path) -> None:
    s = svc(datasets_root).stats("stats-domain")
    assert s is not None
    buckets = {b.bucket: b.count for b in s.length_buckets}
    assert buckets["<200"] == 1
    assert buckets["200-500"] == 1
    assert buckets["500-1000"] == 1
    assert buckets["1000-2000"] == 1
    assert buckets[">=2000"] == 1


def test_stats_empty_domain(tmp_path: Path) -> None:
    domain = tmp_path / "empty"
    domain.mkdir()
    (domain / "MANIFEST.json").write_text(json.dumps({}))
    (domain / "train.jsonl").write_text("")
    s = DatasetsService(roots=[tmp_path]).stats("empty")
    assert s is not None
    assert s.total == 0
    assert s.duplicate_user_count == 0


def test_stats_unknown_domain_returns_none(datasets_root: Path) -> None:
    result = svc(datasets_root).stats("does-not-exist")
    assert result is None
