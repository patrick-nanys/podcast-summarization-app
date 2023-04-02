# FastAPI main file

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
    """
    Index route.
    """
    return {"alive":"True"}
