"""Pydantic schemas for dataset gallery + training designer."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, computed_field


class DatasetSample(BaseModel):
    user: str
    assistant: str


class DatasetSummary(BaseModel):
    domain: str
    name: str
    n_rows: int
    license: str
    hf_dataset_id: str
    download_date: str
    size_bytes: int
    notes: str | None = None

    @computed_field  # type: ignore[misc]
    @property
    def size_mb(self) -> float:
        return round(self.size_bytes / (1024 * 1024), 2)


class DatasetDetail(DatasetSummary):
    samples: list[DatasetSample] = Field(default_factory=list)


class DatasetPage(BaseModel):
    samples: list[DatasetSample]
    total: int
    offset: int
    has_more: bool


class LengthBucket(BaseModel):
    bucket: str
    count: int


class DatasetStats(BaseModel):
    domain: str
    total: int
    user_len_avg: float
    assistant_len_avg: float
    user_len_p50: int
    user_len_p95: int
    assistant_len_p50: int
    assistant_len_p95: int
    duplicate_user_count: int
    length_buckets: list[LengthBucket]


class Flag(BaseModel):
    idx: int
    reason: str
    flagged_at: datetime
    flagged_by: str | None = None
