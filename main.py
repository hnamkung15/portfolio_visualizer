from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from models.base import Base
from db import engine
from routers import account_dashboard, account_setting, dashboard, transactions
from i18n_helpers import get_templates_with_i18n

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# # SQLite DB 초기화
# Base.metadata.create_all(bind=engine)

# 템플릿 디렉터리 설정
templates = Jinja2Templates(directory="templates")



# 기본 홈
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    i18n_templates = get_templates_with_i18n(request)
    return i18n_templates.TemplateResponse(
        "dashboard/dashboard.html",
        {
            "request": request,
            "active": "dashboard",
        },
    )


# Language switching route
@app.get("/lang/{language}")
def switch_language(language: str, request: Request):
    """Switch language and redirect back to the current page."""
    from i18n import SUPPORTED_LANGUAGES
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    
    if language not in SUPPORTED_LANGUAGES:
        language = "ko"  # Default to Korean
    
    # Get the referer URL or default to dashboard
    referer = request.headers.get("referer", "/")
    
    # Parse the URL to properly handle existing parameters
    parsed_url = urlparse(referer)
    query_params = parse_qs(parsed_url.query)
    
    # Replace or add the lang parameter
    query_params['lang'] = [language]
    
    # Rebuild the URL with the updated parameters
    new_query = urlencode(query_params, doseq=True)
    redirect_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query,
        parsed_url.fragment
    ))
    
    return RedirectResponse(url=redirect_url)


app.include_router(dashboard.router)
app.include_router(account_setting.router)
app.include_router(account_dashboard.router)
app.include_router(transactions.router)
