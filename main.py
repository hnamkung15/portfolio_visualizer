from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from models.base import Base
from db import engine
from routers import account_dashboard, account_setting, dashboard, transactions

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# # SQLite DB 초기화
# Base.metadata.create_all(bind=engine)

# 템플릿 디렉터리 설정
templates = Jinja2Templates(directory="templates")


# 기본 홈
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        "dashboard/dashboard.html",
        {
            "request": request,
            "active": "dashboard",
        },
    )


app.include_router(dashboard.router)
app.include_router(account_setting.router)
app.include_router(account_dashboard.router)
app.include_router(transactions.router)
