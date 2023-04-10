""" DB Models file for SQLAlchemy """
from sqlalchemy import Column, String
from uuid_gen import GUID
import uuid
# from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    """
    User model
    """
    __tablename__ = "users"

    id = Column(GUID(), primare_key=True, index=True, default=lambda:str(uuid.uuid4()))
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    # podcasts = relationship("Podcast", back_populates="owner") # To check later
