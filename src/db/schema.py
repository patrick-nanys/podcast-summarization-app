"""DB Schema for podcast storing"""
from pydantic import BaseModel

class PodcastBase(BaseModel):
    id: int
    link: str

class AddPodcast(PodcastBase):
    pass

    class Config:
        orm_mode = True
