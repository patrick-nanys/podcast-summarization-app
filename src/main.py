from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from utils import conf_helper
from utils.middleware import AWS
from utils.podcast import get_podcast_data_by_name
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
        json_results = get_podcast_data_by_name(name)
    except Exception as e:
        logging.exception(f"caught exception: {e}")
        return HTTPException(
            status_code=500, detail="Server timeout, please try again."
        )
    return templates.TemplateResponse("app.html",
                                        {
                                            "request": request,
                                            "podcast_chunks_start_timestamps_result":json_results["Timestamps"],
                                            "json_content_chunks":json_results["Chunks"],
                                            "podcast_mp3_summary_result":json_results["MP3"],
                                            "podcast_summary_txt_result":json_results["Summary"],
                                            "podcast_transcription_csv_result":json_results["CSV"],
                                        })
