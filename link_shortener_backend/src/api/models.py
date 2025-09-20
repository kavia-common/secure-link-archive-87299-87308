from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, AnyHttpUrl, Field


# PUBLIC_INTERFACE
class ShortenRequest(BaseModel):
    """Request to create a shortened URL and archive the page."""
    url: AnyHttpUrl = Field(..., description="The external URL to shorten and archive.")
    note: Optional[str] = Field(None, description="Optional note or label for this link.")


# PUBLIC_INTERFACE
class ShortenResponse(BaseModel):
    """Response payload for a created shortened URL."""
    id: str = Field(..., description="Internal identifier for this short link.")
    code: str = Field(..., description="Short code assigned to the URL.")
    short_url: AnyHttpUrl = Field(..., description="The full shortened URL to share.")
    original_url: AnyHttpUrl = Field(..., description="Original submitted URL.")
    archived_at: datetime = Field(..., description="Timestamp when the content was archived.")


# PUBLIC_INTERFACE
class CompareResponse(BaseModel):
    """Comparison results between archived and current content."""
    id: str = Field(..., description="Link ID.")
    code: str = Field(..., description="Short code.")
    has_changes: bool = Field(..., description="True if content differs.")
    diff_summary: Dict[str, int] = Field(
        ..., description="Summary of changes (e.g., added/removed/changed counts)."
    )
    changed_paths: List[str] = Field(
        default_factory=list, description="List of content blocks/paths that differ."
    )


# PUBLIC_INTERFACE
class ErrorMessage(BaseModel):
    """Standardized error message payload."""
    detail: str = Field(..., description="Human-readable error message.")
