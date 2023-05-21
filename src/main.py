import csv
import json
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from utils import conf_helper
from utils.middleware import AWS
import re
import logging

app = FastAPI()
templates = Jinja2Templates(directory=Path("../frontend"))
app.mount("/static", StaticFiles(directory=Path("../frontend/static")), name="static")
config = conf_helper.read_configuration()

s3_handler = AWS(config["AWS"]["region"], config["AWS"]["aws_access_key_id"], config["AWS"]["aws_secret_access_key"])

# print(s3_handler.list_bucket_content(config["AWS"]["bucket"]))

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

@app.get('/podcast/', response_class=HTMLResponse)
async def podcast(name: str, request: Request):
    """Podcast"""
    try:
        # TODO: separate this name search in an external file as a function
        if name == "naval_how_to_get_rich":
            podcast_name = "How to Get Rich"
            # timestamps json
            podcast_chunks_start_timestamps = s3_handler.fetch_podcast_from_bucket(bucket=config["AWS"]["bucket"], name=name+"/"+podcast_name+"_chunk_start_timestamps.json")
            podcast_chunks_start_timestamps_result = json.loads(podcast_chunks_start_timestamps["Body"].read())
            # json
            podcast_chunks = s3_handler.fetch_podcast_from_bucket(bucket=config["AWS"]["bucket"], name=name+"/"+podcast_name+"_chunks.json")
            json_content_chunks = json.loads(podcast_chunks["Body"].read())
            # mp3
            podcast_mp3_summary = s3_handler.fetch_podcast_from_bucket(bucket=config["AWS"]["bucket"], name=name+"/"+podcast_name+"_read_summary.mp3")
            def iter_mp3_content():
                """Internal function to iterate s3 object content, for mp3 files"""
                for chunk in podcast_mp3_summary["Body"].iter_chunks():
                    yield chunk
            podcast_mp3_summary_result = StreamingResponse(iter_mp3_content(), media_type="audio/mpeg")
            # txt
            podcast_summary_txt = s3_handler.fetch_podcast_from_bucket(bucket=config["AWS"]["bucket"], name=name+"/"+podcast_name+"_summarized_text.json")
            podcast_summary_txt_result = json.loads(podcast_summary_txt["Body"].read())
            # csv
            podcast_transcription_csv = s3_handler.fetch_podcast_from_bucket(bucket=config["AWS"]["bucket"], name=name+"/"+podcast_name+"_transcription.csv")
            def iter_csv_content():
                for chunk in podcast_transcription_csv["Body"].iter_chunks():
                    yield chunk
            podcast_transcription_csv_result = StreamingResponse(iter_csv_content(), media_type="text/csv")

    except Exception as e:
        logging.exception(f"caught exception: {e}")
        return HTTPException(
            status_code=500, detail="Server timeout, please try again."
        )
    return templates.TemplateResponse("app.html",
                                        {
                                            "request": request,
                                            "podcast_chunks_start_timestamps_result":podcast_chunks_start_timestamps_result,
                                            "json_content_chunks":json_content_chunks,
                                            "podcast_mp3_summary_result":podcast_mp3_summary_result,
                                            "podcast_summary_txt_result":podcast_summary_txt_result,
                                            "podcast_transcription_csv_result":podcast_transcription_csv_result
                                        })
