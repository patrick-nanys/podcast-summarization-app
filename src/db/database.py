""" database file for db handling """
import databases
from authx import Authentication, EncodeDBBackend

auth = Authentication(
    backend=EncodeDBBackend(
        database=databases(
            host="localhost",
            port=5432,
            user="x",
            password="x",
            database="breviocast",
        ),
    )
)
