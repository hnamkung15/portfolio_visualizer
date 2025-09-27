from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db import get_db
from services.auth_service import AuthService
from models.user import User
from utils.auth import verify_token

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Get current user from session/token."""
    # Check for token in cookies
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    username = verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Display login page."""
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle login form submission."""
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(username, password)
    
    if not user:
        return templates.TemplateResponse(
            "auth/login.html", 
            {"request": request, "error": "Invalid username or password"}
        )
    
    # Create access token
    access_token = auth_service.create_access_token_for_user(user)
    
    # Redirect to dashboard with token in cookie
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800  # 30 minutes
    )
    return response


@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    """Display signup page."""
    return templates.TemplateResponse("auth/signup.html", {"request": request})


@router.post("/signup")
def signup(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle signup form submission."""
    if password != confirm_password:
        return templates.TemplateResponse(
            "auth/signup.html",
            {"request": request, "error": "Passwords do not match"}
        )
    
    auth_service = AuthService(db)
    try:
        user = auth_service.create_user(username, password)
        # Create access token
        access_token = auth_service.create_access_token_for_user(user)
        
        # Redirect to dashboard with token in cookie
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=1800  # 30 minutes
        )
        return response
    except HTTPException as e:
        return templates.TemplateResponse(
            "auth/signup.html",
            {"request": request, "error": e.detail}
        )


@router.post("/logout")
def logout():
    """Handle logout."""
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response
