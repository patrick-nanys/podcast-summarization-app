""" database file for db handling (still in dev)"""
import databases
import asyncio
import sqlalchemy
from authx import Authentication, EncodeDBBackend

from utils import conf_helper

config = conf_helper.read_configuration()
db_url = f"postgresql://{config['dbSettings']['pg_username']}:{config['dbSettings']['pg_password']}@\
    {config['dbSettings']['host']}:{config['dbSettings']['port']}/{config['dbSettings']['database']}"
database = databases.Database(db_url)

auth = Authentication(backend=EncodeDBBackend(database=database))
