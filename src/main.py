from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from authx import Authentication
from authx.services.auth import AuthService
from authx.backend import UsersRepo
from authx.core.jwt import JWTBackend
from authx.routers.auth import get_router


app = FastAPI()
auth = Authentication(
    debug=True,
    base_url="http://localhost:8000/",
    site="http://localhost:8000/",
    database_backend="breviocast",
    callbacks="http://localhost:8000/callback",
    access_cookie_name="access_token",
    refresh_cookie_name="refresh_token",
    private_key="private.pem",
    public_key="public.pem",
    access_expiration=3600,
    refresh_expiration=86400,
    smtp_username=None,
    smtp_host=None,
    smtp_password=None,
    smtp_tls=False,
    display_name="breviocast",
    recaptcha_secret=None,
    social_creds=None,
    social_providers=None
)
AuthService.setup(
        repo = UsersRepo,
        auth_backend = JWTBackend,
        debug = True,
        base_url = 'http://localhost:8000',
        site = 'http://localhost:8000/',
        recaptcha_secret = None,
        smtp_username = None,
        smtp_password = None,
        smtp_host = None,
        smtp_tls = False,
        display_name = 'authx',
    )
templates = Jinja2Templates(directory="frontend")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.include_router(auth.auth_router, prefix="/api/users")


@app.get('/', response_class=HTMLResponse)
async def homepage(request: Request):
    """Index"""
    return templates.TemplateResponse("home.html", {"request": request})

@app.get('/register.html', response_class=HTMLResponse, name="auth:register")
@app.post('/register', response_class=HTMLResponse, name="auth:register")
async def signup(request: Request, response: Response):
    """Sign up"""
    if request.method == "GET":
        return templates.TemplateResponse("register.html", {"request": request})
    # elif request.method == "POST":
    #     try:
    #         #TODO: Create a user and add it to the DB
    #         data = await request.json()
    #         service = AuthService()
    #         tokens = await service.register(data)
    #         AuthService.set_tokens_in_response(response, tokens)
    #     except Exception as e:
    #         print(f"Some exception occured, details: {e}")
    #     return None


@app.get('/signin.html', response_class=HTMLResponse)
@app.post('/login', response_class=HTMLResponse)
async def signin(request: Request):
    """Sign in"""
    if request.method == "GET":
        return templates.TemplateResponse("signin.html", {"request": request})
    # elif request.method == "POST":
    #     try:
    #         #TODO: Create a user and add it to the DB
    #         data = await request.json()
    #         service = AuthService()
    #         tokens = await service.register(data)
    #         AuthService.set_tokens_in_response(response, tokens)
    #     except Exception as e:
    #         print(f"Some exception occured, details: {e}")
    #     return None

@app.post('/logout', name="auth:logout")
async def logout(*, response: Response):
    """Logout"""
    response.delete_cookie(auth.access_cookie_name)
    response.delete_cookie(auth.refresh_cookie_name)
    return None

@app.get('/browse', response_class=HTMLResponse)
async def browse(request: Request):
    """Browse"""
    return templates.TemplateResponse("app.html", {"request": request})

@app.get('/podcast/{id}', response_class=HTMLResponse)
async def podcast(request: Request):
    """Podcast"""
    return templates.TemplateResponse("explore.html", {"request": request})
