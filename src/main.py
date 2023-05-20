from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional
from utils import conf_helper
from utils.middleware import AWS
import re
import logging

app = FastAPI()
templates = Jinja2Templates(directory=Path("../frontend"))
app.mount("/static", StaticFiles(directory=Path("../frontend/static")), name="static")
config = conf_helper.read_configuration()

s3_handler = AWS(config["AWS"]["region"], config["AWS"]["aws_access_key_id"], config["AWS"]["aws_secret_access_key"])

# print(s3_handler.read_from_bucket(config["AWS"]["bucket"]))

@app.exception_handler(404)
def not_found(request: Request, __):
    """Not found redirection"""
    return templates.TemplateResponse("404.html", {"request": request})

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

@app.get('/browse/', response_class=HTMLResponse)
@app.post('/request/')
async def browse(request: Request):
    """Browse"""
    if request.method == "GET":
        return templates.TemplateResponse("app.html", {"request": request})
    elif request.method == "POST":
        requested_links = []
        ytb_regex_pattern = r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?.*v=|v\/)|youtu\.be\/)([\w\-]{11})(?:$|[^\w\-])"
        try:
            form_data = await request.form()
            url = form_data["url"]
            match = re.search(ytb_regex_pattern, url)
            if match:
                requested_links.append(
                    url
                )  # TODO: insert in database instead of list pushing.
                print(requested_links)
                return {"message": f"your link {url} was submitted successfully!"} # TODO: Make an actual FE for this
            else:
                return RedirectResponse(url="/browse/", status_code=303) # TODO: Show an error in the FE
        except Exception as e:
            logging.exception(f"caught exception: {e}")
            return HTTPException(
                status_code=500, detail="Server timeout, please try again."
            )

@app.get('/podcast/{id}', response_class=HTMLResponse)
async def podcast(request: Request):
    """Podcast"""
    return templates.TemplateResponse("explore.html", {"request": request})
