"""DB Model for podcast storing"""
from sqlalchemy import Column, String, Integer
from .database import Base

class Podcast(Base):
    """Podcast model"""
    __tablename__ = "podcasts"
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    link = Column(String, primary_key=True, nullable=False)
