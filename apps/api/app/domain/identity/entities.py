"""Identity domain entities."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AuthenticatedUser:
    """Verified external identity mapped into RepoMind AI domain language."""

    provider_subject: str
    email: str
    role: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
