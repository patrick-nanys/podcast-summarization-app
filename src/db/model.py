"""DB Model for podcast storing"""
from sqlalchemy import Column, String, Integer
from .database import Base

class Podcast(Base):
    """Podcast model"""
    __tablename__ = "podcasts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    link = Column(String(255), nullable=False)