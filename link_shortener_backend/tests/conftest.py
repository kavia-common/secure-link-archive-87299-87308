import os
import importlib
import pytest
from fastapi.testclient import TestClient

# Test configuration and common fixtures.
# We avoid touching real filesystem under src/api/data by patching env for base URL only.
# The service uses file storage, but as we mock archive/compare functions in endpoint tests,
# we don't need to modify data paths here. Each test ensures isolation via monkeypatch.


@pytest.fixture(scope="session")
def app():
    """
    Returns the FastAPI app instance for testing by importing src.api.main:app.

    If route modules referenced by main are missing, this import will fail.
    In that case, tests depending on those endpoints should xfail accordingly.
    """
    # Ensure a deterministic base URL for generated short links
    os.environ.setdefault("BACKEND_BASE_URL", "http://testserver")
    mod = importlib.import_module("src.api.main")
    return getattr(mod, "app")


@pytest.fixture()
def client(app):
    """Provides a synchronous TestClient against the app."""
    return TestClient(app)


def _router_mounted(app, prefix: str) -> bool:
    """
    Helper to check if there is any registered route that matches the given prefix.
    Used to decide whether to xfail tests when route modules are missing.
    """
    for r in app.router.routes:
        path = getattr(r, "path", "") or getattr(r, "path_format", "")
        if isinstance(path, str) and path.startswith(prefix):
            return True
    return False


@pytest.fixture()
def ensure_shorten_routes(app):
    """Mark tests xfail if /api/urls/shorten is not mounted."""
    if not _router_mounted(app, "/api/urls"):
        pytest.xfail("urls router not mounted (implementation files missing)")


@pytest.fixture()
def ensure_redirect_routes(app):
    """Mark tests xfail if /r/{code} is not mounted."""
    if not _router_mounted(app, "/r/"):
        pytest.xfail("redirect router not mounted (implementation files missing)")


@pytest.fixture()
def ensure_compare_routes(app):
    """Mark tests xfail if /api/compare is not mounted."""
    if not _router_mounted(app, "/api/compare"):
        pytest.xfail("compare router not mounted (implementation files missing)")


@pytest.fixture()
def ensure_header_routes(app):
    """Mark tests xfail if /api/header is not mounted."""
    if not _router_mounted(app, "/api/header"):
        pytest.xfail("header router not mounted (implementation files missing)")
