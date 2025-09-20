# Secure Link Archive - Backend (FastAPI)

Headless service to:
- Shorten submitted URLs and archive the original page
- Serve archived content with a floating header
- Detect and report changes between archived and current content
- Provide header script and stylesheet for frontend injection

Run locally:
- Install: `pip install -r requirements.txt`
- Start: `uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000`
- Docs: http://localhost:8000/docs

Environment variables:
- BACKEND_BASE_URL: Base URL used when generating `short_url` (e.g., `https://api.example.com`). This should match the externally reachable backend URL.

API Overview:
- POST /api/urls/shorten: { url, note? } -> returns { id, code, short_url, original_url, archived_at }
- GET /r/{code}: serves archived content with floating header (HTML)
- GET /api/compare/{code}: returns diff summary
- GET /api/header/style.css and /api/header/script.js: assets for header

Security considerations:
- Only http/https URLs allowed
- Localhost/link-local targets blocked
- Content size capped for archiving
- Safe user agent and limited timeouts
- No direct proxying of external content on redirect; archived normalized text is served

Storage:
- File-based storage under `src/data/`:
  - Archives: `src/data/archives/{code}.txt`
  - Index: `src/data/index.json`

Style Guide:
- Ocean Professional: blue (#2563EB) and amber (#F59E0B) accents, clean, minimalist.
