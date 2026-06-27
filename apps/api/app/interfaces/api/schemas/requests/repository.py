"""Repository request DTOs."""

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class RegisterRepositoryRequest(BaseModel):
    """Request payload for registering a discovered GitHub repository."""

    github_repository_id: str = Field(min_length=1, max_length=255)
    full_name: str = Field(min_length=3, max_length=511, pattern=r"^[^/]+/[^/]+$")
    default_branch: str = Field(min_length=1, max_length=255)


class UpdateRepositorySettingsRequest(BaseModel):
    """Request payload for mutable repository settings."""

    display_name: str | None = Field(default=None, max_length=255)
    favorite: bool | None = None
    notes: str | None = Field(default=None, max_length=1000)

    @field_validator("display_name", "notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        """Store blank optional text as null."""

        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def require_at_least_one_setting(self) -> "UpdateRepositorySettingsRequest":
        """Reject empty PATCH payloads."""

        if not self.model_fields_set:
            raise ValueError("At least one repository setting must be provided.")
        return self

    def to_update_values(self, *, unset: Any) -> dict[str, Any]:
        """Return provided fields while preserving explicit null values."""

        return {
            "display_name": self.display_name if "display_name" in self.model_fields_set else unset,
            "favorite": self.favorite if "favorite" in self.model_fields_set else unset,
            "notes": self.notes if "notes" in self.model_fields_set else unset,
        }