from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from db import model, operation, schema
from db.database import SessionLocal, engine
from utils import conf_helper
from utils.middleware import AWS
from utils.podcast import get_basic_podcast_data_by_name
import re
import logging
import uuid
import time

app = FastAPI()
templates = Jinja2Templates(directory=Path("../frontend"))
app.mount("/static", StaticFiles(directory=Path("../frontend/static")), name="static")
model.Base.metadata.create_all(bind=engine)
config = conf_helper.read_configuration()

s3_handler = AWS(config["AWS"]["region"], config["AWS"]["aws_access_key_id"], config["AWS"]["aws_secret_access_key"])

# some past time as initial time
REFRESH_TIME = 1642886542
PODCAST_NAMES = None

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.exception_handler(404)
def not_found(request: Request, __):
    """Not found redirection"""
    return templates.TemplateResponse("404.html", {"request": request})

@app.get('/', response_class=HTMLResponse)
async def homepage(request: Request):
    """Index"""
    return templates.TemplateResponse("home.html", {"request": request})

@app.get('/register')
async def signup():
    """Sign up"""
    return {"message":"Account handling in construction, please comeback later"} # TODO: Make an actual FE for this

@app.get('/signin')
async def signin():
    """Sign in"""
    return {"message":"Account handling in construction, please comeback later"} # TODO: Make an actual FE for this

def get_podcast_names():
    global PODCAST_NAMES
    now_time = time.time()
    one_hour = 3600
    if PODCAST_NAMES is None or now_time - REFRESH_TIME >= one_hour:
        PODCAST_NAMES = s3_handler.list_podcast_names(config["AWS"]["bucket"], 'podcasts')

    return PODCAST_NAMES

@app.get('/browse', response_class=HTMLResponse)
async def browse(request: Request):
    """Browse"""
    podcast_names = get_podcast_names()
    podcast_names_items = list(podcast_names.items())
    sliced_podcast_names = [podcast_names_items[i::3] for i in range(3)]

    return templates.TemplateResponse("app.html", {"request": request, "sliced_podcast_names": sliced_podcast_names})

        
@app.post('/request/')
async def request(request: Request, url: str = Form(...), db: Session = Depends(get_db)):
    ytb_regex_pattern = r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?.*v=|v\/)|youtu\.be\/)([\w\-]{11})(?:$|[^\w\-])"
    try:
        match = re.search(ytb_regex_pattern, url)
        if match:
            next_id = db.query(func.max(model.Podcast.id)).scalar() or 0
            db_podcast = model.Podcast(id=next_id + 1, link=url)
            db.add(db_podcast)
            db.commit()
            db.refresh(db_podcast)
            return {"message": f"your link {url} was submitted successfully!"} # TODO: Make an actual FE for this
        else:
            raise HTTPException(status_code=403, detail="You tried a url that is not supported!")
    except Exception as e:
        logging.exception(f"caught exception: {e}")
        raise HTTPException(
            status_code=500, detail="Server timeout, please try again."
        )
    
@app.post('/simple_request')
async def simple_request(requested_url: str = Form(...)):
    ytb_regex_pattern = r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?.*v=|v\/)|youtu\.be\/)([\w\-]{11})(?:$|[^\w\-])"
    try:
        match = re.search(ytb_regex_pattern, requested_url)
        if match:
            request_id = id = uuid.uuid4()
            s3_handler.upload_string_as_file_to_s3(config["AWS"]["bucket"], f'requests/{request_id}.txt', requested_url)
            return {"message": f"Your link was submitted successfully!"} # TODO: Make an actual FE for this
    except Exception as e:
        logging.exception(f"caught exception: {e}")
        raise HTTPException(status_code=500, detail="Server timeout, please try again.")
    
    raise HTTPException(status_code=403, detail="You tried a url that is not supported!")

@app.get("/audio/{name}")
async def main(name: str):
    try:
        audio_file_obj = s3_handler.fetch_podcast_from_bucket(bucket=config["AWS"]["bucket"], name=name+"/read_summary.mp3")
        return StreamingResponse(audio_file_obj['Body'], media_type="audio/mpeg")
    except Exception as e:
        return str(e)
    
@app.get('/podcast', response_class=HTMLResponse)
async def podcast(name: str, request: Request):
    """Podcast"""
    try:
        json_results = get_basic_podcast_data_by_name(name)
        response = {
                        "request": request,
                        "name_id": name,
                        "podcast_name": json_results["Name"],
                        "chunks": list(zip(json_results["Chunks"], json_results["ChunkStartTimes"]))
                    }
    except Exception as e:
        logging.exception(f"caught exception: {e}")
        return HTTPException(
            status_code=500, detail="Server timeout, please try again."
        )
    return templates.TemplateResponse("podcast.html", response)
