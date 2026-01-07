from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ErrorStruct:
    http_status_code: int
    error_code: int
    message_format: str
    quiet: bool = False

    def format_message(self, *args: Any) -> str:
        return self.message_format.format(*args)
