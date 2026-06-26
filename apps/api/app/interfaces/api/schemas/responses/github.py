"""GitHub response DTOs."""

from typing import Literal

from pydantic import BaseModel


class GitHubTokenDebugResponse(BaseModel):
    """Safe GitHub token availability debug payload."""

    github_linked: bool
    token_available: bool
    provider: Literal["github"] = "github"