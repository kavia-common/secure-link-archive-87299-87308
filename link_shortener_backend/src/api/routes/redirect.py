from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import HTMLResponse

from ..services import get_record_by_code, get_archived_content

router = APIRouter(tags=["redirect"])


# PUBLIC_INTERFACE
@router.get(
    "/r/{code}",
    response_class=HTMLResponse,
    summary="Serve archived page with floating header",
    responses={
        200: {"description": "HTML content"},
        404: {"description": "Short code not found"},
    },
)
def redirect_with_header(code: str) -> Response:
    """
    Serve the archived normalized content wrapped with a minimal HTML page that
    includes floating header stylesheet and script.

    Parameters:
    - code: short code for the archived record

    Returns:
    - HTML page embedding archived content and header assets references.
    """
    rec = get_record_by_code(code)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    archived = get_archived_content(code)
    if archived is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archive missing")

    # Basic HTML template; archived content is escaped via pre tag context naturally as text.
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta http-equiv="X-UA-Compatible" content="IE=edge"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Archived Content - {code}</title>
  <link rel="stylesheet" href="/api/header/style.css"/>
</head>
<body>
  <header id="sla-header" class="sla-header" data-code="{code}">
    <div class="sla-container">
      <div class="sla-title">Secure Link Archive</div>
      <div class="sla-meta">
        <span class="sla-code">Code: {code}</span>
      </div>
    </div>
  </header>

  <main class="sla-content">
    <pre class="sla-archived-text">{archived}</pre>
  </main>

  <script src="/api/header/script.js" defer></script>
</body>
</html>"""
    return HTMLResponse(content=html, status_code=200)
