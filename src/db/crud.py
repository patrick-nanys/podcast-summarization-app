""" Users CRUD file. """
from sqlalchemy.orm import Session
from uuid import UUID
import bcrypt

from . import models, schemas

def create_user(db: Session, user: schemas.UserCreate):
    """
    Create user and add to Database.
    """
    pw = user.password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pw, salt)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, start_from: int = 0, until: int = 10):
    """
    Get all users information.
    """
    return db.query(models.User).offset(start_from).limit(until).all()

def get_user_by_username(db: Session, username: str):
    """
    Get user by username. Needed for first user registration.
    """
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_id(db: Session, user_id: UUID):
    """
    Get user by UUID. Needed for user information display
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

