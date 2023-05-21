"""DB Schema for podcast storing"""
from pydantic import BaseModel

class Podcast(BaseModel):
    id: int
    link: str
    class Config:
        orm_mode = True
