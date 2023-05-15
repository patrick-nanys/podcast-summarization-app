""" database file for db handling (still in dev)"""
import databases
import asyncio
from sqlalchemy import Table, Column, Integer, String, MetaData


metadata = MetaData()

users = Table(
   'users', metadata,
   Column('id', Integer, primary_key = True),
   Column('username', String),
   Column('first_name', String),
   Column('last_name', String),
   Column('password', String),
)

from utils import conf_helper

config = conf_helper.read_configuration()
db_url = f"postgresql://{config['dbSettings']['pg_username']}:{config['dbSettings']['pg_password']}@\
    {config['dbSettings']['host']}:{config['dbSettings']['port']}/{config['dbSettings']['database']}"
database = databases.Database(db_url)
