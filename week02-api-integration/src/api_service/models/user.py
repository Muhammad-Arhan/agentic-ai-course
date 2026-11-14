"""Data models (validation + the shape of our API's JSON)."""

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Request body for POST /users and PUT /users/{id}. Validated on input."""

    name: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=1, max_length=50)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class User(BaseModel):
    """What our API returns. We expose only the fields we care about."""

    id: int
    name: str
    username: str
    email: str
