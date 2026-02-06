#!/usr/bin/env python3
"""
Export Flask routes from runtime url_map.

This script imports the Flask app from the legacy service and extracts
all registered routes, outputting them in both JSON and readable text formats.

Usage:
    # Set required environment variables first
    export API_FLASK_SESSION_SECRET_KEY=...
    export API_OAUTH_ENFORCE_SSL=false
    export API_SQLALCHEMY_DATABASE_URI=...
    
    # Run the export
    python legacy/scripts/export_routes.py
    
    # Outputs:
    # - artifacts/flask_routes.json (machine-readable)
    # - artifacts/flask_routes.txt (human-readable table)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

# Try to use the new dump_routes.py script from the legacy Flask project if available
# Otherwise fall back to direct import (for backward compatibility)

LEGACY_API_ROOT = Path(__file__).parent.parent.parent.parent.parent / "PycharmProjects" / "api"
DUMP_SCRIPT = LEGACY_API_ROOT / "utils" / "dump_routes.py"

USE_DUMP_SCRIPT = False
routes_from_dump = None

if DUMP_SCRIPT.exists():
    # Use the new dump script approach
    import subprocess
    import json as json_module
    
    print(f"Using dump_routes.py from legacy project: {DUMP_SCRIPT}", file=sys.stderr)
    
    # Run the dump script
    env = os.environ.copy()
    env['DUMP_ROUTES_ONLY'] = '1'
    env['PYTHONPATH'] = str(LEGACY_API_ROOT / 'src')
    
    try:
        result = subprocess.run(
            [sys.executable, str(DUMP_SCRIPT)],
            env=env,
            capture_output=True,
            text=True,
            cwd=str(LEGACY_API_ROOT),
        )
        
        if result.returncode == 0:
            # Parse JSON output
            routes_data = json_module.loads(result.stdout)
            routes_from_dump = routes_data.get("routes", [])
            
            # Convert to our format (add blueprint extraction)
            for route in routes_from_dump:
                endpoint_parts = route["endpoint"].split(".")
                if len(endpoint_parts) > 1:
                    route["blueprint"] = endpoint_parts[0]
                else:
                    route["blueprint"] = None
                
                # Docstring not available from dump script
                route["docstring"] = None
            
            USE_DUMP_SCRIPT = True
        else:
            print(f"WARNING: dump_routes.py failed:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            print(f"Falling back to direct import method...", file=sys.stderr)
    except Exception as e:
        print(f"WARNING: Failed to use dump_routes.py: {e}", file=sys.stderr)
        print(f"Falling back to direct import method...", file=sys.stderr)

# Fallback: Direct import method (for backward compatibility)
if not USE_DUMP_SCRIPT:
    # Add legacy Flask app to path
    LEGACY_SRC = Path(__file__).parent.parent.parent.parent / "api__backup_20260114_1349" / "src"
    if str(LEGACY_SRC) not in sys.path:
        sys.path.insert(0, str(LEGACY_SRC))
    
    # Set minimal environment variables if not set (for route extraction only)
    os.environ.setdefault("DUMP_ROUTES_ONLY", "1")
    os.environ.setdefault("API_FLASK_SESSION_SECRET_KEY", "dummy-secret-for-route-export")
    os.environ.setdefault("API_OAUTH_ENFORCE_SSL", "false")
    os.environ.setdefault("API_SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
    
    # Import Flask app (this will trigger route registration)
    try:
        from App import app
    except Exception as e:
        print(f"ERROR: Failed to import Flask app: {e}", file=sys.stderr)
        print(f"Make sure the legacy Flask service is accessible", file=sys.stderr)
        print(f"\nTroubleshooting:", file=sys.stderr)
        print(f"  1. Use the new dump_routes.py script: {DUMP_SCRIPT}", file=sys.stderr)
        print(f"  2. Or ensure Flask app dependencies are installed", file=sys.stderr)
        print(f"  3. Set DUMP_ROUTES_ONLY=1 to skip external dependencies", file=sys.stderr)
        sys.exit(1)


def extract_routes() -> list[dict[str, Any]]:
    """
    Extract all routes from Flask app's url_map.
    
    Returns:
        List of route dictionaries with path, methods, endpoint, blueprint info
    """
    # If we got routes from dump script, return them
    if USE_DUMP_SCRIPT and routes_from_dump:
        return routes_from_dump
    
    # Otherwise extract from Flask app
    routes = []
    
    for rule in app.url_map.iter_rules():
        # Skip static files
        if rule.endpoint == "static":
            continue
        
        # Get methods (exclude HEAD/OPTIONS unless explicitly defined)
        methods = [m for m in rule.methods if m not in ("HEAD", "OPTIONS")]
        if not methods:
            # If only HEAD/OPTIONS, include them
            methods = list(rule.methods)
        
        # Extract blueprint name if present
        blueprint_name = None
        endpoint_parts = rule.endpoint.split(".")
        if len(endpoint_parts) > 1:
            # Flask-RESTful resources use format "blueprint.resource_method"
            # Regular routes use format "blueprint.function_name"
            blueprint_name = endpoint_parts[0]
        
        # Try to get docstring from view function
        docstring = None
        try:
            view_func = app.view_functions.get(rule.endpoint)
            if view_func and hasattr(view_func, "__doc__"):
                docstring = view_func.__doc__
                if docstring:
                    # Clean up docstring (first line only for brevity)
                    docstring = docstring.strip().split("\n")[0]
        except Exception:
            pass
        
        route_info = {
            "path": rule.rule,
            "methods": sorted(methods),
            "endpoint": rule.endpoint,
            "blueprint": blueprint_name,
            "docstring": docstring,
        }
        
        routes.append(route_info)
    
    # Sort by path for consistency
    routes.sort(key=lambda r: (r["path"], r["methods"]))
    
    return routes


def print_routes_table(routes: list[dict[str, Any]]) -> str:
    """Generate a human-readable table of routes."""
    lines = []
    lines.append("=" * 100)
    lines.append("Flask Routes Inventory")
    lines.append("=" * 100)
    lines.append("")
    
    # Group by blueprint for readability
    by_blueprint: dict[str | None, list[dict[str, Any]]] = {}
    for route in routes:
        bp = route["blueprint"]
        if bp not in by_blueprint:
            by_blueprint[bp] = []
        by_blueprint[bp].append(route)
    
    for blueprint in sorted(by_blueprint.keys(), key=lambda x: x or ""):
        if blueprint:
            lines.append(f"\n[{blueprint}]")
            lines.append("-" * 100)
        
        for route in by_blueprint[blueprint]:
            methods_str = ", ".join(route["methods"])
            path = route["path"]
            endpoint = route["endpoint"]
            doc = route["docstring"] or ""
            
            lines.append(f"  {methods_str:20} {path:40} {endpoint}")
            if doc:
                lines.append(f"    {doc}")
    
    lines.append("")
    lines.append("=" * 100)
    lines.append(f"Total routes: {len(routes)}")
    lines.append("=" * 100)
    
    return "\n".join(lines)


def main():
    """Main entry point."""
    print("Extracting routes from Flask app...", file=sys.stderr)
    
    routes = extract_routes()
    
    if not routes:
        print("WARNING: No routes found. Check Flask app initialization.", file=sys.stderr)
        sys.exit(1)
    
    # Create artifacts directory
    artifacts_dir = Path(__file__).parent.parent.parent / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    
    # Write JSON output
    json_path = artifacts_dir / "flask_routes.json"
    with open(json_path, "w") as f:
        json.dump(routes, f, indent=2)
    print(f"✓ Wrote {len(routes)} routes to {json_path}", file=sys.stderr)
    
    # Write text table
    txt_path = artifacts_dir / "flask_routes.txt"
    table = print_routes_table(routes)
    with open(txt_path, "w") as f:
        f.write(table)
    print(f"✓ Wrote route table to {txt_path}", file=sys.stderr)
    
    # Print summary to stdout
    print(f"\nExtracted {len(routes)} routes")
    print(f"JSON: {json_path}")
    print(f"Table: {txt_path}")


if __name__ == "__main__":
    main()
