"""Business logic for users.

The service decides WHAT to ask the external API and converts its raw JSON into
our own `User` model. It knows nothing about FastAPI or HTTP status codes of
our own API: that is the job of the routes.
"""

from pydantic import ValidationError

from api_service.clients.external_api import InvalidResponseError
from api_service.models.user import User, UserCreate


class UserService:
    def __init__(self, client):
        self.client = client

    def list_users(self):
        payload = self.client.get("/users")
        if not isinstance(payload, list):
            raise InvalidResponseError("Expected a list of users from the external API.")
        return [self._to_user(item) for item in payload]

    def get_user(self, user_id):
        return self._to_user(self.client.get(f"/users/{user_id}"))

    def create_user(self, data: UserCreate):
        return self._to_user(self.client.post("/users", json=data.model_dump()))

    def update_user(self, user_id, data: UserCreate):
        return self._to_user(self.client.put(f"/users/{user_id}", json=data.model_dump()))

    def delete_user(self, user_id):
        self.client.delete(f"/users/{user_id}")

    @staticmethod
    def _to_user(payload):
        """Convert the external API's JSON (a dict) to our User model."""
        try:
            return User.model_validate(payload)
        except ValidationError as exc:
            raise InvalidResponseError(
                "The external API returned user data in an unexpected format."
            ) from exc
