from fastapi import HTTPException, Request
from .policy import PartnerPolicyProvider

def enforce_partner_access(provider: PartnerPolicyProvider):
    async def _dep(request: Request) -> None:
        partner = (request.headers.get("x-partner") or "").strip().lower()
        if not partner:
            raise HTTPException(status_code=401, detail="Missing partner identity")

        policy = provider.get(partner)
        route = request.scope.get("route")
        route_tags = set(getattr(route, "tags", []) or [])

        if not route_tags or not route_tags.intersection(set(policy.allow_tags)):
            raise HTTPException(status_code=403, detail="Partner not allowed")

    return _dep
