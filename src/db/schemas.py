""" Schemas file for pydantic. """
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


# Users schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=4)


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: UUID

    class Config:
        orm_mode = True  # needed for podcasts relationship


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
