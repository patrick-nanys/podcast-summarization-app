""" Users CRUD file. """
from sqlalchemy.orm import Session
from uuid import UUID
import bcrypt

from . import models, schemas

def create_user(db: Session, user: schemas.User):
    """
    Create user and add to Database.
    """
    pw = user.password.encode('utf-8')
    salt = bcrypt.gensalt()
    encrypted_password = bcrypt.hashpw(pw, salt)
    db_user = models.User(username=user.username, email=user.email, encrypted_password=encrypted_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: UUID):
    """
    Get user by UUID.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

