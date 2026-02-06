import os
from functools import lru_cache
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.openapi.docs import get_swagger_ui_html

from .openapi import build_base_openapi, filter_openapi_for_partner
from .policy import PartnerPolicyProvider

router = APIRouter()


def mount_partner_docs(app: FastAPI, provider: PartnerPolicyProvider) -> None:
    """
    Mounts partner-specific OpenAPI + Swagger UI routes onto the app.
    """

    base_spec = build_base_openapi(app)

    @lru_cache(maxsize=256)
    def _partner_spec(partner: str, app_version: str):
        policy = provider.get(partner)
        return filter_openapi_for_partner(base_spec, policy)

    @router.get("/partners/{partner}/openapi.json", include_in_schema=False)
    def partner_openapi(partner: str):
        spec = _partner_spec(partner, app.version)
        if not spec.get("paths"):
            raise HTTPException(status_code=404, detail="No OpenAPI spec for this partner")
        return spec

    @router.get("/partners/{partner}/docs", include_in_schema=False)
    def partner_docs(partner: str):
        return get_swagger_ui_html(
                openapi_url="openapi.json",
                title=f"{partner} API Docs",
                swagger_ui_parameters={
                    "persistAuthorization": True,
                    "docExpansion": "none",
                    "defaultModelsExpandDepth": -1,
                },
        )

    app.include_router(router)
