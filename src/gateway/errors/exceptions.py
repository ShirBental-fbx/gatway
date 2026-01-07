from __future__ import annotations

from typing import Any, Optional

from .types import ErrorStruct


class FundboxAPIException(Exception):
    """
    Raised from routers/dependencies to produce a consistent Fundbox error response.
    """

    def __init__(
        self,
        error: ErrorStruct,
        *message_formatting: Any,
        detail: Optional[dict] = None,
    ):
        self.error = error
        self.message_formatting = message_formatting
        self.detail = detail
        super().__init__(error.message_format)
