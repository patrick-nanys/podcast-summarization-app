""" DB Models file for SQLAlchemy """
from sqlalchemy import Column, String, Integer, ForeignKey
from .uuid_gen import GUID
import uuid
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    """
    User model
    """

    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    podcasts = relationship("Podcast", back_populates="owner")


class Podcast(Base):
    """
    Podcast model
    """

    __tablename__ = "podcasts"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    filename = Column(String, nullable=False, index=True)
    owner_id = Column(GUID(), ForeignKey("users.id"))

    owner = relationship("User", back_populates="podcasts")
