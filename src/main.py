""" FastAPI main file """
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from uuid import UUID

from db.database import SessionLocal, engine
from db import schemas, crud, models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
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
