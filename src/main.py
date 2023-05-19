from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path


app = FastAPI()
templates = Jinja2Templates(directory=Path("../frontend"))
app.mount("/static", StaticFiles(directory=Path("../frontend/static")), name="static")


@app.get('/', response_class=HTMLResponse)
async def homepage(request: Request):
    """Index"""
    return templates.TemplateResponse("home.html", {"request": request})

@app.get('/register.html', response_class=HTMLResponse)
async def signup(request: Request):
    """Sign up"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.get('/signin.html', response_class=HTMLResponse)
async def signin(request: Request):
    """Sign in"""
    return templates.TemplateResponse("signin.html", {"request": request})

@app.get('/browse', response_class=HTMLResponse)
async def browse(request: Request):
    """Browse"""
    return templates.TemplateResponse("app.html", {"request": request})

@app.get('/podcast/{id}', response_class=HTMLResponse)
async def podcast(request: Request):
    """Podcast"""
    return templates.TemplateResponse("explore.html", {"request": request})
