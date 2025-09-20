from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import urls, compare, redirect, header

def create_app() -> FastAPI:
    """
    Factory to create and configure the FastAPI application with metadata and routes.
    """
    app = FastAPI(
        title="Secure Link Archive",
        description=(
            "A headless service to securely shorten URLs, archive the original page, "
            "and provide redirect endpoints with a floating header that highlights changes "
            "since archival."
        ),
        version="1.0.0",
        contact={"name": "Secure Link Archive", "url": "https://example.com"},
        openapi_tags=[
            {"name": "health", "description": "Service health and diagnostics."},
            {"name": "shorten", "description": "Create shortened links and manage archives."},
            {"name": "redirect", "description": "Resolve short codes and serve archived content with header."},
            {"name": "compare", "description": "Compare current vs archived content."},
            {"name": "header", "description": "Floating header script and styles."},
        ],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(urls.router)
    app.include_router(redirect.router)
    app.include_router(compare.router)
    app.include_router(header.router)

    @app.get("/", tags=["health"], summary="Health Check")
    def health_check():
        """Simple health check endpoint."""
        return {"message": "Healthy"}

    return app


app = create_app()
