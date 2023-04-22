""" Schemas file for pydantic. """
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=4)

class UserCreate(UserBase):
    password: str
    
class User(UserBase):
    id: UUID

    class Config:
        orm_mode = True # needed for podcasts relationship
