import string
import random
import uuid
from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: str = Field(default=str(uuid.uuid4()), validate_default=True)
    name: str = Field(
        default="".join([random.choice(string.ascii_lowercase) for _ in range(200)]),
        validate_default=True,
    )
    password: str
    bio: str = Field(default="")
    archtype: str = Field(default="")


# TODO: add validation here
class UserRegisterRequest(BaseModel):
    user_id: str
    user_name: str
    user_password: str
    user_bio: str
    user_archtype: str


class UserLoginRequest(BaseModel):
    user_name: str
    user_password: str
