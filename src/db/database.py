""" database file for db handling """
import databases
from authx import Authentication, EncodeDBBackend

from src.utils import conf_helper

config = conf_helper.read_configuration()

auth = Authentication(
    backend=EncodeDBBackend(
        database=databases(
            host=config['dbSettings']['host'],
            port=config['dbSettings']['port'],
            user=config['dbSettings']['pg_username'],
            password=config['dbSettings']['pg_password'],
            database=config['dbSettings']['database'],
        ),
    )
)
