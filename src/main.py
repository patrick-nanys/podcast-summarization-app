# FastAPI main file

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")
staticfiles = StaticFiles(directory="static")
app.mount("/static", staticfiles, name="static")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """
    Index route.
    """
    return templates.TemplateResponse("index.html", {"request": request, "title": "BrevioCast"})
