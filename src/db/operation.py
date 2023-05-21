"""Database operation file for Podcast storing"""

from sqlalchemy.orm import Session
from . import model, schema

def push_podcast_to_db(db: Session, podcast: schema.AddPodcast):
    """Add requested link to the database"""
    db_podcast = model.Podcast(id=podcast.id, link=podcast.link)
    db.add(db_podcast)
    db.commit()
    db.refresh(db_podcast)
    return db_podcast
