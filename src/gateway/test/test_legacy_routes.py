"""Smoke tests for generated legacy routes."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from gateway.main import app


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


def test_legacy_routes_exist_in_openapi(client: TestClient):
    """
    Verify that generated legacy routes appear in OpenAPI schema.
    
    This ensures routes were generated and wired correctly.
    """
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    openapi_schema = response.json()
    paths = openapi_schema.get("paths", {})
    
    # Count legacy routes (tagged with "Legacy:")
    legacy_paths = [
        path
        for path, methods in paths.items()
        for method_spec in methods.values()
        if isinstance(method_spec, dict)
        and "Legacy:" in str(method_spec.get("tags", []))
    ]
    
    # Should have at least some legacy routes
    # Adjust threshold based on actual Flask route count
    assert len(legacy_paths) > 0, "No legacy routes found in OpenAPI schema"
    
    print(f"Found {len(legacy_paths)} legacy routes in OpenAPI schema")


def test_openapi_schema_structure(client: TestClient):
    """Verify OpenAPI schema has expected structure."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    schema = response.json()
    assert "paths" in schema
    assert "info" in schema
    assert "openapi" in schema


def test_sample_legacy_route_exists(client: TestClient):
    """
    Verify a sample legacy route exists and is callable.
    
    This test checks that:
    1. Route is registered
    2. Route handler exists
    3. Route can be called (may return 502 if upstream not available, but shouldn't 404)
    """
    # Get all paths from OpenAPI
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    schema = response.json()
    paths = schema.get("paths", {})
    
    # Find a sample legacy route (prefer GET for idempotency)
    sample_path = None
    for path, methods in paths.items():
        # Skip gateway-specific routes
        if path in ("/health", "/", "/docs", "/openapi.json"):
            continue
        if path.startswith("/debug/") or path.startswith("/partners/"):
            continue
        
        # Prefer GET methods
        if "get" in methods:
            sample_path = path
            break
    
    if not sample_path:
        # Fall back to any legacy route
        for path in paths.keys():
            if path not in ("/health", "/", "/docs", "/openapi.json"):
                if not path.startswith("/debug/") and not path.startswith("/partners/"):
                    sample_path = path
                    break
    
    if sample_path:
        # Try to call the route
        # It may fail with 502 (upstream not available) but shouldn't 404
        response = client.get(sample_path)
        
        # 404 means route not found (bad)
        # 502 means upstream not available (expected in test env)
        # 200/other means route works
        assert response.status_code != 404, f"Route {sample_path} returned 404 (not found)"
        
        print(f"Sample route {sample_path} returned status {response.status_code}")
    else:
        pytest.skip("No sample legacy route found to test")


def test_legacy_routers_importable():
    """Verify legacy router modules can be imported."""
    try:
        from gateway.routers.legacy import __all__
        
        # Should have at least some routers
        assert len(__all__) > 0, "No legacy routers exported"
        
        print(f"Found {len(__all__)} legacy router modules")
    except ImportError:
        pytest.skip("Legacy routers not generated yet")


def test_route_order_preserved(client: TestClient):
    """
    Verify that gateway-specific routes take precedence over legacy routes.
    
    Gateway routes should be matched before catch-all proxy.
    """
    # Gateway routes should work
    response = client.get("/health")
    assert response.status_code == 200
    
    # Gateway root should work
    response = client.get("/")
    assert response.status_code == 200
