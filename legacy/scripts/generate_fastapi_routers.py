#!/usr/bin/env python3
"""
Generate FastAPI router skeletons from Flask route inventory.

This script reads artifacts/flask_routes.json and generates FastAPI routers
grouped by blueprint or path segment, with proxy-only handlers.

Usage:
    python legacy/scripts/generate_fastapi_routers.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# Gateway-specific routes that should not be generated
GATEWAY_RESERVED_ROUTES = {
    "/health",
    "/",
    "/docs",
    "/openapi.json",
}

GATEWAY_RESERVED_PREFIXES = [
    "/debug/",
    "/partners/",
]


def normalize_path(path: str) -> str:
    """
    Normalize Flask path to FastAPI path format.
    
    Flask uses <converter:name> syntax, FastAPI uses {name:type} syntax.
    """
    # Flask to FastAPI converter mapping
    converters = {
        "string": "str",
        "int": "int",
        "float": "float",
        "path": "path",
    }
    
    # Replace Flask converters with FastAPI format
    # Flask: <string:name> -> FastAPI: {name:str}
    pattern = r"<(?P<converter>\w+):(?P<name>\w+)>"
    
    def replace(match: re.Match[str]) -> str:
        converter = match.group("converter")
        name = match.group("name")
        fastapi_type = converters.get(converter, "str")
        return f"{{{name}:{fastapi_type}}}"
    
    normalized = re.sub(pattern, replace, path)
    
    # Also handle Flask's <name> (defaults to string)
    normalized = re.sub(r"<(\w+)>", r"{\1:str}", normalized)
    
    return normalized


def get_router_group_name(route: dict[str, Any]) -> str:
    """
    Determine router group name for a route.
    
    Groups by blueprint if available, otherwise by first path segment.
    """
    if route.get("blueprint"):
        return route["blueprint"]
    
    # Extract first path segment
    path = route["path"].strip("/")
    if not path:
        return "root"
    
    first_segment = path.split("/")[0]
    # Sanitize for Python module name
    first_segment = re.sub(r"[^a-zA-Z0-9_]", "_", first_segment)
    return first_segment or "root"


def is_reserved_route(path: str) -> bool:
    """Check if a route conflicts with gateway-specific endpoints."""
    if path in GATEWAY_RESERVED_ROUTES:
        return True
    
    for prefix in GATEWAY_RESERVED_PREFIXES:
        if path.startswith(prefix):
            return True
    
    return False


def generate_route_handler(route: dict[str, Any]) -> str:
    """
    Generate FastAPI route handler code for a Flask route.
    
    Returns Python code as string.
    """
    path = normalize_path(route["path"])
    methods = route["methods"]
    endpoint = route["endpoint"]
    docstring = route.get("docstring") or ""
    
    # Generate handler function name from endpoint
    handler_name = endpoint.replace(".", "_").replace("-", "_")
    # Ensure valid Python identifier
    handler_name = re.sub(r"[^a-zA-Z0-9_]", "_", handler_name)
    if handler_name[0].isdigit():
        handler_name = f"route_{handler_name}"
    
    # Generate decorator with methods
    decorator_lines = []
    for method in methods:
        decorator_lines.append(f'@router.{method.lower()}("{path}")')
    
    # Use first decorator (FastAPI allows multiple methods on same handler)
    decorator = decorator_lines[0]
    
    # Generate handler code with summary for better Swagger UI visibility
    summary = endpoint.replace("_", " ").replace("/", " ").title()
    if len(summary) > 50:
        summary = summary[:47] + "..."
    
    handler_code = f'''{decorator}
async def {handler_name}(request: Request) -> Response:
    """
    Proxy handler for Flask endpoint: {endpoint}
    Original path: {route["path"]}
    Methods: {", ".join(methods)}
    {f"Docstring: {docstring}" if docstring else ""}
    """
    return await proxy_to_upstream(request, upstream_path="{route["path"]}")'''
    
    return handler_code


def generate_router_module(group_name: str, routes: list[dict[str, Any]]) -> str:
    """
    Generate a complete FastAPI router module for a route group.
    
    Returns Python code as string.
    """
    # Sanitize group name for module name
    module_name = re.sub(r"[^a-zA-Z0-9_]", "_", group_name)
    
    # Generate imports
    imports = '''"""Auto-generated FastAPI router for Flask route group: {group_name}

