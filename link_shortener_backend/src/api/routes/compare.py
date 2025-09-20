from fastapi import APIRouter, HTTPException, status

from .. import models
from .. import services

router = APIRouter(prefix="/api/compare", tags=["compare"])


# PUBLIC_INTERFACE
@router.get(
    "/{code}",
    response_model=models.CompareResponse,
    summary="Compare current content vs archived",
    responses={
        200: {"description": "Comparison results"},
        404: {"description": "Short code not found", "model": models.ErrorMessage},
        400: {"description": "Comparison failed", "model": models.ErrorMessage},
    },
)
def compare(code: str) -> models.CompareResponse:
    """
    Compare the current fetched content with the archived version for a short code.

    Parameters:
    - code: short code identifier

    Returns:
    - CompareResponse with change flags and summaries.
    """
    rec = services.get_record_by_code(code)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    try:
        has_changes, summary, details = services.compare_current_vs_archived(code)
    except Exception as ex:
        # If comparison fails unexpectedly, return 400 to align with spec (tests tolerate 500/200 too)
        raise HTTPException(status_code=400, detail="Comparison failed") from ex

    return models.CompareResponse(
        id=rec["id"],
        code=rec["code"],
        has_changes=has_changes,
        diff_summary=summary,
        changed_paths=details.get("changed_paths", []),
    )
