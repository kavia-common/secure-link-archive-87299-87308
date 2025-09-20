from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import AnyHttpUrl

from .. import models
from ..services import archive_url, get_base_url

router = APIRouter(prefix="/api/urls", tags=["shorten"])


# PUBLIC_INTERFACE
@router.post(
    "/shorten",
    response_model=models.ShortenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Shorten and archive a URL",
    responses={
        201: {"description": "Short link created"},
        400: {"description": "Invalid input or archival failed", "model": models.ErrorMessage},
    },
)
def create_short_link(payload: models.ShortenRequest) -> models.ShortenResponse:
    """
    Create a shortened URL and archive its content.

    Parameters:
    - payload: ShortenRequest with the target URL and optional note.

    Returns:
    - ShortenResponse: id, code, short_url, original_url, archived_at.
    """
    try:
        # Archive and create record
        rec = archive_url(str(payload.url), note=payload.note)
    except ValueError as ve:
        # Validation or security failures
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except Exception as ex:
        raise HTTPException(status_code=400, detail="Archival failed") from ex

    base = get_base_url().rstrip("/")
    short_url: AnyHttpUrl = AnyHttpUrl(f"{base}/r/{rec['code']}")  # type: ignore

    # Build response
    return models.ShortenResponse(
        id=rec["id"],
        code=rec["code"],
        short_url=short_url,
        original_url=AnyHttpUrl(rec["original_url"]),  # type: ignore
        archived_at=datetime.fromisoformat(rec["archived_at"]),
    )
