from __future__ import annotations

from functools import lru_cache

from fastapi import HTTPException, status

from gateway.profiles.base import ApiProfile
from gateway.profiles.legacy import LegacyProfile
from gateway.profiles.standard import StandardProfile


class ProfileRegistry:
    def __init__(self):
        self._profiles: dict[str, ApiProfile] = {
            "standard": StandardProfile(),
            "legacy": LegacyProfile(),
        }

    def get(self, name: str) -> ApiProfile:
        profile = self._profiles.get(name)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown api_profile: {name}",
            )
        return profile


@lru_cache(maxsize=1)
def get_profile_registry() -> ProfileRegistry:
    return ProfileRegistry()
