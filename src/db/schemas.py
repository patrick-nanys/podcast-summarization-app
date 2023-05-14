""" Schemas file for pydantic. """
from uuid import UUID
from pydantic import BaseModel
from authx.models import user


# Users schemas
class register(user.UserInRegister):
    first_name: str
    last_name: str


class login(user.UserInLogin):
    pass


class user_update_username(user.UserInChangeUsername):
    pass


class user_update_password(user.UserInChangePassword):
    pass


# Podcasts schemas
class PodcastBase(BaseModel):
    filename: str


class PodcastCreate(PodcastBase):
    pass


class Podcast(PodcastBase):
    id: int
    owner_id: UUID

    class Config:
        orm_mode = True
