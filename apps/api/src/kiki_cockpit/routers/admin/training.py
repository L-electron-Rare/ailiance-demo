"""Admin training runs endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from kiki_cockpit.auth.tailscale import require_tailscale_user
from kiki_cockpit.deps import get_training_runs_provider
from kiki_cockpit.models import TrainingRun

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(require_tailscale_user)],
)


@router.get("/training/runs", response_model=list[TrainingRun])
def list_training_runs(provider=Depends(get_training_runs_provider)) -> list[TrainingRun]:
    return provider.list_runs()


@router.get("/training/runs/{run_id}", response_model=TrainingRun)
def get_training_run(
    run_id: str,
    provider=Depends(get_training_runs_provider),
) -> TrainingRun:
    run = provider.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return run


@router.get("/training/runs/{run_id}/logs")
async def stream_training_logs(
    run_id: str,
    provider=Depends(get_training_runs_provider),
) -> StreamingResponse:
    run = provider.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    return StreamingResponse(provider.tail_log_sse(run_id), media_type="text/event-stream")
