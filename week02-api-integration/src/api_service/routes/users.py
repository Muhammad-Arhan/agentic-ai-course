"""User routes: Client -> Route -> Service -> External API.

A route only handles HTTP concerns (paths, methods, status codes, validation).
The real work is delegated to UserService.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Response, status

from api_service.clients.external_api import ExternalApiClient
from api_service.models.user import User, UserCreate
from api_service.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service() -> UserService:
    """Dependency: build the service. Tests replace this with a fake."""
    return UserService(ExternalApiClient())


ServiceDep = Annotated[UserService, Depends(get_user_service)]
UserId = Annotated[int, Path(ge=1, description="Numeric user id")]


@router.get("", response_model=list[User])
def list_users(service: ServiceDep):
    """Retrieve all users."""
    return service.list_users()


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, service: ServiceDep):
    """Create a user."""
    return service.create_user(data)


@router.get("/{user_id}", response_model=User)
def get_user(user_id: UserId, service: ServiceDep):
    """Retrieve one user by id."""
    return service.get_user(user_id)


@router.put("/{user_id}", response_model=User)
def update_user(user_id: UserId, data: UserCreate, service: ServiceDep):
    """Update (replace) a user."""
    return service.update_user(user_id, data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UserId, service: ServiceDep):
    """Delete a user."""
    service.delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
