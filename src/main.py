""" FastAPI main file """
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from uuid import UUID
from utils.middleware import AWS
from authx import Authentication, EncodeDBBackend, HTTPCache, cache
from pathlib import Path
import logging
import re

import db.database as db
import cache.redis_conf as rd
from db import schemas


app = FastAPI()
auth = Authentication(backend=EncodeDBBackend(database=db.database, users=db.users, email_confirmation=db.email_confirmation))
HTTPCache.init(redis_url=rd.REDIS_URL, namespace='breviocast_cache')
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(db.auth.auth_router, prefix="/api/users")
app.include_router(db.auth.password_router, prefix="/api/users")
app.include_router(db.auth.admin_router, prefix="/api/users")
app.include_router(db.auth.search_router, prefix="/api/users")

# This will be deleted later, just for testing purposes.
# s3_handler = AWS("eu-west-1", config["AWS"]["aws_access_key_id"], config["AWS"]["aws_secret_access_key"])
# file_name = Path("static/mp3/music.mp3")
# s3_handler.upload_to_bucket(file_name, "breviocast-prod")


@app.get("/", response_class=HTMLResponse)
@cache(key="c.home", ttl_in_seconds=180)
async def index(request: Request):
    """
    Index route.
    """
    return templates.TemplateResponse("index.html", {"request": request, "title": "BrevioCast"})

@app.get("/signup/", response_class=HTMLResponse)
def signup(request: Request):
    """
    Signup route. (GET)
    """
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/signup/", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Signup route. (POST)

    TODO:
        + Add password confirmation check
        + Handle same email used twice with different username, unique constraint on sqlite
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return crud.create_user(db=db, user=user)


@app.get("/login/", response_class=HTMLResponse)
def login(request: Request):
    """
    Login route. (GET)
    """
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/users/", response_model=list[schemas.User])
def get_users(start_from: int = 0, until: int = 10, db: Session = Depends(get_db)):
    """
    Display all users information. (GET)

    TODO:
        + Add authorization check
    """
    users_list = crud.get_users(db=db, start_from=start_from, until=until)
    return users_list


@app.get("/user_info/{user_id}", response_model=schemas.User)
def get_user_info(user_id: UUID, db: Session = Depends(get_db)):
    """
    Display user information. (GET)

    TODO:
        + Add authorization check
        + Handle UUID not found -> we get 500 response instead of 404
    """
    user = crud.get_user_by_id(db=db, user_id=user_id)
    if user is None:
        return HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/request/", response_class=HTMLResponse)
@app.post("/request/")
async def request_podcast(request: Request):
    """
    Request Podcast route. (GET/POST)
    """
    if request.method == "GET":
        return templates.TemplateResponse("request.html", {"request": request})
    elif request.method == "POST":
        requested_links = []
        ytb_regex_pattern = (
            r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?.*v=|v\/)|youtu\.be\/)([\w\-]{11})(?:$|[^\w\-])"
        )
        try:
            form_data = await request.form()
            url = form_data["url"]
            match = re.search(ytb_regex_pattern, url)
            if match:
                requested_links.append(url)  # TODO: insert in database instead of list pushing.
                print(requested_links)
                return {"message": f"your link {url} was submitted successfully!"}
            else:
                redirect_url = request.url_for("request_podcast")
                return RedirectResponse(redirect_url, status_code=303)
        except Exception as e:
            logging.exception(f"caught exception: {e}")
            return HTTPException(status_code=500, detail="Server timeout, please try again.")
