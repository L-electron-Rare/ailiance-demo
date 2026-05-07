"""Admin datasets gallery endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query

from ailiance_demo.auth.tailscale import require_tailscale_user
from ailiance_demo.deps import get_datasets_service
from ailiance_demo.models import DatasetDetail, DatasetSummary
from ailiance_demo.models.dataset import DatasetPage, DatasetStats
from ailiance_demo.services.datasets import DatasetsService

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(require_tailscale_user)],
)


@router.get("/datasets", response_model=list[DatasetSummary])
def list_datasets(
    svc: DatasetsService = Depends(get_datasets_service),
) -> list[DatasetSummary]:
    return svc.list()


@router.get("/datasets/{domain}/samples", response_model=DatasetPage)
def get_dataset_samples(
    domain: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=200),
    search: str | None = Query(default=None),
    svc: DatasetsService = Depends(get_datasets_service),
) -> DatasetPage:
    page = svc.paginate(domain, offset=offset, limit=limit, search=search)
    if page is None:
        raise HTTPException(status_code=404, detail=f"Dataset {domain} not found")
    return page


@router.get("/datasets/{domain}/stats", response_model=DatasetStats)
def get_dataset_stats(
    domain: str,
    svc: DatasetsService = Depends(get_datasets_service),
) -> DatasetStats:
    stats = svc.stats(domain)
    if stats is None:
        raise HTTPException(status_code=404, detail=f"Dataset {domain} not found")
    return stats


@router.get("/datasets/{domain}", response_model=DatasetDetail)
def get_dataset(
    domain: str,
    svc: DatasetsService = Depends(get_datasets_service),
) -> DatasetDetail:
    detail = svc.get(domain)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Dataset {domain} not found")
    return detail
