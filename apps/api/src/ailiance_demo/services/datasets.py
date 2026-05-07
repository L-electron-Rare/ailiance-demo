"""Read dataset manifests laid out as <root>/<domain>/MANIFEST.json."""
from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path

from ailiance_demo.models.dataset import (
    DatasetDetail,
    DatasetPage,
    DatasetSample,
    DatasetStats,
    DatasetSummary,
    LengthBucket,
)

# Maximum number of samples read for stats computation (performance cap).
_STATS_CAP = 5000


class DatasetsService:
    def __init__(self, roots: list[Path]) -> None:
        self.roots = roots

    def list(self) -> list[DatasetSummary]:
        out: list[DatasetSummary] = []
        for root in self.roots:
            if not root.exists():
                continue
            for manifest_path in sorted(root.glob("*/MANIFEST.json")):
                summary = self._read_summary(manifest_path)
                if summary is not None:
                    out.append(summary)
        return out

    def get(self, domain: str, max_samples: int = 3) -> DatasetDetail | None:
        for root in self.roots:
            manifest_path = root / domain / "MANIFEST.json"
            if not manifest_path.exists():
                continue
            summary = self._read_summary(manifest_path)
            if summary is None:
                continue
            samples = self._read_samples(manifest_path.parent / "train.jsonl", max_samples)
            return DatasetDetail(**summary.model_dump(exclude={"size_mb"}), samples=samples)
        return None

    def paginate(
        self,
        domain: str,
        offset: int = 0,
        limit: int = 10,
        search: str | None = None,
    ) -> DatasetPage | None:
        """Return a paginated slice of samples with optional search filter.

        Search applies a case-insensitive substring match on user OR assistant content.
        Reads the file lazily — only streams until `offset + limit` matches are found
        (or EOF), except when computing total (which requires a full pass).
        """
        jsonl_path = self._find_train_path(domain)
        if jsonl_path is None:
            return None

        query = search.strip().lower() if search else None
        all_samples: list[DatasetSample] = []

        with jsonl_path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msgs = row.get("messages", [])
                user = next((m["content"] for m in msgs if m.get("role") == "user"), "")
                assistant = next(
                    (m["content"] for m in msgs if m.get("role") == "assistant"), ""
                )
                if not user and not assistant:
                    continue
                if query and query not in user.lower() and query not in assistant.lower():
                    continue
                all_samples.append(DatasetSample(user=user, assistant=assistant))

        total = len(all_samples)
        page = all_samples[offset : offset + limit]
        return DatasetPage(
            samples=page,
            total=total,
            offset=offset,
            has_more=(offset + limit) < total,
        )

    def stats(self, domain: str) -> DatasetStats | None:
        """Compute quality statistics for a dataset.

        Reads up to _STATS_CAP lines for performance; documented cap.
        """
        jsonl_path = self._find_train_path(domain)
        if jsonl_path is None:
            return None

        user_lens: list[int] = []
        asst_lens: list[int] = []
        user_contents: list[str] = []

        with jsonl_path.open() as f:
            for line in f:
                if len(user_lens) >= _STATS_CAP:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msgs = row.get("messages", [])
                user = next((m["content"] for m in msgs if m.get("role") == "user"), "")
                assistant = next(
                    (m["content"] for m in msgs if m.get("role") == "assistant"), ""
                )
                if not user and not assistant:
                    continue
                user_lens.append(len(user))
                asst_lens.append(len(assistant))
                user_contents.append(user)

        total = len(user_lens)
        if total == 0:
            return DatasetStats(
                domain=domain,
                total=0,
                user_len_avg=0.0,
                assistant_len_avg=0.0,
                user_len_p50=0,
                user_len_p95=0,
                assistant_len_p50=0,
                assistant_len_p95=0,
                duplicate_user_count=0,
                length_buckets=[],
            )

        def percentile(lst: list[int], p: float) -> int:
            sorted_lst = sorted(lst)
            idx = int(len(sorted_lst) * p / 100)
            idx = min(idx, len(sorted_lst) - 1)
            return sorted_lst[idx]

        counts = Counter(user_contents)
        duplicate_user_count = sum(1 for c in counts.values() if c >= 2)

        buckets = _compute_buckets(asst_lens)

        return DatasetStats(
            domain=domain,
            total=total,
            user_len_avg=round(statistics.mean(user_lens), 2),
            assistant_len_avg=round(statistics.mean(asst_lens), 2),
            user_len_p50=percentile(user_lens, 50),
            user_len_p95=percentile(user_lens, 95),
            assistant_len_p50=percentile(asst_lens, 50),
            assistant_len_p95=percentile(asst_lens, 95),
            duplicate_user_count=duplicate_user_count,
            length_buckets=buckets,
        )

    # ------------------------------------------------------------------ helpers

    def _find_train_path(self, domain: str) -> Path | None:
        for root in self.roots:
            p = root / domain / "train.jsonl"
            if p.exists():
                return p
        return None

    def _read_summary(self, manifest_path: Path) -> DatasetSummary | None:
        try:
            data = json.loads(manifest_path.read_text())
        except (OSError, json.JSONDecodeError):
            return None
        domain = manifest_path.parent.name
        train_path = manifest_path.parent / "train.jsonl"
        size_bytes = train_path.stat().st_size if train_path.exists() else 0
        return DatasetSummary(
            domain=domain,
            name=data.get("hf_dataset_id", domain).split("/")[-1],
            n_rows=int(data.get("n_used") or data.get("n_source_rows") or 0),
            license=str(data.get("license", "unknown")),
            hf_dataset_id=str(data.get("hf_dataset_id", "")),
            download_date=str(data.get("download_date", "")),
            size_bytes=size_bytes,
            notes=data.get("notes"),
        )

    def _read_samples(self, jsonl_path: Path, limit: int) -> list[DatasetSample]:
        if not jsonl_path.exists() or limit <= 0:
            return []
        out: list[DatasetSample] = []
        with jsonl_path.open() as f:
            for line in f:
                if len(out) >= limit:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msgs = row.get("messages", [])
                user = next((m["content"] for m in msgs if m.get("role") == "user"), "")
                assistant = next((m["content"] for m in msgs if m.get("role") == "assistant"), "")
                if user and assistant:
                    out.append(DatasetSample(user=user, assistant=assistant))
        return out


def _compute_buckets(asst_lens: list[int]) -> list[LengthBucket]:
    """Bucket assistant lengths: <200, 200-500, 500-1000, 1000-2000, >=2000."""
    labels = ["<200", "200-500", "500-1000", "1000-2000", ">=2000"]
    counts = [0, 0, 0, 0, 0]
    for n in asst_lens:
        if n < 200:
            counts[0] += 1
        elif n < 500:
            counts[1] += 1
        elif n < 1000:
            counts[2] += 1
        elif n < 2000:
            counts[3] += 1
        else:
            counts[4] += 1
    return [LengthBucket(bucket=label, count=count) for label, count in zip(labels, counts)]
