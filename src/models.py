""" DB Models file for SQLAlchemy """
from sqlalchemy import Column, Integer, String
# from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    """
    User model
    """
    __tablename__ = "users"

    id = Column(Integer, primare_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    # podcasts = relationship("Podcast", back_populates="owner") # To check later
