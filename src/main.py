# FastAPI main file

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr

app = FastAPI()
templates = Jinja2Templates(directory="templates")
staticfiles = StaticFiles(directory="static")
app.mount("/static", staticfiles, name="static")

class User(BaseModel):
    id: UUID
    username: str = Field(min_length=4)
    email: EmailStr
    password: str

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """
    Index route.
    """
    return templates.TemplateResponse("index.html", {"request": request, "title": "BrevioCast"})

@app.get("/signup", response_class=HTMLResponse)
def signup(request: Request):
    """
    Signup route. (GET)
    """
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    """
    Login route. (GET)
    """
    return templates.TemplateResponse("login.html", {"request": request})
