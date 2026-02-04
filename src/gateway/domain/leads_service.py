from __future__ import annotations


class LeadsService:
    async def create_lead(self, canonical: dict) -> dict:
        return {"lead_id": "ld_123", "status": "created"}
