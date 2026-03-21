"""Integration test: verify all routers are registered with correct prefixes."""

from fastapi import APIRouter

from src.main import app
from src import security, vision
from src.routers import collection


def _route_paths() -> list[str]:
    """Extract all route paths from the FastAPI app."""
    return [route.path for route in app.routes]


def test_health_route_registered():
    paths = _route_paths()
    assert "/health" in paths


def test_auth_router_exists():
    """security.py exports an APIRouter with prefix /auth."""
    assert isinstance(security.router, APIRouter)
    assert security.router.prefix == "/auth"


def test_scan_router_exists():
    """vision.py exports an APIRouter with prefix /scan."""
    assert isinstance(vision.router, APIRouter)
    assert vision.router.prefix == "/scan"


def test_collection_router_exists():
    """routers/collection.py exports an APIRouter with prefix /cards."""
    assert isinstance(collection.router, APIRouter)
    assert collection.router.prefix == "/cards"


def test_card_crud_routes_present():
    """Verify the specific CRUD routes for /cards/ are all registered."""
    paths = _route_paths()
    expected = ["/cards/", "/cards/sync", "/cards/{card_id}"]
    for route in expected:
        assert route in paths, f"Expected route {route} not found in {paths}"
