from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/api/header", tags=["header"])


# PUBLIC_INTERFACE
@router.get(
    "/style.css",
    summary="Floating header stylesheet",
    response_class=PlainTextResponse,
    responses={200: {"description": "CSS stylesheet"}},
)
def header_style() -> Response:
    """
    Returns CSS for the floating header injected on archived pages.
    """
    css = """
/* Secure Link Archive Floating Header */
:root {
  --sla-primary: #2563EB;
  --sla-accent: #F59E0B;
  --sla-bg: #ffffff;
  --sla-shadow: rgba(0,0,0,0.08);
}
.sla-header {
  position: sticky;
  top: 0;
  z-index: 9999;
  background: var(--sla-bg);
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 2px 8px var(--sla-shadow);
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Arial, "Apple Color Emoji", "Segoe UI Emoji";
}
.sla-container {
  max-width: 1080px;
  margin: 0 auto;
  padding: 10px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.sla-title {
  color: var(--sla-primary);
  font-weight: 700;
}
.sla-meta {
  color: #374151;
  font-size: 0.9rem;
}
.sla-content {
  padding: 16px;
}
.sla-archived-text {
  white-space: pre-wrap;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 12px;
}
"""
    return PlainTextResponse(content=css.strip(), media_type="text/css")


# PUBLIC_INTERFACE
@router.get(
    "/script.js",
    summary="Floating header script",
    response_class=PlainTextResponse,
    responses={200: {"description": "JavaScript content"}},
)
def header_script() -> Response:
    """
    Returns JavaScript for initializing the floating header and optionally
    fetching compare results for the current code to show change indicators.
    """
    js = """
/* Secure Link Archive Header Script */
(function () {
  function ready(fn){ if(document.readyState !== 'loading'){ fn(); } else { document.addEventListener('DOMContentLoaded', fn); } }

  function renderChangeBadge(changed){
    var meta = document.querySelector('#sla-header .sla-meta');
    if(!meta) return;
    var badge = document.createElement('span');
    badge.style.marginLeft = '8px';
    badge.style.padding = '2px 8px';
    badge.style.borderRadius = '9999px';
    badge.style.fontSize = '0.8rem';
    badge.style.color = '#fff';
    badge.style.background = changed ? '#F59E0B' : '#10B981';
    badge.textContent = changed ? 'Changes detected' : 'No changes';
    meta.appendChild(badge);
  }

  function fetchCompare(code){
    if(!code) return;
    fetch('/api/compare/' + encodeURIComponent(code), { method: 'GET' })
      .then(function(r){ return r.json(); })
      .then(function(data){
        if (typeof data.has_changes !== 'undefined') {
          renderChangeBadge(!!data.has_changes);
        } else {
          renderChangeBadge(false);
        }
      })
      .catch(function(){ renderChangeBadge(false); });
  }

  ready(function(){
    var header = document.getElementById('sla-header');
    var code = header ? header.getAttribute('data-code') : null;
    fetchCompare(code);
  });
})();
"""
    # application/javascript or text/javascript are both acceptable in tests
    return PlainTextResponse(content=js.strip(), media_type="application/javascript")
