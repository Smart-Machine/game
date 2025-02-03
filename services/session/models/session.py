import uuid
from pydantic import BaseModel, Field, computed_field


class SessionRequest(BaseModel):
    session_id: str


class Session(BaseModel):
    session_id: str = Field(default=str(uuid.uuid4()), validate_default=True)
    created_at: float = Field(default=0, validate_default=True)
    deleted_at: float = Field(default=0, validate_default=True)
    allowed_users: list = Field(default_factory=list)
    active_users: list = Field(default_factory=list)

    @computed_field
    @property
    def duration(self) -> float:
        return self.deleted_at - self.created_at
