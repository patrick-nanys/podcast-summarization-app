""" DB Models file for SQLAlchemy """
from sqlalchemy import Column, String
from .uuid_gen import GUID
import uuid
# from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    """
    User model
    """
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, nullable=False, index=True, default=lambda:str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    encrypted_password = Column(String, nullable=False)
    # podcasts = relationship("Podcast", back_populates="owner") # To check later
