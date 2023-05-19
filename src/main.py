from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from utils import conf_helper
from utils.middleware import AWS

app = FastAPI()
templates = Jinja2Templates(directory=Path("../frontend"))
app.mount("/static", StaticFiles(directory=Path("../frontend/static")), name="static")
config = conf_helper.read_configuration()

s3_handler = AWS(config["AWS"]["region"], config["AWS"]["aws_access_key_id"], config["AWS"]["aws_secret_access_key"])

@app.get('/', response_class=HTMLResponse)
async def homepage(request: Request):
    """Index"""
    return templates.TemplateResponse("home.html", {"request": request})

@app.get('/register.html')
async def signup():
    """Sign up"""
    return {"message":"Account handling in construction, please comeback later"} # TODO: Make an actual FE for this

@app.get('/signin.html')
async def signin():
    """Sign in"""
    return {"message":"Account handling in construction, please comeback later"} # TODO: Make an actual FE for this

@app.exception_handler(404)
def not_found(request: Request, __):
    """Not found redirection"""
    return templates.TemplateResponse("404.html", {"request": request})

@app.get('/browse', response_class=HTMLResponse)
async def browse(request: Request):
    """Browse"""
    return templates.TemplateResponse("app.html", {"request": request})

@app.get('/podcast/{id}', response_class=HTMLResponse)
async def podcast(request: Request):
    """Podcast"""
    return templates.TemplateResponse("explore.html", {"request": request})
