"""Request/response shapes used by the FastAPI service."""

from pydantic import BaseModel, Field


class TicketSearchRequest(BaseModel):
    """The issue text an agent wants to search for."""
    ticket_id: str | None = None
    subject: str = Field(min_length=1, description="Short title of the new issue")
    description: str = Field(min_length=1, description="What the customer reported")
    limit: int = Field(default=3, ge=1, le=10)
    threshold: float = Field(default=0.08, ge=0.0, le=1.0)
