""" FastAPI main file """
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session


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
def signup(user: schemas.User, db: Session = Depends(get_db)):
    """
    Signup route. (POST)
    """
    db_user = crud.get_user(db, id=user.id)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return crud.create_user(db=db, user=user)

@app.get("/login/", response_class=HTMLResponse)
def login(request: Request):
    """
    Login route. (GET)
    """
    return templates.TemplateResponse("login.html", {"request": request})
