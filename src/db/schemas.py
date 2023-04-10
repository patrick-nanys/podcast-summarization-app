""" Schemas file for pydantic. """
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    id: UUID
    username: str = Field(min_length=4)
    email: EmailStr
    password: str
