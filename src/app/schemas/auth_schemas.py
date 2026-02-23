from pydantic import BaseModel


class UserProfile(BaseModel):
    user_id: str
    user_email: str
