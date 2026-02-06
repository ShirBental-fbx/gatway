from __future__ import annotations
from typing import Dict, Optional
from .policy import PartnerPolicy, PartnerPolicyProvider

class InMemoryPolicyProvider(PartnerPolicyProvider):
    def __init__(self, policies: Dict[str, PartnerPolicy], default: Optional[PartnerPolicy] = None):
        super().__init__(policies)
        self._policies = {k.lower(): v for k, v in policies.items()}
        self._default = default

    def get(self, partner: str) -> PartnerPolicy:
        key = (partner or "").lower()
        return self._policies.get(key) or self._default or PartnerPolicy(partner=key, allow_tags=frozenset())
