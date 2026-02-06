from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, Optional


@dataclass(frozen=True)
class PartnerPolicy:
    partner: str
    allow_tags: FrozenSet[str]


class PartnerPolicyProvider:
    """
    MVP store.
    Later: load from YAML/DB/Parameter Store.
    """
    def __init__(self, policies: Dict[str, PartnerPolicy], default_policy: Optional[PartnerPolicy] = None):
        self._policies = policies
        self._default = default_policy

    def get(self, partner: str) -> PartnerPolicy:
        if partner in self._policies:
            return self._policies[partner]
        if self._default:
            return self._default
        # choose strict default
        return PartnerPolicy(partner=partner, allow_tags=frozenset())
