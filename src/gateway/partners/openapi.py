from __future__ import annotations

import copy
from typing import Any, Dict

from fastapi.openapi.utils import get_openapi

from .policy import PartnerPolicy


def build_base_openapi(app) -> Dict[str, Any]:
    """
    Build the full OpenAPI spec for the app (unsliced).
    """
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )


def filter_openapi_for_partner(
    base_spec: Dict[str, Any],
    policy: PartnerPolicy,
) -> Dict[str, Any]:
    """
    Return a partner-specific OpenAPI spec filtered by allowed tags.
    """
    spec = copy.deepcopy(base_spec)

    allowed_tags = set(policy.allow_tags)
    paths = spec.get("paths", {})

    filtered_paths: Dict[str, Any] = {}

    for path, methods in paths.items():
        filtered_methods: Dict[str, Any] = {}

        for method, operation in methods.items():
            op_tags = set(operation.get("tags", []))

            # No tags = internal endpoint → hide
            if not op_tags:
                continue

            if op_tags & allowed_tags:
                filtered_methods[method] = operation

        if filtered_methods:
            filtered_paths[path] = filtered_methods

    spec["paths"] = filtered_paths

    # Keep only relevant tags in the tag list
    if "tags" in spec:
        spec["tags"] = [
            t for t in spec.get("tags", [])
            if t.get("name") in allowed_tags
        ]

    # Optional metadata
    spec.setdefault("info", {})["x-partner"] = policy.partner

    return spec