This module contains contract-first route definitions that proxy to the legacy Flask service.
Routes are grouped by blueprint or path segment.

Generated from: artifacts/flask_routes.json
DO NOT EDIT MANUALLY - Regenerate using: python legacy/scripts/generate_fastapi_routers.py
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from starlette.responses import Response

from gateway.proxy.endpoint import proxy_to_upstream
'''.format(group_name=group_name)
    
    # Generate router initialization
    router_init = f'''
router = APIRouter(tags=["Legacy: {group_name}"])
'''
    
    # Generate route handlers
    handlers = []
    for route in routes:
        handlers.append(generate_route_handler(route))
    
    # Combine all parts
    module_code = imports + router_init + "\n\n".join(handlers) + "\n"
    
    return module_code, module_name


def main():
    """Main entry point."""
    # Read Flask routes inventory
    artifacts_dir = Path(__file__).parent.parent.parent / "artifacts"
    json_path = artifacts_dir / "flask_routes.json"
    
    if not json_path.exists():
        print(f"ERROR: Flask routes inventory not found: {json_path}", file=sys.stderr)
        print("Run: python legacy/scripts/export_routes.py first", file=sys.stderr)
        sys.exit(1)
    
    with open(json_path) as f:
        data = json.load(f)
    
    # Handle both formats: {"routes": [...]} and [...]
    if isinstance(data, dict) and "routes" in data:
        routes = data["routes"]
    elif isinstance(data, list):
        routes = data
    else:
        print(f"ERROR: Invalid JSON format. Expected {{'routes': [...]}} or [...], got {type(data)}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Loaded {len(routes)} routes from {json_path}", file=sys.stderr)
    
    # Group routes by router group
    route_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    collisions = []
    
    for route in routes:
        path = route["path"]
        
        # Check for collisions with gateway routes
        if is_reserved_route(path):
            collisions.append(path)
            continue
        
        group_name = get_router_group_name(route)
        route_groups[group_name].append(route)
    
    if collisions:
        print(f"\nWARNING: Skipped {len(collisions)} routes that collide with gateway endpoints:", file=sys.stderr)
        for path in sorted(collisions):
            print(f"  - {path}", file=sys.stderr)
    
    # Generate router modules
    routers_dir = Path(__file__).parent.parent.parent / "src" / "gateway" / "routers" / "legacy"
    routers_dir.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py that imports all routers
    init_imports = ['"""Auto-generated legacy routers module.\n\nDO NOT EDIT MANUALLY - Regenerate using: python legacy/scripts/generate_fastapi_routers.py\n"""\n\nfrom __future__ import annotations\n\n']
    
    generated_modules = []
    
    for group_name, group_routes in sorted(route_groups.items()):
        module_code, module_name = generate_router_module(group_name, group_routes)
        
        module_path = routers_dir / f"{module_name}.py"
        with open(module_path, "w") as f:
            f.write(module_code)
        
        print(f"✓ Generated {module_path} ({len(group_routes)} routes)", file=sys.stderr)
        
        # Add to __init__.py imports
        init_imports.append(f"from gateway.routers.legacy.{module_name} import router as {module_name}_router\n")
        generated_modules.append(module_name)
    
    # Write __init__.py
    init_code = "".join(init_imports) + "\n"
    init_code += "# Export all routers for easy importing\n"
    init_code += "__all__ = [\n"
    for module_name in generated_modules:
        init_code += f'    "{module_name}_router",\n'
    init_code += "]\n\n"
    init_code += "# List of all router instances for bulk inclusion\n"
    init_code += "all_routers = [\n"
    for module_name in generated_modules:
        init_code += f"    {module_name}_router,\n"
    init_code += "]\n"
    
    init_path = routers_dir / "__init__.py"
    with open(init_path, "w") as f:
        f.write(init_code)
    
    print(f"\n✓ Generated {len(route_groups)} router modules", file=sys.stderr)
    print(f"✓ Total routes: {sum(len(routes) for routes in route_groups.values())}", file=sys.stderr)
    print(f"\nNext steps:", file=sys.stderr)
    print(f"  1. Review generated routers in: {routers_dir}", file=sys.stderr)
    print(f"  2. Import and include routers in src/gateway/main.py", file=sys.stderr)


if __name__ == "__main__":
    main()
