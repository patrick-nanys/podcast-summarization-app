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

def get_user(db: Session, username: str):
    """
    Get user by UUID.
    """
    return db.query(models.User).filter(models.User.username == username).first()

