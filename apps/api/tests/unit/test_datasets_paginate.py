"""Unit tests for DatasetsService.paginate()."""
import json
from pathlib import Path

import pytest

from ailiance_demo.services.datasets import DatasetsService


@pytest.fixture
def datasets_root(tmp_path: Path) -> Path:
    domain = tmp_path / "test-domain"
    domain.mkdir()
    (domain / "MANIFEST.json").write_text(
        json.dumps({"hf_dataset_id": "org/test", "license": "MIT", "download_date": "2026-01-01"})
    )
    lines = []
    for i in range(25):
        lines.append(
            json.dumps(
                {
                    "messages": [
                        {"role": "user", "content": f"question {i}"},
                        {"role": "assistant", "content": f"answer {i} long text here"},
                    ]
                }
            )
        )
    (domain / "train.jsonl").write_text("\n".join(lines) + "\n")
    return tmp_path


def svc(root: Path) -> DatasetsService:
    return DatasetsService(roots=[root])


def test_paginate_first_page(datasets_root: Path) -> None:
    page = svc(datasets_root).paginate("test-domain", offset=0, limit=10)
    assert page is not None
    assert len(page.samples) == 10
    assert page.total == 25
    assert page.offset == 0
    assert page.has_more is True


def test_paginate_last_page(datasets_root: Path) -> None:
    page = svc(datasets_root).paginate("test-domain", offset=20, limit=10)
    assert page is not None
    assert len(page.samples) == 5
    assert page.has_more is False


def test_paginate_offset_equals_total(datasets_root: Path) -> None:
    page = svc(datasets_root).paginate("test-domain", offset=25, limit=10)
    assert page is not None
    assert len(page.samples) == 0
    assert page.has_more is False
    assert page.total == 25


def test_paginate_offset_beyond_total(datasets_root: Path) -> None:
    page = svc(datasets_root).paginate("test-domain", offset=999, limit=10)
    assert page is not None
    assert len(page.samples) == 0
    assert page.has_more is False


def test_paginate_limit_larger_than_remaining(datasets_root: Path) -> None:
    page = svc(datasets_root).paginate("test-domain", offset=22, limit=100)
    assert page is not None
    assert len(page.samples) == 3


def test_paginate_search_match(datasets_root: Path) -> None:
    page = svc(datasets_root).paginate("test-domain", offset=0, limit=50, search="question 1")
    assert page is not None
    # matches "question 1", "question 10".."question 19" = 11 total
    assert page.total == 11
    assert all("question 1" in s.user.lower() for s in page.samples)


def test_paginate_search_no_hits(datasets_root: Path) -> None:
    page = svc(datasets_root).paginate("test-domain", offset=0, limit=10, search="xyznotfound")
    assert page is not None
    assert page.total == 0
    assert page.samples == []
    assert page.has_more is False


def test_paginate_search_in_assistant(datasets_root: Path) -> None:
    page = svc(datasets_root).paginate("test-domain", offset=0, limit=50, search="long text")
    assert page is not None
    assert page.total == 25


def test_paginate_search_case_insensitive(datasets_root: Path) -> None:
    page = svc(datasets_root).paginate("test-domain", offset=0, limit=50, search="QUESTION")
    assert page is not None
    assert page.total == 25


def test_paginate_unknown_domain_returns_none(datasets_root: Path) -> None:
    result = svc(datasets_root).paginate("does-not-exist")
    assert result is None
