import hashlib
import json
import os
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

import httpx
from bs4 import BeautifulSoup  # type: ignore

# Local storage root (created automatically)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ARCHIVE_DIR = DATA_DIR / "archives"
INDEX_FILE = DATA_DIR / "index.json"

# Ensure directories exist
os.makedirs(ARCHIVE_DIR, exist_ok=True)


def _now_utc() -> datetime:
    """Return current UTC time with tzinfo."""
    return datetime.now(timezone.utc)


# PUBLIC_INTERFACE
def get_base_url() -> str:
    """Derive base URL for generated short URLs from environment or sensible default."""
    base = os.getenv("BACKEND_BASE_URL")
    if base:
        return base.rstrip("/")
    return "http://localhost:8000"


def _load_index() -> Dict[str, Any]:
    if INDEX_FILE.exists():
        with INDEX_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {"by_code": {}, "by_id": {}}


def _save_index(data: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with INDEX_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def _safe_fetch(url: str, timeout: float = 10.0) -> Tuple[str, str]:
    """
    Fetch a URL with safe settings:
    - Only http/https
    - Limit redirects
    - Restrict content size
    Returns (content, content_type)
    """
    if not re.match(r"^https?://", url, flags=re.IGNORECASE):
        raise ValueError("Only http/https URLs are allowed.")

    # Disallow potentially dangerous localhost and link-local hostnames
    if re.search(r"(?i)://(localhost|127\.0\.0\.1|::1|\[::1\])", url):
        raise ValueError("Localhost URLs are not allowed.")

    max_bytes = 1_500_000  # 1.5 MB cap for archive content

    with httpx.Client(follow_redirects=True, timeout=timeout, limits=httpx.Limits(max_keepalive_connections=2)) as client:
        resp = client.get(url, headers={"User-Agent": "SecureLinkArchive/1.0"})
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "text/html").split(";")[0].strip()

        content = resp.text
        # Enforce size cap for text; for non-text fall back to empty
        if isinstance(content, str):
            if len(content.encode("utf-8")) > max_bytes:
                content = content.encode("utf-8")[:max_bytes].decode("utf-8", errors="ignore")
        else:
            content = ""

        return content, content_type


def _normalize_html(html: str) -> str:
    """Strip scripts/styles and normalize whitespace for diffing."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text("\n")
    # Collapse excessive whitespace
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)


def _generate_code(url: str) -> str:
    """Generate a short code using url hash and a random salt."""
    h = hashlib.sha256((url + secrets.token_urlsafe(8)).encode("utf-8")).hexdigest()
    return h[:8]


# PUBLIC_INTERFACE
def archive_url(url: str, note: Optional[str] = None) -> Dict[str, Any]:
    """
    Archive a URL's content and create a short code entry.

    Returns a record with:
    - id, code, original_url, archived_at, archive_path, content_type
    """
    content, content_type = _safe_fetch(url)

    norm = _normalize_html(content) if content_type.startswith("text/html") else content
    archived_at = _now_utc()

    code = _generate_code(url)
    _id = hashlib.md5(f"{url}-{archived_at.isoformat()}".encode()).hexdigest()

    # Persist archive
    archive_file = ARCHIVE_DIR / f"{code}.txt"
    with archive_file.open("w", encoding="utf-8") as f:
        f.write(norm)

    # Update index
    index = _load_index()
    rec = {
        "id": _id,
        "code": code,
        "original_url": url,
        "archived_at": archived_at.isoformat(),
        "archive_file": str(archive_file),
        "content_type": content_type,
        "note": note,
    }
    index["by_code"][code] = rec
    index["by_id"][rec["id"]] = rec
    _save_index(index)

    return rec


# PUBLIC_INTERFACE
def get_record_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Lookup an archive record by short code."""
    index = _load_index()
    return index["by_code"].get(code)


# PUBLIC_INTERFACE
def get_record_by_id(_id: str) -> Optional[Dict[str, Any]]:
    """Lookup an archive record by ID."""
    index = _load_index()
    return index["by_id"].get(_id)


# PUBLIC_INTERFACE
def get_archived_content(code: str) -> Optional[str]:
    """Load archived normalized content for a given code."""
    rec = get_record_by_code(code)
    if not rec:
        return None
    p = Path(rec["archive_file"])
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8")


# PUBLIC_INTERFACE
def compare_current_vs_archived(code: str) -> Tuple[bool, Dict[str, int], Dict[str, Any]]:
    """
    Compare current fetched normalized content with archived version.

    Returns:
    - has_changes: bool
    - summary: dict with added/removed/changed counts
    - details: dict with changed_paths (line indexes) and maybe future structured diffs
    """
    rec = get_record_by_code(code)
    if not rec:
        raise KeyError("Record not found")

    archived = get_archived_content(code) or ""
    try:
        curr_raw, content_type = _safe_fetch(rec["original_url"])
        current = _normalize_html(curr_raw) if content_type.startswith("text/html") else curr_raw
    except Exception:
        return False, {"added": 0, "removed": 0, "changed": 0}, {"changed_paths": [], "error": "fetch_failed"}

    archived_lines = archived.splitlines()
    current_lines = current.splitlines()

    added = max(0, len(current_lines) - len(archived_lines))
    removed = max(0, len(archived_lines) - len(current_lines))
    changed = sum(
        1 for i in range(min(len(archived_lines), len(current_lines)))
        if archived_lines[i] != current_lines[i]
    )

    changed_positions = [
        f"line:{i+1}" for i in range(min(len(archived_lines), len(current_lines)))
        if archived_lines[i] != current_lines[i]
    ]

    has_changes = (added + removed + changed) > 0
    summary = {"added": added, "removed": removed, "changed": changed}
    details = {"changed_paths": changed_positions}
    return has_changes, summary, details
