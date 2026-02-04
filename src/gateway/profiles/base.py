from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Type

from pydantic import BaseModel

from gateway.context.request_context import RequestContext


class ApiProfile(ABC):
    name: str

    @abstractmethod
    def lead_create_request_model(self) -> Type[BaseModel]:
        ...

    @abstractmethod
    def lead_create_response_model(self) -> Type[BaseModel]:
        ...

    @abstractmethod
    def map_lead_create_to_canonical(self, ctx: RequestContext, req: BaseModel) -> dict:
        ...

    @abstractmethod
    def shape_lead_create_response(self, ctx: RequestContext, domain_resp: dict) -> BaseModel:
        ...
